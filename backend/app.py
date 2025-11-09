from flask import Flask, jsonify, request
import os
from data_loader import Dataloader
from data_cleaner import DataCleaner
from kpi_calculator import KPICalculator
from llm_agent import LLMAgent
import json
from database import BusinessDatabase

# HIMANSHU'S ML MODULES (NEW IMPORTS)
from feature_engineer import FeatureEngineer
from ml_predictor import MLPredictor
from visualizations import ChartGenerator

app = Flask(__name__)  # initialize the flask app

# Set the upload folder
UPLOAD_FOLDER = "../data/upload"  # path
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER  # configure the upload folder

#Set the upload folder
app.config['UPLOAD_FOLDER'] = '../data/upload'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
#HOME ROUTE for test 
@app.route("/")  #Decorator, when request comes than run this function
def home():
    return jsonify({
        "message": "Business Analyzer API",
        "status": "success"
    })

# defining the upload route
@app.route("/upload", methods=["POST"])
def upload_file():
    # set the logic in the upload route
    # When file is not send
    if "file" not in request.files:
        return jsonify({"error": "file not found"}), 400
    # store the file object
    file = request.files["file"]
    # when file is not selected
    if file.filename == '':
        return jsonify({'error': "File is not selected"}),400
    #save file 
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file_path = file_path.replace('\\', '/')  # Fix path separators
    file.save(file_path)
    #return success message
    return jsonify({
        "success": "File uploaded successfully",
        "filename": file.filename
    }), 200

# defining the analyze route
@app.route("/analyze", methods=["POST"])
def analyze_business():
    # Get the file name from the request
    data = request.get_json()
    filename = data.get("filename")
    # check the file name is provided or not
    if not filename:
        return jsonify({
            'error': 'Filename is required'
        }), 400
    # Full path of the file
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    # Checking the file exists or not
    if not os.path.exists(filepath):
        return jsonify({
            'error': 'file not found'
        }), 404
    try:
        #Step 1 : loading the csv file given by the user 
        loader = Dataloader(filepath)   #file is loaded
        if not loader.load_csv() :
            return jsonify({
                'error' : 'Failed to load data'
            }),500
        
        #Step 2 : Clean CSV file Data
        df = loader.get_dataframe()
        cleaner = DataCleaner(df)
        cleaned_df = cleaner.clean_all()  # now the file is cleaned
        # Step 3: Performing the KPI calculations on the data
        calculator = KPICalculator(cleaned_df)
        kpis = calculator.get_all_kpis()
        # Step 4: Return the results after the analyze
        return jsonify({
            'message': 'Analysis Complete!',
            'kpis': kpis
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

# define the llm route that take the suggestion from the llm
@app.route("/recommendations", methods=["POST"])
def get_recommendations():
    # get the kpis file data
    data = request.get_json()
    kpis = data.get('kpis')
    # when kpis file not found
    if not kpis:
        return jsonify({
            'error': 'Kpis Required'
        }), 400
    # main logic of the recommendations
    try:
        # Create the llm agent
        agent = LLMAgent()
        # Generating the recommendation for llm
        recommendations = agent.generate_recommendations(kpis)
        # parse the json file by using the json.loads() for easy use in frontend

        return jsonify({
            'message': 'Recommendations generated successfully',
            'recommendations': recommendations
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


# ========== HIMANSHU'S NEW ENDPOINTS (ML & PREDICTIONS) ==========

@app.route("/predict", methods=["POST"])
def predict_sales():
    """
    ML-based sales prediction endpoint
    
    Request JSON:
    {
        "filename": "uploaded_file.csv"
    }
    
    Response:
    {
        "success": true,
        "model_name": "Linear Regression",
        "model_accuracy": 1.0,
        "future_predictions": [70000, 72000, 75000, ...],
        "insights": {...}
    }
    """
    data = request.get_json()
    filename = data.get("filename")
    
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400
    
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Step 1: Load and Clean Data (Using Dhruv's modules)
        loader = Dataloader(filepath)
        if not loader.load_csv():
            return jsonify({'error': 'Failed to load file'}), 500
        
        df = loader.get_dataframe()
        cleaner = DataCleaner(df)
        cleaned_df = cleaner.clean_all()
        
        # Step 2: Feature Engineering (Himanshu's module)
        engineer = FeatureEngineer(cleaned_df)
        engineer.create_time_features()
        engineer.create_lag_features(column='Revenue', lags=[1, 2, 3])
        engineer.create_rolling_features(column='Revenue', windows=[3, 5])
        engineer.create_growth_rate(column='Revenue')
        engineer.drop_missing_rows()
        
        X, y = engineer.prepare_ml_data(target_column='Revenue')
        
        # Step 3: Train ML Model (Himanshu's module)
        predictor = MLPredictor()
        metrics = predictor.train_models(X, y, test_size=0.2)
        predictor.save_model('models/sales_predictor.pkl')
        
        # Step 4: Generate Future Predictions
        last_features = X.iloc[-1].values
        predictions = predictor.predict_next_periods(last_features, num_periods=6)
        
        # Step 5: Calculate Insights
        current_avg = float(cleaned_df['Revenue'].tail(6).mean())
        predicted_avg = float(sum(predictions) / len(predictions))
        growth_rate = ((predicted_avg - current_avg) / current_avg) * 100
        
        # Step 6: Return Response
        model_key = predictor.best_model_name.lower().replace(' ', '_')
        
        return jsonify({
            'success': True,
            'message': 'Predictions generated successfully',
            'model_name': predictor.best_model_name,
            'model_accuracy': metrics[model_key]['R2'],
            'future_predictions': predictions,
            'insights': {
                'current_avg_revenue': current_avg,
                'predicted_avg_revenue': predicted_avg,
                'expected_growth_rate': round(growth_rate, 2)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/charts", methods=["POST"])
def generate_charts():
    """
    Generate business analytics charts
    
    Request JSON:
    {
        "filename": "uploaded_file.csv",
        "chart_types": ["revenue_trend", "product_comparison", "expense_breakdown", "forecast"]
    }
    
    Response:
    {
        "success": true,
        "charts": {
            "revenue_trend": "base64_encoded_image...",
            "product_comparison": "base64_encoded_image...",
            ...
        }
    }
    """
    data = request.get_json()
    filename = data.get("filename")
    chart_types = data.get("chart_types", ["revenue_trend"])
    
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400
    
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Step 1: Load and Clean Data
        loader = Dataloader(filepath)
        if not loader.load_csv():
            return jsonify({'error': 'Failed to load file'}), 500
        
        df = loader.get_dataframe()
        cleaner = DataCleaner(df)
        cleaned_df = cleaner.clean_all()
        
        # Step 2: Initialize Chart Generator
        generator = ChartGenerator()
        charts = {}
        
        # Step 3: Generate Requested Charts
        if 'revenue_trend' in chart_types:
            charts['revenue_trend'] = generator.revenue_trend_chart(
                cleaned_df, 
                date_col='Date', 
                revenue_col='Revenue'
            )
        
        if 'product_comparison' in chart_types:
            # Aggregate revenue by product
            product_revenue = cleaned_df.groupby('Product_Name')['Revenue'].sum().to_dict()
            top_products = dict(sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:10])
            product_data = {k: {'revenue': v} for k, v in top_products.items()}
            charts['product_comparison'] = generator.product_comparison_chart(product_data)
        
        if 'expense_breakdown' in chart_types:
            expense_data = {
                'COGS': cleaned_df['Costs_Of_Goods'].sum(),
                'Marketing': cleaned_df['Marketing_Cost'].sum(),
                'Logistics': cleaned_df['Logistic_Cost'].sum(),
                'Operating': cleaned_df['Operating_Expenses'].sum(),
                'Other': cleaned_df['Other_Cost'].sum()
            }
            charts['expense_breakdown'] = generator.expense_breakdown_chart(expense_data)
        
        if 'forecast' in chart_types:
            # Get historical data
            historical_revenue = cleaned_df['Revenue'].tail(20).tolist()
            
            # Get predictions (if available)
            try:
                # Quick feature engineering for predictions
                engineer = FeatureEngineer(cleaned_df)
                engineer.create_time_features()
                engineer.create_lag_features(column='Revenue', lags=[1, 2])
                engineer.create_rolling_features(column='Revenue', windows=[3])
                engineer.drop_missing_rows()
                
                X, y = engineer.prepare_ml_data(target_column='Revenue')
                
                # Load or train model
                predictor = MLPredictor()
                try:
                    predictor.load_model('models/sales_predictor.pkl')
                except:
                    predictor.train_models(X, y, test_size=0.2)
                
                last_features = X.iloc[-1].values
                predictions = predictor.predict_next_periods(last_features, num_periods=6)
                
                charts['forecast'] = generator.forecast_chart(historical_revenue, predictions)
            except:
                # If prediction fails, show only historical
                charts['forecast'] = generator.forecast_chart(historical_revenue, [])
        
        # Step 4: Return Charts
        return jsonify({
            'success': True,
            'message': 'Charts generated successfully',
            'charts': charts
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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

# running the app
if __name__ == "__main__":
    app.run(debug=True)