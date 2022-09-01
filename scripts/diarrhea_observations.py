# Diarrhea observations

import selenium, os, time, sys

import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

from tqdm import tqdm
from webdriver_manager.firefox import GeckoDriverManager

def diarrhea_observations(driver, query_list):
    
    '''
    This module will add all diarrhea observations for Primate Center animals and determine whether the animals had idiopathic chronic diarrhea (ICD) which is defined as 45 or more diarrhea observations within a 6-month period according to Blackwood et al., 2008 Comp. Med.
    '''
    
    data = pd.DataFrame()
    
    with tqdm(total=len(query_list)) as progress_bar:
        
        for i in query_list:
            
            # Go to Diarrhea section in Webvitals
            try:
                # Return to Animal Summary
                driver = driver
                driver.find_element_by_name("query_input").send_keys(i)    
                driver.find_element_by_name("submit").click()

                text = 'Animal Not Found!  Please be sure you entered a valid animal ID.'
                
                if text in driver.page_source:
                    s = '''
                    Animal Number {animal_num} Not Found! Please be sure you entered a valid animal ID.
                    '''.format(animal_num=i)
                    print('')
                    print(s)
                    print('')
                    continue
                
                xpath="/html/body/table[1]/tbody/tr[3]/td/center/table[2]/tbody/tr/td[6]/a"
                driver.find_element_by_xpath(xpath).click()
                
                # Extract html table
                xpath="/html/body/table[2]/tbody/tr/td[1]/center[1]/table"
                tableelement= driver.find_element_by_xpath(xpath).get_attribute('outerHTML') 
                table = pd.read_html(str(tableelement))[0]

                # Add column to specify MMU number
                table['MMU'] = i
                first_column = table.pop('MMU')
                table.insert(0, 'MMU', first_column)

                # Append dataframes into one dataframe
                data = data.append(table, ignore_index=True)
                
                # Replace blank cells with 0
                df = data.fillna(0)
                
                # Replace all diarrhea obs with 1
                d_list = ['D', '+D', '+DM', '~D', '-D', '-DM', 'DM', 'DM+', '~DM', 'DMM']
                df = df.replace(dict.fromkeys(d_list, ['1']))
                
                # Replace all move obs with 0
                m_list = ['M', 'MM', '+M', '~M', '-M', '~MM', '~MMM', '-MM', '+MM', '+~M', '+', '-', '~', '~-']
                df = df.replace(dict.fromkeys(m_list, ['0']))
                
                # Sum monthly diarrhea obs
                df['Month_diarrhea_obs'] = df.iloc[:,3:31].astype(int).sum(axis=1, numeric_only=True)
                
                # Calculate the # of obs in a 6-month window
                df['Rolling_sum_obs'] = df.Month_diarrhea_obs.rolling(6).sum().fillna(0)
                
                # Determine if animal meeting qual. for chronic issue
                df['Chronic_diarrhea'] = np.where(
                    df['Rolling_sum_obs'] > 45, 1, np.where(
                    df['Rolling_sum_obs'] < 45, 0, 0)) 
            
                # Drop day columns
                df.drop(df.iloc[:, 3:34], axis = 1, inplace=True)
                
                # Log job progress
                progress_bar.update(1)
                
            except NoSuchElementException:
                # Go back if error 500 is reached
                driver.back()
                
                s = '''\
                Animal Number {animal_num} exists but no table was found.
                This could be due to an error on the admin side.
                {animal_num} will be included as an empty row in the resulting table.\
                '''.format(animal_num=i)
                print(s)
                
                no_data =  {
                    'Year':[None],
                    'Month':[None],
                    'Month_diarrhea_obs':[None],
                    'Rolling_sum_obs':[None],
                    'Chronic_diarrhea':[None]
                }
                missing = pd.DataFrame(no_data,
                                       columns = list(no_data.keys()))

                missing['MMU'] = i
                first_column = missing.pop('MMU')
                missing.insert(0, 'MMU', first_column)
                
                # Log job progress
                progress_bar.update(1)
            
            # Append missing data to final table    
            try:
                df = df.append(missing, ignore_index=True)
                
            except NameError:
                continue 
            
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