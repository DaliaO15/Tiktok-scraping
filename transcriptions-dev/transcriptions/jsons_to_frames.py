import openpyxl
import pandas as pd
import json 
import subprocess
import os 
from fastparquet import write

"""
This code organises the transcriptions into one data frame per author. 
"""

# Function to read the json files
def open_json(path:str):
    
    # Read file
    with open(path, 'r') as f:
        js = f.read()
        
    return json.loads(js)

# To parse all jsons to a parque file per author
def jsons_to_parque(input_dir_name:str, output_dir_name:str):
    
    # Get paths for all gifts
    channels_names = [f for f in os.listdir(input_dir_name) if not f.startswith('.')]
    paths = [os.path.join(input_dir_name,c) for c in channels_names]
   
    # Create a parque file per author 
    for p in paths:

        jsons = [os.path.join(p,f) for f in os.listdir(p) if not f.startswith('.')]
        author = p.split('/')[-1]
        parquet_path = output_dir_name+author+'.parquet'
        print(parquet_path)
        
        for j in jsons: 
            
            gift_id = j.split('/')[-1].split('.')[0]
            gift_url = 'https://www.tiktok.com/@'+author+'/video/'+gift_id
            texto = open_json(j)['text']
            
            # Arrange data
            info = {'Video_url':[gift_url], 'Text':[texto]}

            # Save info to parquet
            if not os.path.isfile(parquet_path):
                write(parquet_path, pd.DataFrame(info))
            else:
                write(parquet_path, pd.DataFrame(info), append=True)
            
        # Transform parquet to xlsx for the PI   
        #pd.read_parquet(parquet_path, engine='fastparquet').to_excel(output_dir_name+author+'.xlsx',index=False)
           
        
def main(): 
    
    in_dir = 'PATH/TO/FOLDER/FOR/TRANSCRIPTIONS'  ####---------------------///---- modify here
    ou_dir = 'PATH/TO/FOLDER/FOR/TRANSCRIPTIONS_IN_DATAFRAMES'  ####---------------------///---- modify here
    jsons_to_parque(in_dir, ou_dir)
        
    
if __name__ == "__main__":
    main()
