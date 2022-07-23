# Diarrhea observations

import selenium, os, time

import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

from tqdm import tqdm
from webdriver_manager.firefox import GeckoDriverManager

def diarrhea_observations(driver, query_list):
    
    '''
    This function will add all diarrhea for CNPRC animals and determine whether
    the animals had idiopathic chronic diarrhea which is defined as 45 or more 
    diarrhea observations within a 6-month period.
    '''
    
    data = pd.DataFrame()
    
    with tqdm(total=len(query_list)) as progress_bar:
        
        for i in query_list:
            
            # Go to Diarrhea section in Webvitals
            driver = driver
            driver.find_element_by_name("query_input").send_keys(i)
            driver.find_element_by_name("submit").click()
            xpath="/html/body/table[1]/tbody/tr[3]/td/center/table[2]/tbody/tr/td[6]/a"
            driver.find_element_by_xpath(xpath).click()

            # Extract html table
            xpath="/html/body/table[2]/tbody/tr/td[1]/center[1]/table"
            tableelement= (
                WebDriverWait(driver,10)
                .until(EC.visibility_of_element_located((By.XPATH, xpath)))
                .get_attribute('outerHTML')
            )        
            table = pd.read_html(str(tableelement))[0]

            # Add column to specify MMU number
            table['MMU'] = i
            first_column = table.pop('MMU')
            table.insert(0, 'MMU', first_column)

            # Append dataframes into one dataframe
            data = data.append(table, ignore_index=True)
            
            # Log job progess
            progress_bar.update(1)

            # Replace blank cells with 0
            df = data.fillna(0)
            # Replace all diarrhea obs with 1
            df = df.replace(dict.fromkeys(['D', '+D', '~D', '-D', '-DM'], ['1']))
            # Replace all move obs with 0
            df = df.replace(dict.fromkeys(['M', '+M', '~M', '-M', '~MM', '-MM', '+MM', '+', '-', '~'], ['0']))
            # Sum monthly diarrhea obs
            df['Month_diarrhea_obs'] = df.iloc[:,3:31].astype(int).sum(axis=1, numeric_only=True)
            # Calcualte the # of obs in a 6-month window
            df['Rolling_sum_obs'] = df.Month_diarrhea_obs.rolling(6).sum().fillna(0)
            # Determine if animal meeting qual. for chronic issue
            df['Chronic_diarrhea'] = np.where(
                df['Rolling_sum_obs'] > 45, 1, np.where(
                df['Rolling_sum_obs'] < 45, 0, 0))   
            
        # Add object to namespace
        globals()['df'] = df
        
        # Export table
        os.makedirs('data', exist_ok=True)
        output='webvitals_query.csv'
        timestr = time.strftime("data/%Y%m%d-%H%M%S")
        absolute_path = os.path.abspath(timestr)
        df.to_csv(f"{timestr}-diarrhea_obs_{output}")
     
    print('')
    file=f"{absolute_path}-diarrhea_obs_{output}"    
    print(f"Output file is located at: '{file}'")
