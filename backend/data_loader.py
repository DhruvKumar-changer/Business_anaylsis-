#read the csv file 

import pandas as pd

class Dataloader:
    def __init__(self,filepath):   #constructor
        self.filepath = filepath  #store the file path that define in the app.py file
        self.df = None    #dataframe remain empty intially 

        #load the csv file
    def load_csv(self):
        try:
            self.df = pd.read_csv(self.filepath)  #read the csv file
            print(f"The file is loaded! Rows = {len(self.df)}")
            return True
        except Exception as e:
            print(f"file is not loaded:{e}")
            return False

    #Show the data in the file
    def show_data(self):
        if self.df is not None:
            print((self.df.head()))  #print the 5 rows for checking 
        else:
            print("file is not loaded yet")
    def get_dataframe(self):
        return self.df

# #Create the instance
# loader = Dataloader("file.csv")
# #call the functions through the instance
# loader.load_csv()
# loader.show_data()
# df = loader.get_dataframe()
# print(df.shape)