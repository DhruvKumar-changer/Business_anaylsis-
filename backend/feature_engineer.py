

import pandas as pd
import numpy as np

class FeatureEngineer:
    """
    Feature Engineering class for creating ML-ready features from business data
    
    Main features created:
    1. Time-based features (Month, Quarter, Year)
    2. Lag features (Previous period values)
    3. Rolling window features (Moving averages)
    4. Growth rate features (Percentage changes)
    """
    
    def __init__(self, dataframe):
        """
        Initialize with a pandas DataFrame
        
        Args:
            dataframe (pd.DataFrame): Raw business data with Date and numeric columns
        """
        self.df = dataframe.copy()  # Create a copy to avoid modifying original
        print(f"✅ FeatureEngineer initialized with {len(self.df)} rows")
    
    def create_time_features(self):
        """
        Extract time-based features from Date column
        
        Creates:
        - Month (1-12)
        - Quarter (1-4)
        - Year
        - Day of Week (0=Monday, 6=Sunday)
        - Is Weekend (0 or 1)
        """
        try:
            # Convert Date column to datetime if not already
            self.df['Date'] = pd.to_datetime(self.df['Date'])
            
            # Extract time features
            self.df['Month'] = self.df['Date'].dt.month
            self.df['Quarter'] = self.df['Date'].dt.quarter
            self.df['Year'] = self.df['Date'].dt.year
            self.df['Day_of_Week'] = self.df['Date'].dt.dayofweek
            self.df['Is_Weekend'] = (self.df['Day_of_Week'] >= 5).astype(int)
            
            print("✅ Time features created: Month, Quarter, Year, Day_of_Week, Is_Weekend")
        except Exception as e:
            print(f"❌ Error creating time features: {e}")
        
        return self
    
    def create_lag_features(self, column='Revenue', lags=[1, 2, 3]):
        """
        Create lag features (previous period values)
        
        Example: Revenue_Lag_1 = Revenue from 1 period ago
        
        Args:
            column (str): Column name to create lags for
            lags (list): List of lag periods (e.g., [1, 2, 3] for last 3 periods)
        """
        try:
            for lag in lags:
                lag_col_name = f'{column}_Lag_{lag}'
                self.df[lag_col_name] = self.df[column].shift(lag)
            
            print(f"✅ Lag features created for {column}: {lags}")
        except Exception as e:
            print(f"❌ Error creating lag features: {e}")
        
        return self
    
    def create_rolling_features(self, column='Revenue', windows=[3, 6]):
        """
        Create rolling window features (moving averages)
        
        Example: Revenue_MA_3 = Average of last 3 periods
        
        Args:
            column (str): Column name to create rolling features for
            windows (list): List of window sizes (e.g., [3, 6] for 3 and 6 period averages)
        """
        try:
            for window in windows:
                # Moving Average
                ma_col_name = f'{column}_MA_{window}'
                self.df[ma_col_name] = self.df[column].rolling(window=window).mean()
                
                # Moving Standard Deviation (volatility)
                std_col_name = f'{column}_STD_{window}'
                self.df[std_col_name] = self.df[column].rolling(window=window).std()
            
            print(f"✅ Rolling features created for {column}: MA and STD for windows {windows}")
        except Exception as e:
            print(f"❌ Error creating rolling features: {e}")
        
        return self
    
    def create_growth_rate(self, column='Revenue'):
        """
        Calculate growth rate (percentage change from previous period)
        
        Formula: (Current - Previous) / Previous * 100
        
        Args:
            column (str): Column name to calculate growth rate for
        """
        try:
            growth_col_name = f'{column}_Growth'
            self.df[growth_col_name] = self.df[column].pct_change() * 100
            
            print(f"✅ Growth rate created for {column}")
        except Exception as e:
            print(f"❌ Error creating growth rate: {e}")
        
        return self
    
    def create_cumulative_features(self, column='Revenue'):
        """
        Create cumulative sum (running total)
        
        Args:
            column (str): Column name to create cumulative sum for
        """
        try:
            cumsum_col_name = f'{column}_Cumsum'
            self.df[cumsum_col_name] = self.df[column].cumsum()
            
            print(f"✅ Cumulative sum created for {column}")
        except Exception as e:
            print(f"❌ Error creating cumulative features: {e}")
        
        return self
    
    def drop_missing_rows(self):
        """
        Remove rows with missing values (NaN)
        
        Note: Lag and rolling features create NaN values for initial rows
        """
        before_count = len(self.df)
        self.df = self.df.dropna()
        after_count = len(self.df)
        removed = before_count - after_count
        
        print(f"🧹 Removed {removed} rows with missing values (Total rows: {after_count})")
        return self
    
    def get_features_dataframe(self):
        """
        Return the feature-engineered DataFrame
        
        Returns:
            pd.DataFrame: DataFrame with all engineered features
        """
        return self.df
    
    def prepare_ml_data(self, target_column='Revenue'):
        """
        Prepare data for machine learning
        
        Separates features (X) and target (y) for ML models
        
        Args:
            target_column (str): Name of the column to predict
            
        Returns:
            tuple: (X, y) where X is features DataFrame and y is target Series
        """
        try:
            # Select only numeric columns
            numeric_df = self.df.select_dtypes(include=[np.number])
            
            # Separate target variable
            if target_column not in numeric_df.columns:
                raise ValueError(f"Target column '{target_column}' not found in numeric columns")
            
            y = numeric_df[target_column]
            X = numeric_df.drop(columns=[target_column])
            
            print(f"✅ ML data prepared:")
            print(f"   Features (X): {X.shape[1]} columns, {X.shape[0]} rows")
            print(f"   Target (y): {y.shape[0]} values")
            print(f"   Feature names: {list(X.columns)}")
            
            return X, y
        
        except Exception as e:
            print(f"❌ Error preparing ML data: {e}")
            return None, None


# ========== EXAMPLE USAGE ==========
if __name__ == "__main__":
    # Example with dummy data
    print("=" * 60)
    print("FEATURE ENGINEERING EXAMPLE")
    print("=" * 60)
    
    # Create sample business data
    dates = pd.date_range(start='2023-01-01', periods=50, freq='D')
    sample_data = pd.DataFrame({
        'Date': dates,
        'Revenue': np.random.randint(10000, 50000, 50),
        'Expenses': np.random.randint(5000, 20000, 50),
        'Customers': np.random.randint(50, 200, 50)
    })
    
    print("\n📊 Original Data (first 5 rows):")
    print(sample_data.head())
    
    # Initialize Feature Engineer
    engineer = FeatureEngineer(sample_data)
    
    # Apply all feature engineering steps
    engineer.create_time_features()
    engineer.create_lag_features(column='Revenue', lags=[1, 2, 3])
    engineer.create_rolling_features(column='Revenue', windows=[3, 7])
    engineer.create_growth_rate(column='Revenue')
    engineer.create_cumulative_features(column='Revenue')
    engineer.drop_missing_rows()
    
    # Get final DataFrame
    final_df = engineer.get_features_dataframe()
    print("\n📊 Feature-Engineered Data (first 5 rows):")
    print(final_df.head())
    print(f"\n📈 Total columns: {len(final_df.columns)}")
    print(f"Column names: {list(final_df.columns)}")
    
    # Prepare for ML
    X, y = engineer.prepare_ml_data(target_column='Revenue')
    
    print("\n" + "=" * 60)
    print("✅ Feature Engineering Complete!")
    print("=" * 60)
    