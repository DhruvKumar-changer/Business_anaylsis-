import os
import json
from data_loader import Dataloader
from data_cleaner import DataCleaner
from kpi_calculator import KPICalculator
from llm_agent import LLMAgent
from database import BusinessDatabase
import numpy as np

# Set up environment (ensure .env has GROQ_API_KEY and DB credentials)
os.environ['GROQ_API_KEY'] ='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'  # Replace with actual key
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_USER'] = 'root'
os.environ['DB_PASSWORD'] = 'dhruv'  # Use secure password
os.environ['DB_NAME'] = 'business_analyzer_db'

def test_backend():
    # Step 1: Load data (pass filepath to Dataloader init; use forward slashes for paths)
    loader = Dataloader('../data/upload/sample_business_data.csv') # Adjust path if needed (e.g., 'upload/sample_business_data.csv')
    loader.load_csv()  # No argument needed here
    df = loader.get_dataframe()
    
    # Check if DataFrame loaded successfully
    if df is None:
        print("Error: DataFrame could not be loaded. Check the file path and ensure the CSV exists.")
        return {"status": "error", "message": "File not found or could not be loaded."}
    
    # Step 2: Clean data
    cleaner = DataCleaner(df)
    cleaner.clean_all()
    cleaned_df = cleaner.get_dataframe()
    
    # Step 3: Calculate KPIs
    calculator = KPICalculator(cleaned_df)
    kpis = calculator.get_all_kpis()
    
    # Step 4: Generate recommendations
    agent = LLMAgent()
    recommendations = agent.generate_recommendations(kpis)
    
    # Step 5: Save to database
    db = BusinessDatabase()
    db.connect()  
    db.create_tables() 
    
    db.insert_business('Test Business', 'Technology', 'Startup')

    business_id = db.get_latest_business_id()
    db.insert_analysis(business_id, kpis)
    # db.insert_prediction(business_id, recommendations)
    
    # Step 6: Output results in JSON format for frontend
    result = {
        "business_id": business_id,
        "kpis": kpis,
        "recommendations": recommendations,
        "status": "success"
    }
    # Step 7: Test ML Predictions
    print("\n📈 Testing ML Predictions...")
    from feature_engineer import FeatureEngineer
    from ml_predictor import MLPredictor

    engineer = FeatureEngineer(cleaned_df)
    engineer.create_time_features()
    engineer.create_lag_features(column='Revenue', lags=[1, 2, 3])
    engineer.create_rolling_features(column='Revenue', windows=[3, 5])
    engineer.create_growth_rate(column='Revenue')
    engineer.drop_missing_rows()

    X, y = engineer.prepare_ml_data(target_column='Revenue')

    predictor = MLPredictor()
    metrics = predictor.train_models(X, y, test_size=0.2)
    predictor.save_model('../models/sales_predictor.pkl')

    last_features = X.iloc[-1].values
    predictions = predictor.predict_next_periods(last_features, num_periods=6)

    result['ml_predictions'] = {
        'model': predictor.best_model_name,
        'accuracy': metrics[predictor.best_model_name.lower().replace(' ', '_')]['R2'],
        'future_6_months': predictions
    }

    # Step 8: Test Chart Generation
    print("\n📊 Testing Charts...")
    from visualizations import ChartGenerator

    generator = ChartGenerator()
    revenue_chart = generator.revenue_trend_chart(cleaned_df, 'Date', 'Revenue')

    result['charts_generated'] = True
    result['chart_sample_length'] = len(revenue_chart) if revenue_chart else 0

    
    def convert_np(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj

    result = json.loads(json.dumps(result, default=convert_np))
    print(json.dumps(result, indent=4))
    
    return result

if __name__ == "__main__":
    test_backend()