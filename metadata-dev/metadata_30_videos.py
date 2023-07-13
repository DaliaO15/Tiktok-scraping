from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import os
import pandas as pd
from fastparquet import write
import time

"""This implementation only collect the first 30 video id's for every channel in the initial csv file.
After your run this code, you will obtain a parquet file with the information of the author's name, the
links for each video, and each video's description.
"""

def get_30_fist_ids(driver, url:str, output_file_path:str):
    
    stop = True
    while stop: # Run until we have the data we need 
        driver.get(url)
        time.sleep(5)
        html = driver.execute_script("return document.documentElement.outerHTML;")
        soup = BeautifulSoup(html, "html.parser")
        data = soup.find("script", {"id": "SIGI_STATE", "type": "application/json"})

        if data.text is not None:
            data = json.loads(data.text)
            stop = False

    # Process data and store in parquet file 
    for i in data["ItemModule"]:
        Author = data["ItemModule"][i]["author"]
        Video_url = 'https://www.tiktok.com/@'+ Author +'/video/' + data["ItemModule"][i]["id"]
        Description = data["ItemModule"][i]["desc"]

        stuff = {"Author": [Author],"Video_url": [Video_url],"Description": [Description],}

        # Save info to parquet
        if not os.path.isfile(output_file_path):
            write(output_file_path, pd.DataFrame(stuff))
        else:
            write(output_file_path, pd.DataFrame(stuff), append=True)

def main():
    # Configuration for the driver 
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--headless')
    path_to_driver = 'PATH/TO/CHROME_DRIVER' ####---------------------///---- modify here
    browser = webdriver.Chrome(executable_path=path_to_driver,
                                            options=options)
    out_path = 'PATH/TO/OUTPUT/FOLDER/gifts_info.parquet' ####---------------------///---- modify here

    # Get the info per channel 
    path_to_raw_data = 'PATH/TO/CSV_FILE/WITH/CHANNEL_LINKS' ####---------------------///---- modify here
    channels_ls = pd.read_csv(path_to_raw_data, header=None)[0].to_list() 
    for url in channels_ls:
        get_30_fist_ids(driver=browser,url = url, output_file_path = out_path)
        print(f'Done for {url}')
    
    browser.quit()


if __name__ == "__main__":
    main()