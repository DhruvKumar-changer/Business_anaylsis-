import mysql.connector
from mysql.connector import Error 
import json 
from datetime import datetime

#Database class that interact with the database
class BusinessDatabase:
    def __init__(self):
        #database credentials that is used for the connection
        self.host = "localhost" #change after render or deploy
        self.user = "root"
        self.password = "dhruv8872"
        self.database = "business_analyzer_db"  #mysql database name 
        #initally server is not connected 
        self.connection = None
    
    #1.Enstablish the connection of Mysql
    def connect(self):
        #mysql.connector.connect helps to create the link that connect the Mqsql 
        try:
            self.connection = mysql.connector.connect(
                host = self.host,
                user = self.user,
                password = self.password,
                database = self.database
            )
            #check the connection is build or not
            if self.connection.is_connected():
                print("Connected to MySQL")
                return True
        except Exception as e:
            print(f"Connection error:{e}")
            return False 


    #2. Creating the required tables 
    def create_tables(self):
        cursor = self.connection.cursor() #cursor helps to execute the queries 

        # Table 1: Businesses = storing the basic details of the business
        query_businesses = """ 
            CREATE TABLE IF NOT EXISTS businesses(
            id INT AUTO_INCREMENT PRIMARY KEY,
            business_name VARCHAR(200) NOT NULL,
            industry VARCHAR(100),
            business_type VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        #RUN the query 
        cursor.execute(query_businesses)
        print("Table businesses created/verified successfully")

        #Table 2: Analysis = storing all the kpis analysis 
        query_analyses = """
        CREATE TABLE IF NOT EXISTS analyses(
            id INT AUTO_INCREMENT PRIMARY KEY,
            business_id INT,
            total_revenue DECIMAL(15, 2),
            total_costs DECIMAL(15, 2),
            net_profit DECIMAL(15, 2),
            profit_margin DECIMAL(5, 2),
            ebitda DECIMAL(15, 2),
            burn_rate DECIMAL(15, 2),
            scalability_score INT,
            risk_score INT,
            ipo_readiness INT,
            shark_tank_score INT,
            full_kpis JSON,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (business_id) REFERENCES businesses(id)
        )
        """
        


        #Table 3 : Predictions = storing the model prediction data
        query_predictions = """
        CREATE TABLE IF NOT EXISTS predictions(
        id INT AUTO_INCREMENT PRIMARY KEY,
        business_id INT,
        prediction_type VARCHAR(50),
        predicted_values JSON,
        model_used VARCHAR(100),
        accuracy_score DECIMAL(5,2),
        predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (business_id) REFERENCES businesses(id)
        )
        """
        #Run all the queries
        cursor.execute(query_analyses)
        print("Table 'analyses' created")
        
        cursor.execute(query_predictions)
        print("Table 'predictions' created")
        #free the resource
        cursor.close()

    def insert_business(self, business_name, industry, business_type):
        #activate cursor 
        cursor = self.connection.cursor()
        #SQL Query -insert the statement
        query = """
        INSERT INTO businesses(business_name,industry,business_type)VALUES(%s,%s,%s) 
        """
        #order the values in %s where %s is the placeholder prevent from the sql injection 
        values = (business_name,industry,business_type)
        #execute the query 
        cursor.execute(query,values)
        #commit the changes by which it store permanently in the database
        self.connection.commit()
        #getting the newly inserted row id
        business_id = cursor.lastrowid
        print(f"Business added: {business_name} (ID:{business_id})")
        cursor.close()
        return business_id


    def insert_analysis(self, business_id, kpis):
        cursor = self.connection.cursor()
        #important kpi store in separate columns for fast query
        query = """
        INSERT INTO analyses(
            business_id, 
            total_revenue, 
            total_costs, 
            net_profit,
            profit_margin,
            ebitda,
            burn_rate,
            scalability_score,
            risk_score,
            ipo_readiness,
            shark_tank_score,
            full_kpis
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            business_id,
            kpis.get('total_revenue'),
            kpis.get('total_costs'),
            kpis.get('net_profit'),
            kpis.get('profit_margin'),
            kpis.get('ebitda'),
            kpis.get('burn_rate'),
            kpis.get('scalability_score'),
            kpis.get('risk_score'),
            kpis.get('ipo_readiness'),
            kpis.get('shark_tank_score'),
            json.dumps(kpis)
        )
        cursor.execute(query, values)
        self.connection.commit()
        analysis_id = cursor.lastrowid
        print(f"Analysis added (ID: {analysis_id})")
        cursor.close()
        return analysis_id


    def insert_prediction(self, business_id, prediction_type, predictions, model_used, accuracy):
        cursor = self.connection.cursor()
        query = """
        INSERT INTO predictions(
        business_id,
        prediction_type,
        predicted_values,
        model_used,
        accuracy_score
        )VALUES(%s,%s,%s,%s,%s)
        """
        values = (
            business_id,
            prediction_type,
            json.dumps(predictions) ,#convert the list values into the json
            model_used,
            accuracy
        )
        cursor.execute(query,values)
        self.connection.commit()
        prediction_id = cursor.lastrowid
        print(f"Prediction save (ID: {prediction_id})")
        cursor.close()
        return prediction_id

    def get_business_by_id(self, business_id):
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT * FROM businesses WHERE id = %s"
        cursor.execute(query, (business_id,))
        business = cursor.fetchone() #where fetchone means return only one row
        cursor.close()
        return business

    def get_latest_analysis(self, business_id):
        cursor = self.connection.cursor(dictionary=True)
        query = """
        SELECT * FROM analyses WHERE business_id = %s
        ORDER BY analyzed_at DESC
        LIMIT 1
        """
        cursor.execute(query,(business_id,))
        analysis = cursor.fetchone()
        #Convert the JSON string into dict
        if analysis and analysis['full_kpis']:
            analysis['full_kpis'] = json.loads(analysis['full_kpis'])
        cursor.close()
        return analysis

    def get_all_analyses(self, business_id):
        cursor = self.connection.cursor(dictionary=True)
        query = """
        SELECT * FROM analyses WHERE business_id = %s
        ORDER BY analyzed_at DESC
        """
        cursor.execute(query, (business_id,))
        #fetch all the rows 
        analyses = cursor.fetchall()
        #convert into the json
        for analysis in analyses:
            if analysis and analysis.get('full_kpis'):
                analysis['full_kpis'] = json.loads(analysis['full_kpis'])
        cursor.close()
        return analyses

    def get_latest_prediction(self, business_id):
        cursor = self.connection.cursor(dictionary=True)
        query = """
        SELECT * FROM predictions WHERE business_id = %s
        ORDER BY predicted_at DESC
        LIMIT 1
        """
        cursor.execute(query,(business_id,))
        prediction = cursor.fetchone()
        #json array into the list
        if prediction and prediction['predicted_values']:
            prediction['predicted_values']= json.loads(prediction['predicted_values'])
        cursor.close()
        return prediction


    def close(self):
        #closing the connection
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")





