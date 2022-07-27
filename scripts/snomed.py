# Snomed

import selenium, os, time

import pandas as pd

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

from tqdm import tqdm
from webdriver_manager.firefox import GeckoDriverManager

from bs4 import BeautifulSoup

def snomed(driver, query_list):
        
        '''
        This module will pull all animal records for the time the animal was at the Primate Center-- this includes antibiotics, food, medication, etc.
        '''
        
        data = pd.DataFrame()
        
        with tqdm(total=len(query_list)) as progress_bar:
        
                for i in query_list:
                
                        # Go to snomed in Webvitals
                        driver=driver
                        driver.find_element_by_name("query_input").send_keys(i)
                        driver.find_element_by_name("submit").click()

                        xpath="/html/body/table[1]/tbody/tr[3]/td/center/table[3]/tbody/tr/td[8]/a"
                        driver.find_element_by_xpath(xpath).click()

                        # Extract table for snomed
                        xpath="/html/body/table[2]"
                        tableelement = driver.find_element_by_xpath(xpath).get_attribute('outerHTML')
                        
                        # Clean up table
                        soup = BeautifulSoup(tableelement, 'html.parser')
                        df = pd.read_html(str(soup))[0]
                        df.drop(index=df.index[0:3], 
                                axis=0, 
                                inplace=True)
                        df.drop(df.columns.difference(['Date', 'Info Qualifier', 'Seq', 'Code', 'Nomenclature']),
                                1, inplace=True)
                        df.drop(df.tail(5).index,
                                inplace = True)

                        # Add column to specify MMU number
                        df['MMU'] = i
                        first_column = df.pop('MMU')
                        df.insert(0, 'MMU', first_column)
                        table = df.ffill()

                        # Append dataframes into one dataframe
                        data = data.append(table, ignore_index=True)

                        # Log job progress
                        progress_bar.update(1)
                        
        # Add object to namespace
        df = data
        globals()['df'] = df

        # Export table
        os.makedirs('data', exist_ok=True)
        output='webvitals_query.csv'
        timestr = time.strftime("data/%Y%m%d-%H%M%S")
        absolute_path = os.path.abspath(timestr)
        df.to_csv(f"{timestr}-snomed_{output}")

        print('')
        file=f"{absolute_path}-relocation_{output}"    
        print(f"Output file is located at: '{file}'")