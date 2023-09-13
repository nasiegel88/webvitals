# BB assessment

import selenium, os, time, sys

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

def bbassessment(driver, query_list):
        
        '''
        This module will pull all animal Biobehavioral Assessment records if a given animal was selected for the assessment. Otherwise, the animal will be added to the output as an empty row containing only the animal's identifier.
        '''
        
        data = pd.DataFrame()
        
        with tqdm(total=len(query_list)) as progress_bar:
        
                for i in query_list:
                
                        # Go to BB assessment in Webvitals
                        driver=driver
                        driver.find_element_by_name("query_input").send_keys(i)
                        driver.find_element_by_name("submit").click()
                        
                        try:
                                # Return to Animal Summary
                                xpath='/html/body/table[1]/tbody/tr[3]/td/center/table[2]/tbody/tr/td[3]'
                                driver.find_element_by_xpath(xpath).click()
                        
                        except NoSuchElementException:
                                s = '''\
                                Animal Number {animal_num} Not Found! 
                                Please be sure you entered a valid animal ID.\
                                '''.format(animal_num=i)
                                print(s)
                                continue
                        
                        try:
                                # Extract table for snomed
                                xpath="/html/body/table[2]/tbody/tr/td[1]/table[2]"
                                tableelement = driver.find_element_by_xpath(xpath).get_attribute('outerHTML')

                                # Clean up table
                                soup = BeautifulSoup(tableelement, 'html.parser')
                                
                                df = pd.DataFrame(pd
                                                .read_html(str(soup))[0]
                                                .dropna(thresh=2)
                                                .values
                                                .reshape(-1, 2)).transpose()
                                
                                df = df.rename(columns=df.iloc[0]).drop(df.index[0])
                                # Remove columns that don't contain anything
                                df = df.loc[:, df.columns.notna()]
                                
                                # Error is resulting dataframe is empty
                                if df.empty == True:
                                        raise RuntimeError('Symbol doesn\'t exist')

                        except Exception as e:
                                # Create empty table if one does not exist for animals
                                no_data = {
                                'Date tested': [None],
                                'Age at testing (days)': [None],
                                'Rearing Condition': [None],
                                'Weight at testing (kg)': [None],
                                'SPF status': [None],
                                'Day 1 Activity': [None],
                                'Day 2 Activity': [None],
                                'Day 1 Emotionality': [None],
                                'Day 2 Emotionality': [None],
                                'Sample 1': [None],
                                'Sample 2': [None],
                                'Sample 3': [None],
                                'Sample 4': [None],
                                'Activity': [None],
                                'Aggression': [None],
                                'Emotionality': [None],
                                'Displacement': [None],
                                'Vigilant': [None],
                                'Confident': [None],
                                'Gentle': [None],
                                'Nervous': [None],
                                'Total White Cell Count (x10^3 / ml)': [None],
                                'Hemoglobin (gm/dl)': [None],
                                'Total Lymphocyte count (/ml)': [None],
                                'Hematocrit (%)': [None],
                                'CD4+ cell numbers (/ml)': [None],
                                'MCV (fl)': [None],
                                'CD8+ cell numbers (/ml)': [None],
                                'Plasma Protein (gm/dl)': [None],
                                'Serotonin transporter promoter': [None],
                                'Monoamine oxidase A promoter': [None],
                                'Behavioral Inhibition Index': [None]
                                }
                                df = pd.DataFrame(no_data, columns = list(no_data.keys()))

                        # Add column to specify MMU number
                        df['MMU'] = i
                        first_column = df.pop('MMU')
                        df.insert(0, 'MMU', first_column)

                        # Append dataframes into one dataframe
                        data = data.append(df, ignore_index=True)
                        
                        # Arrange so animals with assessment records or on top
                        data.sort_values(by=["Date tested"], inplace=True)

                        # Log job progress
                        progress_bar.update(1)
                        
        # Add object to namespace
        globals()['data'] = data

        # Export table
        os.makedirs('data', exist_ok=True)
        output='webvitals_query.csv'
        timestr = time.strftime("data/%Y%m%d-%H%M%S")
        absolute_path = os.path.abspath(timestr)
        data.to_csv(f"{timestr}-bbassessment_{output}")

        print('')
        file=f"{absolute_path}-bbassessment_{output}"    
        print(f"Output file is located at: '{file}'")