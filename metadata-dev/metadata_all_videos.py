from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time
import logging
import re
import os.path
from fastparquet import write
import pandas as pd
import csv

"""This implementation only collect all the video id's for every channel in the initial csv file.
After your run this code, you will obtain a parquet file with the information of the author's name, the
links for each video, and each video's description.
"""

# setup logging config
logging.basicConfig(level=logging.INFO, filename='metadata_collection.log', 
                    format='%(asctime)s : %(levelname)s : %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

class Driver:
    def __init__(self, browser):
        self.browser = browser

    def setup_driver(self):
        # Set up selected driver 
        if self.browser == "firefox":
            from selenium.webdriver.firefox.options import Options
            from webdriver_manager.firefox import GeckoDriverManager

            # Configuration for the driver 
            options = Options()
            options.headless = False
            # Load driver 
            try:
                path_to_driver = 'PATH/TO/MOZILA_DRIVER' ####---------------------///---- modify here
                driver = webdriver.Firefox(executable_path=path_to_driver, 
                                        options=options)
            except Exception as e:
                logging.info("Problem accessing the driver")
        elif self.browser == "chrome":
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Configuration for the driver 
            options = Options()
            #options.headless = True
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-browser-side-navigation")
            options.add_argument("--disable-infobars")
            options.add_argument("enable-automation")
            options.add_experimental_option('excludeSwitches', ['enable-logging'])

            # Load webdriver if you already have it 
            try:
                path_to_driver = 'PATH/TO/CHROME_DRIVER' ####---------------------///---- modify here
                driver = webdriver.Chrome(executable_path=path_to_driver,
                                        options=options)
            except Exception as e:
                logging.info("Problem accessing the driver")
        else:
            raise ValueError(f"{self.browser} is not a valid driver")
        
        return driver # Return a configured driver 
    
    @staticmethod
    def infine_scroll(driver,channel_url):
        #time.sleep(10)
        driver.get(channel_url) # Open the web page
        time.sleep(20)

        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight") #Scroll down

        while True:
            try:
                # Scroll down to bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Wait to load page
                time.sleep(10)

                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height: # If you already reached the bottom 
                    break
                last_height = new_height # If you have not reached the bottom, then update the last poit 
            except Exception as e:
                logging.info(f"Did not reached the bottom for {channel_url}")

        # Get the page's info
        html = driver.page_source # Collect the data 
        # Parse
        soup = BeautifulSoup(html, "html.parser")
        #driver.quit() # Close driver
        return soup

def metadata_extracting(htlm_info: BeautifulSoup, file_path: str):
    
    # Try to get the author
    author = htlm_info.find(attrs={'class':re.compile(r'tiktok-arkop9-H2ShareTitle ekmpd5l5')}).text

    # Get all links and descriptions to gifts 
    for i in htlm_info.findAll(attrs={'class':re.compile(r'tiktok-x6y88p-DivItemContainerV2 e19c29qe7')}):
        
        # Try to get the links
        try:
            link = i.find('a')['href']
        except Exception as e:
            logging.info("No link was found")
            link = 'No link was found'
        
        # Try to get the descriptions
        try:
            desc = i.find('a', class_="tiktok-1wrhn5c-AMetaCaptionLine eih2qak0")['title'] 
        except Exception as e:
            logging.info(f"No description was found for {link}")
            desc = 'No description was found for'  

        # Arrange data
        info = {'Author':[author],'Video_url':[link], 'Description':[desc]} 
        
        # Save info to parquet
        if not os.path.isfile(file_path):
            write(file_path, pd.DataFrame(info))
        else:
            write(file_path, pd.DataFrame(info), append=True)
        

def main():
    # Read csv with channels 
    path_to_raw_data = 'PATH/TO/CSV_FILE/WITH/CHANNEL_LINKS' ####---------------------///---- modify here
    channels_ls = pd.read_csv(path_to_raw_data, header=None)[0].to_list() # Column 0 contains the channels' url
    driver = Driver('chrome').setup_driver()
    for channel in channels_ls:
        print(channel)
        try:
            #driver = Driver('chrome').setup_driver()
            sopa = Driver.infine_scroll(driver,channel)
            out_path = 'PATH/TO/OUTPUT/FOLDER/gifts_info.parquet' ####---------------------///---- modify here
            metadata_extracting(sopa, out_path)
            print('Done')
        except Exception as e:
            logging.info(f"Data for {channel} was not collected")

if __name__ == "__main__":
    main()

