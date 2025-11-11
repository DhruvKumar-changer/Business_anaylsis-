#cleaning the data 

import pandas as pd
import numpy as np 

class DataCleaner:
    #store the dataframe in the constructor
    def __init__(self,dataframe):
        self.df = dataframe

    #handling the missing values in the data 
    def handle_missing_values(self):
        numeric_cols = self.df.select_dtypes(include=["number"]).columns
        for col in numeric_cols:
            self.df[col].fillna(self.df[col].mean(),inplace=True)

        string_cols = self.df.select_dtypes(include=["object"]).columns
        for col in string_cols:
            self.df[col].fillna("Unknown",inplace=True)
        return self.df
    
    #remove the duplicates values in the data 
    def remove_duplicates(self):
        before = len(self.df)
        self.df.drop_duplicates(inplace=True)
        after = len(self.df)
        remove = before - after
        if remove >0:
            print(f"The Duplicates {remove} values are removed ")
        else:
            print(("No Duplicates found"))
        return self.df

    #format the date column in the datetime format
    def format_dates(self):
        if "Date" in self.df.columns:
            self.df["Date"] = pd.to_datetime(self.df["Date"], errors="coerce")
            print("Date formated")
        else:
            print("no dates found")
        return self.df
    
    #remove outlier means that values that are uncertain and extremly unique
    def remove_outliers(self,z_threshold=3):
        numeric_cols = self.df.select_dtypes(include=["number"]).columns
        for col in numeric_cols:
            z_scores = np.abs(( self.df[col]- self.df[col].mean() ) / self.df[col].std())
            self.df = self.df[z_scores < z_threshold]
        return self.df

    #call  all the functions 
    def clean_all(self):
        self.handle_missing_values()
        self.remove_duplicates()
        self.format_dates()
        return self.df
    # Return the cleaned DataFrame
    def get_dataframe(self):
        return self.df


# #creating the object 
# cleaner = DataCleaner("self.df")
# cleaner_df = cleaner.clean_all()