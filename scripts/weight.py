# Weight

import selenium, os, time, datetime

import pandas as pd
import dateutil.parser as dparser

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

from tqdm import tqdm
from webdriver_manager.firefox import GeckoDriverManager

def weight(driver, query_list):
    
    '''
    This module will pull animal weights and the dates the weights were taken and then the function will add how old the animal was in months and days.
    '''
    
    data = pd.DataFrame()
    
    with tqdm(total=len(query_list)) as progress_bar:
        
            for i in query_list:
                
                    # Go to weight TB in Webvitals
                    driver=driver
                    driver.find_element_by_name("query_input").send_keys(i)
                    driver.find_element_by_name("submit").click()

                    # Return to Animal Summary
                    xpath="/html/body/table[1]/tbody/tr[3]/td/center/table[2]/tbody/tr/td[1]/a"
                    driver.find_element_by_xpath(xpath).click()

                    # Extract birthday
                    try:
                        xpath="/html/body/table[2]/tbody/tr/td[1]/table[2]/tbody/tr[5]/td[2]"
                        birthday = driver.find_element_by_xpath(xpath).text
                        dt = dparser.parse(birthday.split()[0], fuzzy=True)
                        birthday = dt.strftime('%Y-%m-%d')
                        
                    except Exception as e:
                        xpath='/html/body/table[2]/tbody/tr/td[1]/table[2]/tbody/tr[4]/td[2]'
                        birthday = driver.find_element_by_xpath(xpath).text
                        dt = dparser.parse(birthday.split()[0], fuzzy=True)
                        birthday = dt.strftime('%Y-%m-%d')   

                    xpath="/html/body/table[1]/tbody/tr[3]/td/center/table[3]/tbody/tr/td[10]/a"
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

                    # Add birthday column
                    table['Birth']=""
                    ninth_column = table.pop('Birth')
                    table.insert(8, 'Birth', ninth_column)
                    table.loc[table['MMU'] == i, ['Birth']] = birthday

                    # Append dataframes into one dataframe
                    data = data.append(table, ignore_index=True)

                    # Log job progress
                    progress_bar.update(1)

    # Drop non-informative data
    df = data.drop(columns = ['Body Condition', 'Conception ID',
                                'Days Pregnant', 'TB', 'Tattoo',
                                'Test 1', 'Test 2'], errors='ignore')
    # Convert to datetime
    ## List age in months
    day_month = 30.436875
    df[["Birth", "Weighing Date"]] = df[["Birth", "Weighing Date"]].apply(pd.to_datetime)

    # Calculate age in days
    df['Age_days'] = (df['Weighing Date'] - df['Birth']).dt.days

    # Calculate age in months
    df['Age_months'] = df.Age_days.div(day_month).round(2)

    # Reorder columns
    column_names = ['MMU', 'Location', 'Birth',
                    'Weighing Date', 'Age_days',
                    'Age_months', 'Weight']
    df = df.reindex(columns=column_names)

    # Add object to namespace
    globals()['df'] = df

    # Export table
    os.makedirs('data', exist_ok=True)
    output='webvitals_query.csv'
    timestr = time.strftime("data/%Y%m%d-%H%M%S")
    absolute_path = os.path.abspath(timestr)
    df.to_csv(f"{timestr}-weight_{output}")

    print('')
    file=f"{absolute_path}-weight_{output}"    
    print(f"Output file is located at: '{file}'")