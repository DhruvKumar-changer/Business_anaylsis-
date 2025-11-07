

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import numpy as np
import os

class MLPredictor:
    """
    Machine Learning Predictor for business forecasting
    
    Supports:
    - Linear Regression
    - Random Forest
    - Gradient Boosting
    
    Automatically selects best model based on R² score
    """
    
    def __init__(self):
        """Initialize ML models"""
        self.linear_model = None
        self.rf_model = None
        self.gb_model = None
        self.best_model = None
        self.best_model_name = None
        self.feature_names = None
        self.metrics = {}
        
        print("✅ MLPredictor initialized")
    
    def train_models(self, X, y, test_size=0.2):
        """
        Train multiple ML models and select the best one
        
        Args:
            X (pd.DataFrame): Features
            y (pd.Series): Target variable
            test_size (float): Proportion of data for testing (default: 0.2)
            
        Returns:
            dict: Dictionary containing metrics for all models
        """
        print("\n" + "=" * 60)
        print("TRAINING ML MODELS")
        print("=" * 60)
        
        # Store feature names for future predictions
        self.feature_names = list(X.columns)
        
        # Split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        print(f"\n📊 Data Split:")
        print(f"   Training set: {len(X_train)} rows ({(1-test_size)*100:.0f}%)")
        print(f"   Testing set: {len(X_test)} rows ({test_size*100:.0f}%)")
        print(f"   Features: {X.shape[1]}")
        
        # ===== MODEL 1: LINEAR REGRESSION =====
        print("\n" + "-" * 60)
        print("🔹 Training Linear Regression...")
        print("-" * 60)
        
        self.linear_model = LinearRegression()
        self.linear_model.fit(X_train, y_train)
        
        y_pred_linear = self.linear_model.predict(X_test)
        
        mae_linear = mean_absolute_error(y_test, y_pred_linear)
        rmse_linear = np.sqrt(mean_squared_error(y_test, y_pred_linear))
        r2_linear = r2_score(y_test, y_pred_linear)
        
        self.metrics['linear_regression'] = {
            'MAE': round(mae_linear, 2),
            'RMSE': round(rmse_linear, 2),
            'R2': round(r2_linear, 4)
        }
        
        print(f"Linear Regression Results:")
        print(f"   MAE (Mean Absolute Error): ₹{mae_linear:,.2f}")
        print(f"   RMSE (Root Mean Squared Error): ₹{rmse_linear:,.2f}")
        print(f"   R² Score: {r2_linear:.4f}")
        
        # ===== MODEL 2: RANDOM FOREST =====
        print("\n" + "-" * 60)
        print("🔹 Training Random Forest...")
        print("-" * 60)
        
        self.rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.rf_model.fit(X_train, y_train)
        
        y_pred_rf = self.rf_model.predict(X_test)
        
        mae_rf = mean_absolute_error(y_test, y_pred_rf)
        rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
        r2_rf = r2_score(y_test, y_pred_rf)
        
        self.metrics['random_forest'] = {
            'MAE': round(mae_rf, 2),
            'RMSE': round(rmse_rf, 2),
            'R2': round(r2_rf, 4)
        }
        
        print(f"Random Forest Results:")
        print(f"   MAE (Mean Absolute Error): ₹{mae_rf:,.2f}")
        print(f"   RMSE (Root Mean Squared Error): ₹{rmse_rf:,.2f}")
        print(f"   R² Score: {r2_rf:.4f}")
        
        # ===== MODEL 3: GRADIENT BOOSTING =====
        print("\n" + "-" * 60)
        print("🔹 Training Gradient Boosting...")
        print("-" * 60)
        
        self.gb_model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        self.gb_model.fit(X_train, y_train)
        
        y_pred_gb = self.gb_model.predict(X_test)
        
        mae_gb = mean_absolute_error(y_test, y_pred_gb)
        rmse_gb = np.sqrt(mean_squared_error(y_test, y_pred_gb))
        r2_gb = r2_score(y_test, y_pred_gb)
        
        self.metrics['gradient_boosting'] = {
            'MAE': round(mae_gb, 2),
            'RMSE': round(rmse_gb, 2),
            'R2': round(r2_gb, 4)
        }
        
        print(f"Gradient Boosting Results:")
        print(f"   MAE (Mean Absolute Error): ₹{mae_gb:,.2f}")
        print(f"   RMSE (Root Mean Squared Error): ₹{rmse_gb:,.2f}")
        print(f"   R² Score: {r2_gb:.4f}")
        
        # ===== SELECT BEST MODEL =====
        print("\n" + "=" * 60)
        print("MODEL SELECTION")
        print("=" * 60)
        
        r2_scores = {
            'Linear Regression': r2_linear,
            'Random Forest': r2_rf,
            'Gradient Boosting': r2_gb
        }
        
        self.best_model_name = max(r2_scores, key=r2_scores.get)
        
        if self.best_model_name == 'Linear Regression':
            self.best_model = self.linear_model
        elif self.best_model_name == 'Random Forest':
            self.best_model = self.rf_model
        else:
            self.best_model = self.gb_model
        
        print(f"\n🏆 Best Model: {self.best_model_name}")
        print(f"   R² Score: {r2_scores[self.best_model_name]:.4f}")
        print("=" * 60)
        
        return self.metrics
    
    def save_model(self, filepath='models/sales_predictor.pkl'):
        """
        Save the best trained model to disk
        
        Args:
            filepath (str): Path to save the model file
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save model with metadata
            model_data = {
                'model': self.best_model,
                'model_name': self.best_model_name,
                'feature_names': self.feature_names,
                'metrics': self.metrics
            }
            
            joblib.dump(model_data, filepath)
            print(f"\n✅ Model saved successfully: {filepath}")
            print(f"   Model type: {self.best_model_name}")
        
        except Exception as e:
            print(f"❌ Error saving model: {e}")
    
    def load_model(self, filepath='models/sales_predictor.pkl'):
        """
        Load a trained model from disk
        
        Args:
            filepath (str): Path to the model file
        """
        try:
            model_data = joblib.load(filepath)
            
            self.best_model = model_data['model']
            self.best_model_name = model_data['model_name']
            self.feature_names = model_data['feature_names']
            self.metrics = model_data['metrics']
            
            print(f"\n✅ Model loaded successfully: {filepath}")
            print(f"   Model type: {self.best_model_name}")
            print(f"   Features: {len(self.feature_names)}")
        
        except Exception as e:
            print(f"❌ Error loading model: {e}")
    
    def predict(self, X_new):
        """
        Make predictions on new data
        
        Args:
            X_new (pd.DataFrame): New features to predict
            
        Returns:
            np.array: Predictions
        """
        if self.best_model is None:
            raise ValueError("Model not trained yet! Call train_models() first.")
        
        predictions = self.best_model.predict(X_new)
        return predictions
    
    def predict_next_periods(self, last_features, num_periods=6):
        """
        Predict future periods (simplified approach)
        
        Note: This is a basic implementation. For production, use proper
        time series forecasting with updated lag features.
        
        Args:
            last_features (np.array or pd.Series): Features from the last known period
            num_periods (int): Number of future periods to predict
            
        Returns:
            list: Predicted values for next N periods
        """
        if self.best_model is None:
            raise ValueError("Model not trained yet! Call train_models() first.")
        
        print(f"\n📈 Generating predictions for next {num_periods} periods...")
        
        predictions = []
        current_features = np.array(last_features).reshape(1, -1)
        
        for period in range(num_periods):
            # Predict next value
            pred = self.best_model.predict(current_features)[0]
            predictions.append(round(pred, 2))
            
            # Note: In production, update lag features here
            # For now, keeping features constant (simplified)
        
        print(f"✅ Predictions generated: {predictions}")
        return predictions
    
    def get_feature_importance(self, top_n=10):
        """
        Get feature importance (only for tree-based models)
        
        Args:
            top_n (int): Number of top features to return
            
        Returns:
            dict: Feature names and their importance scores
        """
        if self.best_model_name in ['Random Forest', 'Gradient Boosting']:
            importances = self.best_model.feature_importances_
            
            feature_importance = dict(zip(self.feature_names, importances))
            
            # Sort by importance
            sorted_features = sorted(
                feature_importance.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:top_n]
            
            print(f"\n📊 Top {top_n} Important Features ({self.best_model_name}):")
            for feature, importance in sorted_features:
                print(f"   {feature}: {importance:.4f}")
            
            return dict(sorted_features)
        else:
            print(f"⚠️ Feature importance not available for {self.best_model_name}")
            return {}


# ========== EXAMPLE USAGE ==========
if __name__ == "__main__":
    import pandas as pd
    
    print("=" * 60)
    print("ML PREDICTOR EXAMPLE")
    print("=" * 60)
    
    # Create sample data
    np.random.seed(42)
    n_samples = 100
    
    X = pd.DataFrame({
        'Month': np.random.randint(1, 13, n_samples),
        'Quarter': np.random.randint(1, 5, n_samples),
        'Revenue_Lag_1': np.random.randint(10000, 50000, n_samples),
        'Revenue_MA_3': np.random.randint(15000, 45000, n_samples),
        'Customers': np.random.randint(50, 200, n_samples)
    })
    
    y = pd.Series(np.random.randint(20000, 60000, n_samples), name='Revenue')
    
    print(f"\n📊 Sample Data:")
    print(f"   Features: {X.shape}")
    print(f"   Target: {y.shape}")
    
    # Initialize and train
    predictor = MLPredictor()
    metrics = predictor.train_models(X, y)
    
    # Save model
    predictor.save_model()
    
    # Feature importance
    predictor.get_feature_importance()
    
    # Future predictions
    last_row = X.iloc[-1].values
    future_predictions = predictor.predict_next_periods(last_row, num_periods=6)
    
    print("\n" + "=" * 60)
    print("✅ ML Training Complete!")
    print("=" * 60)