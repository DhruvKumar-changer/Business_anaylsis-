from flask import Flask, jsonify, request,send_file
import os
from data_loader import Dataloader
from data_cleaner import DataCleaner
from kpi_calculator import KPICalculator
from llm_agent import LLMAgent
import json
import numpy as np 
from database import BusinessDatabase
from entry_questions import BusinessQuestions
from flask_cors import CORS
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak ,Table,TableStyle
from reportlab.lib import colors
from datetime import datetime
from flask import send_file
# HIMANSHU'S ML MODULES (NEW IMPORTS)
from feature_engineer import FeatureEngineer
from ml_predictor import MLPredictor
from visualizations import ChartGenerator

app = Flask(__name__)  # initialize the flask app
CORS(app)  # Enable CORS for frontend-backend communication

# Set the upload folder
UPLOAD_FOLDER = "../data/upload"  # path
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER  # configure the upload folder
REPORTS_FOLDER = "../reports"
app.config["REPORTS_FOLDER"] = REPORTS_FOLDER


#Set the upload folder
app.config['UPLOAD_FOLDER'] = '../data/upload'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists(app.config["REPORTS_FOLDER"]):
    os.makedirs(app.config["REPORTS_FOLDER"],exist_ok=True)
print(f"📁 Upload Folder: {os.path.abspath(UPLOAD_FOLDER)}")
print(f"📁 Reports Folder: {os.path.abspath(REPORTS_FOLDER)}")

#HOME ROUTE for test 
@app.route("/")  #Decorator, when request comes than run this function
def home():
    return jsonify({
        "message": "Business Analyzer API",
        "status": "success"
    })


# Add this route after existing routes
@app.route("/questions", methods=["GET"])
def get_entry_questions():
    """Get entry-level onboarding questions"""
    try:
        questions = BusinessQuestions.get_questions()
        return jsonify({
            'success': True,
            'questions': questions
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/submit-profile", methods=["POST"])
def submit_business_profile():
    """Submit business profile after questions"""
    try:
        data = request.get_json()
        answers = data.get('answers')
        
        # Validate answers
        is_valid, error = BusinessQuestions.validate_answers(answers)
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Create profile
        profile = BusinessQuestions.create_business_profile(answers)
        
        # Save to database
        db = BusinessDatabase()
        db.connect()
        business_id = db.insert_business(
            profile['business_name'],
            profile['industry'],
            profile['business_type']
        )
        db.close()
        
        return jsonify({
            'success': True,
            'message': 'Profile created successfully',
            'business_id': business_id,
            'profile': profile
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

def convert_numpy_types(obj):
    """Convert numpy types to Python native types"""
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(i) for i in obj]
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    return obj
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
        print("🔹 Step 1: Loading file...")
        loader = Dataloader(filepath)   #file is loaded
        if not loader.load_csv() :
            return jsonify({
                'error' : 'Failed to load data'
            }),500
        
        #Step 2 : Clean CSV file Data
        print("🔹 Step 2: Cleaning data...")
        df = loader.get_dataframe()
        cleaner = DataCleaner(df)
        cleaned_df = cleaner.clean_all()  # now the file is cleaned
        print(f"✅ Cleaned! Rows: {len(cleaned_df)}")

        # Step 3: Performing the KPI calculations on the data
        print("🔹 Step 3: Calculating KPIs...")
        calculator = KPICalculator(cleaned_df)
        kpis = calculator.get_all_kpis()
        kpis = convert_numpy_types(kpis) 
        print("✅ KPIs calculated!")

        # Step 4: Return the results after the analyze
        return jsonify({
        'message': 'Analysis Complete!',
        'kpis': kpis
        }), 200
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")  
        import traceback
        traceback.print_exc() #(Shows full error)
        return jsonify({
            'error': str(e)
        }), 500

# define the llm route that take the suggestion from the llm
@app.route("/recommendations", methods=["POST"])
def get_recommendations():
    data = request.get_json()
    kpis = data.get('kpis')
    business_profile = data.get('profile')
    
    print("=" * 60)
    print("🤖 RECOMMENDATIONS REQUEST")
    print("Has KPIs:", bool(kpis))
    print("Has Profile:", bool(business_profile))
    print("=" * 60)
    
    if not kpis:
        return jsonify({'error': 'Kpis Required'}), 400
    
    try:
        print("🔹 Creating LLM Agent...")
        agent = LLMAgent()
        print("✅ Agent created")
        
        print("🔹 Calling generate_recommendations...")
        recommendations = agent.generate_recommendations(kpis, business_profile)
        print("✅ Recommendations generated successfully")
        print(f"Response length: {len(recommendations)} chars")
        
        return jsonify({
            'message': 'Recommendations generated successfully',
            'recommendations': recommendations
        }), 200
        
    except AttributeError as e:
        print(f"❌ ATTRIBUTE ERROR: {str(e)}")
        print("This means the function name is wrong!")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Function error: {str(e)}'}), 500
        
    except Exception as e:
        print(f"❌ GENERAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

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
        #Convert to normal Python list
        predictions = [float(p) for p in predictions]

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
        print("📊 Generating charts...")
        # Step 1: Load and Clean Data
        loader = Dataloader(filepath)
        if not loader.load_csv():
            return jsonify({'error': 'Failed to load file'}), 500
        
        df = loader.get_dataframe()
        cleaner = DataCleaner(df)
        cleaned_df = cleaner.clean_all()
        print(f"✅ Data cleaned: {len(cleaned_df)} rows") 

        # Step 2: Initialize Chart Generator
        generator = ChartGenerator()
        charts = {}
        
        # Step 3: Generate Requested Charts
        if 'revenue_trend' in chart_types:
            try:
                print("🔹 Generating revenue trend...")
                charts['revenue_trend'] = generator.revenue_trend_chart(
                    cleaned_df, 
                    date_col='Date', 
                    revenue_col='Revenue'
            )
                print("✅ Revenue trend done")  # ADD THIS
            except Exception as e:
                print(f"❌ Revenue trend failed: {e}") 
        
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
        print(f"❌ Charts error: {str(e)}") 
        import traceback
        traceback.print_exc() 
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
    
# GENERATE PDF REPORT

@app.route("/generate-pdf", methods=["POST", "OPTIONS"])
def generate_pdf():
    """Generate PDF report"""
    # Handle OPTIONS preflight
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        print("\n" + "="*60)
        print("📄 PDF GENERATION REQUEST RECEIVED")
        print("="*60)
        
        data = request.get_json()
        print(f"✅ Request data received: {list(data.keys())}")
        
        kpis = data.get('kpis')
        profile = data.get('profile', {})
        recommendations = data.get('recommendations')
        
        print(f"   - KPIs: {bool(kpis)} ({len(kpis) if kpis else 0} items)")
        print(f"   - Profile: {bool(profile)}")
        print(f"   - Recommendations: {bool(recommendations)} ({len(str(recommendations)) if recommendations else 0} chars)")
        
        if not kpis:
            print("❌ KPIs missing!")
            return jsonify({'error': 'KPIs required'}), 400
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"business_report_{timestamp}.pdf"
        filepath = os.path.join(app.config["REPORTS_FOLDER"], filename)
        
        print(f"\n📁 PDF Output:")
        print(f"   - Filename: {filename}")
        print(f"   - Full path: {filepath}")
        print(f"   - Folder exists: {os.path.exists(REPORTS_FOLDER)}")
        
        # Create PDF document
        print("\n🔨 Building PDF document...")
        doc = SimpleDocTemplate(
            filepath, 
            pagesize=A4, 
            topMargin=0.5*inch, 
            bottomMargin=0.5*inch
        )
        styles = getSampleStyleSheet()
        story = []
        
        print("   ✅ SimpleDocTemplate created")
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph("Business Analysis Report", title_style))
        story.append(Spacer(1, 0.2*inch))
        print("   ✅ Title added")
        
        # Business Name
        business_name = profile.get('business_name', 'Business Report')
        story.append(Paragraph(f"<b>{business_name}</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        # Business Info Section
        story.append(Paragraph("<b>Business Information</b>", styles['Heading3']))
        story.append(Paragraph(f"Industry: {profile.get('industry', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"Business Type: {profile.get('business_type', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"Primary Goal: {profile.get('primary_goal', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        print("   ✅ Business info added")
        
        # Key Metrics Table
        story.append(Paragraph("<b>Key Financial Metrics</b>", styles['Heading3']))
        
        metrics_data = [
            ['Metric', 'Value'],
            ['Total Revenue', f"₹{kpis.get('total_revenue', 0):,.2f}"],
            ['Net Profit', f"₹{kpis.get('net_profit', 0):,.2f}"],
            ['Profit Margin', f"{kpis.get('profit_margin', 0):.2f}%"],
            ['Revenue Growth', f"{kpis.get('revenue_growth_rate', 0)}%"],
            ['Burn Rate', f"₹{kpis.get('burn_rate', 0):,.2f}/month"],
            ['Runway', f"{kpis.get('runway_months', 0)} months"],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 0.3*inch))
        print("   ✅ Metrics table added")
        
        # Investment Scores
        story.append(Paragraph("<b>Investment Readiness Scores</b>", styles['Heading3']))
        
        scores_data = [
            ['Score Type', 'Value'],
            ['Shark Tank Score', f"{kpis.get('shark_tank_score', 0)}/100"],
            ['IPO Readiness', f"{kpis.get('ipo_readiness', 0)}/100"],
            ['Scalability Score', f"{kpis.get('scalability_score', 0)}/100"],
            ['Risk Score', f"{kpis.get('risk_score', 0)}/100"],
        ]
        
        scores_table = Table(scores_data, colWidths=[3*inch, 3*inch])
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(scores_table)
        story.append(Spacer(1, 0.3*inch))
        print("   ✅ Scores table added")
        
        # Business Health Summary
        if recommendations:
            try:
                rec_data = json.loads(recommendations) if isinstance(recommendations, str) else recommendations
                if rec_data.get('summary', {}).get('business_health'):
                    story.append(PageBreak())
                    story.append(Paragraph("<b>AI-Generated Business Health Summary</b>", styles['Heading3']))
                    summary_text = rec_data['summary']['business_health'][:500]  # First 500 chars
                    story.append(Paragraph(summary_text, styles['Normal']))
                    story.append(Spacer(1, 0.2*inch))
                    print("   ✅ Business health summary added")
            except Exception as e:
                print(f"   ⚠️ Recommendations summary failed: {e}")
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            f"<i>Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>", 
            styles['Normal']
        ))
        story.append(Paragraph(
            "<i>Powered by AI Business Analyzer</i>", 
            styles['Normal']
        ))
        
        # Build PDF
        print("\n🔨 Building PDF file...")
        doc.build(story)
        print(f"✅ PDF built successfully")
        
        # Verify file exists
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"✅ PDF file verified:")
            print(f"   - Size: {file_size} bytes")
            print(f"   - Path: {filepath}")
        else:
            print(f"❌ PDF file not created!")
            return jsonify({'error': 'PDF creation failed'}), 500
        
        print("\n" + "="*60)
        print("📥 Sending PDF to client...")
        print("="*60 + "\n")
        
        # Send file
        return send_file(
            filepath, 
            mimetype='application/pdf',
            as_attachment=True, 
            download_name=filename
        )
        
    except Exception as e:
        print(f"\n❌ PDF GENERATION ERROR:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500
    
# running the app
if __name__ == "__main__":
    app.run(debug=True)