from flask import Flask,jsonify,request
import os
from data_loader import Dataloader
from data_cleaner import DataCleaner
from kpi_calculator import KPICalculator



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
        "Sucess":"file is uploaded successfully",
        "filename":file.filename
    }),200

#defining the analyze route
app.route("/analyze" , methods= ["POST"])
def analyze_business():
    #Get the file name from the request
    data = request.get_json()
    filename = data.get("filename")

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

        #Step 4 : Return the results after the anaylze
        return jsonify({
            'message': 'Analysis Complete!',
            'kpis' : kpis
        }),200
    except Exception as e:
        return jsonify({
            'error' : str(e)
        }),500


#runing the app
if __name__ == "__main__":
    app.run(debug=True)
