from flask import Flask,jsonify,request
import os
from data_loader import Dataloader
from data_cleaner import DataCleaner
from kpi_calculator import KPICalculator
from llm_agent import LLMAgent
import json
from database import BusinessDatabase



app = Flask(__name__) #initialize the flask app

#Set the upload folder
UPLOAD_FOLDER = "../data/upload"    #path
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER  #configure the upload folder 

#HOME ROUTE for test 
@app.route("/")  #Decorator, when request comes than run this function
def home():
    return jsonify({
        "message":"Business Analyzer API",
        "status": "success"
        }
)

#defining the upload route
@app.route("/upload" , methods= ["POST"])
def upload_file():
    #set the logic in the upload route
    #When file is not send
    if "file" not in request.files:
        return jsonify({"error":"file not found"}),400
    #store the file object 
    file = request.files["file"]
    #when file is not selected
    if file.filename == '':
        return jsonify({'error': "File is not selected"}),400
    #save file 
    file_path = os.path.join(app.config["UPLOAD_FOLDER"],file.filename)  #join both the paths and send the file in the upload folder
    file.save(file_path)  #save the file 
    #return success message
    return jsonify({
        "sucess":"File uploaded successfully",
        "filename":file.filename
    }),200

#defining the analyze route
@app.route("/analyze" , methods= ["POST"])
def analyze_business():
    #Get the file name from the request
    data = request.get_json()
    filename = data.get("filename")
    business_name = data.get('business_name') #comes from the frontend
    industry = data.get('industry')
    business_type = data.get('business_type')
    
    #check the file name is provided or not 
    if not filename:
        return jsonify({
            'error': 'Filename is required'
        }),400
    #Full path of the  file 
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    # Checking the file exists or not
    if not os.path.exists(filepath):
        return jsonify({
            'error': 'file not found'
        }) ,404   
    try:
        #Step 1 : loading the csv file given by the user 
        loader = Dataloader(filepath)   #file is loaded
        if loader.load_csv() is None or loader.load_csv().empty:
            return jsonify({
                'error' : 'Failed to load data'
            }),500
        if not loader.load_csv():
            return jsonify({
                'error': 'file not loaded'
            }),500  
        #Step 2 : Clean CSV file Data
        df = loader.get_dataframe()
        cleaner = DataCleaner(df)
        cleaner_df = cleaner.clean_all()  #now the file is cleaned
        #Step 3 : Performing the KPI calculations on the data
        calculator = KPICalculator(cleaner_df)
        kpis = calculator.get_all_kpis()
        print("KPIS generated:",list(kpis.keys()))
        #Step 4 : Save the data in the database
        db  = BusinessDatabase()
        db.connect()
        db.create_tables()
        #insert business
        business_id = db.insert_business(business_name,industry,business_type)
        #insert analysis
        analysis_id = db.insert_analysis(business_id,kpis)
        db.close()   #database save
        #Step 5 : Return the results after the anaylze
        return jsonify({
            'message': 'Analysis Complete!',
            'business_id': business_id,
            'analysis' : analysis_id,
            'kpis' : kpis
        }),200
    except Exception as e:
        return jsonify({
            'error' : str(e)
        }),500

#define the llm route that take the suggestion from the llm 
@app.route("/recommendations" , methods = ["POST"])
def get_recommendations():
    #get the kpis file data 
    data = request.get_json()
    kpis = data.get('kpis')
    #when kpis file not found
    if not kpis:
        return jsonify({
            'error': 'Kpis Required'
        }),400
    #main logic of the recommendations
    try:
        #Create the llm agent
        agent = LLMAgent()
        #Generating the recommendation for llm 
        recommendations = agent.generate_recommendations(kpis)
        #parse the json file by using the json.loads() for easy use in frontend 
        try:
            rec_json = json.loads(recommendations)
        except:
            rec_json = {"raw txt" : recommendations}
        return jsonify({
            'message': 'Recommendations genrated successfully',
            'recommendations' : recommendations
        }),200
    except Exception as e:
        return jsonify({
            'error' : str(e)
        }),500

#route for fetching the past analyses
@app.route('/history/<int:business_id>', methods = ['GET'])
def get_history(business_id):
    try:
        db = BusinessDatabase()
        db.connect()
        #business details
        business = db.get_business_by_id(business_id)
        analyses = db.get_all_analyses(business_id)
        db.close()
        return jsonify({
            'busienss' : business,
            'analyses': analyses
        }) ,200
    except Exception as e:
        return jsonify({'error':str(e)}),500

#runing the app
if __name__ == "__main__":
    app.run(debug=True)
