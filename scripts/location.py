# Location
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

def location(driver, query_list):
    
    '''
    This module will measure how long an animal spent at any location in the Primate Center and record the time spent
    in at each location. The module will also pull information on whether an animal died at a location.
    '''    
    data = pd.DataFrame()
    
    with tqdm(total=len(query_list)) as progress_bar:
        
        for i in query_list:

            # Go to relocation history in Webvitals
            driver = driver
            driver.find_element_by_name("query_input").send_keys(i)
            driver.find_element_by_name("submit").click()

            # Return to Animal Summary
            xpath="/html/body/table[1]/tbody/tr[3]/td/center/table[2]/tbody/tr/td[1]/a"
            driver.find_element_by_xpath(xpath).click()

            # Look for cause of death if animal has passed 
            
            try:
                xpath="/html/body/table[2]/tbody/tr/td[1]/table[2]/tbody/tr[11]"
                cause_of_death = driver.find_element_by_xpath(xpath).text

            except NoSuchElementException: 
                xpath="/html/body/table[2]/tbody/tr/td[1]/table[2]/tbody/tr[1]/td[4]"
                cause_of_death = driver.find_element_by_xpath(xpath).text
           
            # Go to relocation history in Webvitals
            xpath="/html/body/table[1]/tbody/tr[3]/td/center/table[3]/tbody/tr/td[5]/a"
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

            # Add cause of death if animal has passed 
            table['Cause_of_death']=""
            table.loc[table['MMU'] == i, ['Cause_of_death']] = cause_of_death

            # Append dataframes into one dataframe
            data = data.append(table, ignore_index=True)
            
            # Log job progess
            progress_bar.update(1)

        # Clean output table   
        data = data.rename(columns={"Time at Locationyr : mon : day" : "Time"})
        data = data.join(data['Time'].str.split(':', 3, expand=True))
        data = data.rename(columns={0:"Year",1:"Month",2:"Day"})

        # Subset date of death if animal is dead
        death = (
            data
            .loc[data['Location'] == 'DEAD']
            .rename(columns={"Date In":"Dead"})
        )[['MMU', 'Dead']]
        
        # Merge dataframes
        df = (
            data
            .merge(death, on='MMU', how='left')
        )
        df[df["Location"].str.contains("DEAD")==False]
        
        # Convert age to numeric
        df['Year'] = pd.to_numeric(df['Year'])
        df['Month'] = pd.to_numeric(df['Month'])
        df['Day'] = pd.to_numeric(df['Day'])
        
        # List age in months
        day_year = 365.2425
        day_month = 30.436875
        df['Days'] = df.Year.mul(day_year) + df.Month.mul(day_month) + df.Day
        df['Months'] = df.Days.div(day_month)
        df.drop(['Year', 'Month', 'Day', 'Days', 'Time'],inplace=True, axis=1)
        df = df.round(2)
        
        # Add object to namespace
        globals()['df'] = df
        
        # Export table
        os.makedirs('data', exist_ok=True)
        output='webvitals_query.csv'
        timestr = time.strftime("data/%Y%m%d-%H%M%S")
        absolute_path = os.path.abspath(timestr)
        df.to_csv(f"{timestr}-relocation_{output}")
        
    print('')
    file=f"{absolute_path}-relocation_{output}"    
    print(f"Output file is located at: '{file}'")
