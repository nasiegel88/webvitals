# Conception

import selenium, os, time, datetime, sys

import pandas as pd
from pandas.api.types import is_numeric_dtype
import dateutil.parser as dparser

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

from tqdm import tqdm
from webdriver_manager.firefox import GeckoDriverManager

def conception(driver, query_list):
    
    '''
    This module will pull conception information such as when a dam was pregnant, how many times they were pregnant, and the IDs of their offspring.
    '''
    
    data = pd.DataFrame()
    
    with tqdm(total=len(query_list)) as progress_bar:
        
            for i in query_list:
                
                    # Go to conception in Webvitals
                    driver=driver
                    driver.find_element_by_name("query_input").send_keys(i)
                    driver.find_element_by_name("submit").click()
                    
                    try:
                        # Return to Animal Summary
                        xpath="/html/body/table[1]/tbody/tr[3]/td/center/table[2]/tbody/tr/td[1]/a"
                        driver.find_element_by_xpath(xpath).click()
                        
                    except NoSuchElementException:
                        s = '''\
                        Animal Number {animal_num} Not Found! 
                    Please be sure you entered a valid animal ID.\
                        '''.format(animal_num=i)
                        print(s)
                        continue
                                            
                    # Go to conception table
                    xpath='/html/body/table[1]/tbody/tr[3]/td/center/table[2]/tbody/tr/td[4]/a'
                    driver.find_element_by_xpath(xpath).click()
                    
                    try:
                        # Extract html table
                        xpath="/html/body/table[2]/tbody/tr/td[1]/center[1]/table"
                        tableelement= driver.find_element_by_xpath(xpath).get_attribute('outerHTML') 
                        table = pd.read_html(str(tableelement))[0]
                        
                    except Exception as e:
                        # Create empty table if one does not exist for animals 
                        no_data =  {
                            'Conception':[None],
                            'Unnamed: 1':[None],
                            'Offspring':[None],
                            'Sex':[None],
                            'Concept Date':[None],
                            'Breed Type':[None],
                            'Unnamed: 6':[None],
                            'Sire':[None],
                            'Unnamed: 8':[None],
                            'Gest Days':[None],
                            'Est':[None],
                            'PregTerm Date':[None],
                            'Delivery Type':[None],
                            'Loc Date':[None],
                            'Location':[None],
                            'Death Type':[None],
                            'Comment':[None]
                        }
                        table = pd.DataFrame(no_data,
                                             columns = list(no_data.keys()))
                        
                    # Add column to specify MMU number
                    table['MMU'] = i
                    first_column = table.pop('MMU')
                    table.insert(0, 'MMU', first_column)  
                    
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
    df.to_csv(f"{timestr}-conception_{output}")

    print('')
    file=f"{absolute_path}-conception_{output}"    
    print(f"Output file is located at: '{file}'")