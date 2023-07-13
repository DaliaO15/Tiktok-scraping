from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import logging
import re
import os.path
from fastparquet import write
import pandas as pd
from datetime import datetime, timedelta

# setup logging config
logging.basicConfig(level=logging.INFO, filename='dates_collection.log', 
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
                driver = webdriver.Firefox(executable_path=path_to_driver, options=options)
            except Exception as e:
                logging.info("Problem accessing the driver")
        elif self.browser == "chrome":
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Configuration for the driver 
            options = Options()
            options.headless = True
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
    def get_info(driver,gift_url):
        #time.sleep(10)
        driver.get(gift_url) # Open the web page
        # Get the page's info
        html = driver.page_source # Collect the data 
        # Parse
        soup = BeautifulSoup(html, "html.parser")
        #driver.quit() # Close driver
        return soup
    

def format_date(date:str):
    date = date.strip() # Remove spaces at the begging and end
    if 'ago' in date: # For dates such as 3d ago
        days_ago = int(date.split('d')[0])
        upload_day = (datetime.today() - timedelta(days=days_ago)).strftime('%d')
        date = datetime.today().strftime('%Y-%m-{}').format(upload_day)
    elif len(date) < 6: # For dates like '5-27'
        current_year = datetime.today().year
        date = datetime.strptime(date, "%m-%d").strftime(f"{current_year}-%m-%d")
    else: # For the other dates
        pass
    return date

def date_extracting(htlm_info: BeautifulSoup, gift_url:str, file_path: str):
    
    # Try to get the author
    try:
        date = htlm_info.findAll(attrs={'class':re.compile(r'tiktok-1sklzc9-SpanOtherInfos e17fzhrb2')})[0].text.split('·')[-1]
        date = format_date(date)
    except:
        date = None

    # Arrange data
    info = {'Video_url':[gift_url], 'Upload_date':[date]} 
    
    # Save info to parquet
    if not os.path.isfile(file_path):
        write(file_path, pd.DataFrame(info))
    else:
        write(file_path, pd.DataFrame(info), append=True)
        

def main():
    # Read csv with channels 
    path_to_info_data = 'PATH/TO/INFO_FILE/gifts_info.parquet' ####---------------------///---- modify here
    gift_url_ls = pd.read_parquet(path_to_info_data, engine='fastparquet')['Video_url'].to_list()
    driver = Driver('chrome').setup_driver()
    counter = 0
    for gift_url in gift_url_ls:

        # Track position
        if counter % 100 == 0:
            print(f'We are in gift number {counter} at {gift_url}')

        try:
            sopa = Driver.get_info(driver, gift_url)
            out_path = 'PATH/TO/DATES_FILE/gifts_with_date.parque' ####---------------------///---- modify here
            date_extracting(sopa, gift_url, out_path)
        except Exception as e:
            logging.info(f"Data for {gift_url} was not collected")

        counter += 1

if __name__ == "__main__":
    main()
