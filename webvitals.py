import argparse, pathlib, os, time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

from jproperties import Properties

from argparse import ArgumentParser
from webdriver_manager.firefox import GeckoDriverManager

# Import custom modules
from scripts import location
from scripts import diarrhea_observations
from scripts import weight
from scripts import snomed

def login():
    '''
    This function will log into webvitals. Create a `webvitals_config.properties` file with your username
    and password if you want to avoid entering your login credentials each time the program is ran.
    '''
    key="webvitals_config.properties"

    try:
        f = open(key)
        configs = Properties()

        with open(key, 'rb') as config_file:
            configs.load(config_file)

        items_view = configs.items()
        list_keys = []
        print(f"'{key}' found!\n") 
        for item in items_view:
            list_keys.append(item[0])
            
        # Login attempt (1)
        driver.find_element_by_name("ssousername").send_keys(configs.get("USERNAME")[0])
        driver.find_element_by_name("password").send_keys(configs.get("PASSWORD")[0])
        xpath="/html/body/center/table/tbody/tr[3]/td/font/input[1]"
        driver.find_element_by_xpath(xpath).click()
        
        # Enter Webvitals
        driver.find_element_by_xpath("/html/body/ul/li[1]/a").click()
        
        # Handle errors logging in
        WebDriverWait(driver=driver, timeout=10).until(
        lambda x: x.execute_script("return document.readyState === 'complete'"))
        error_message = "Incorrect username or password."
        errors = driver.find_elements_by_class_name("flash-error")

        # Print errors optionally
        if any(error_message in e.text for e in errors):
            print("[!] Login failed!")
        else:
            print("[+] Login successful!\n")
  
    except IOError:
        print('Enter correct username and password combo to continue')
        count=0
        while count < 3:
            username = getpass.getpass('Enter Username:')
            password = getpass.getpass('Enter Password:')
            try:
                driver.find_element_by_name("ssousername").send_keys(username)
                driver.find_element_by_name("password").send_keys(password)
                xpath="/html/body/center/table/tbody/tr[3]/td/font/input[1]"
                driver.find_element_by_xpath(xpath).click()
                
                # Enter Webvitals
                driver.find_element_by_xpath("/html/body/ul/li[1]/a").click()
                print('Access granted\n')
                time.sleep(2)
                break
            except NoSuchElementException:
                print('Access denied. Try again.')
                count += 1
#     else:
#         globals()['driver'] = driver

# Create parser
parser = ArgumentParser()

parser.add_argument('-l', '--list', help='delimited list input', type=str)

parser.add_argument('-f', '--file', help='text input', type=pathlib.Path)

parser.add_argument('-q', '--query', 
                    nargs="?",
                    choices=['location', 'diarrhea_observations',
                             'weight', 'snomed'],
                    default='location'
                    )

args = parser.parse_args()

if args.file is not None and args.list is not None:

    parser.error("Choose --list or --file but not both!")

elif args.file is not None:

    with args.file.open('r') as file:
        file_content = file.read()
        query_list = file_content.split("\n")

elif args.list is not None:

    query_list = [str(item) for item in args.list.split(',')]

# Manually handle the default for "function"
query = "location" if args.query is None else args.query

# Start program
print('')
print('Launching Webvitals webscraper')
print('')
time.sleep(2)

# Enter options
options = Options()
options.add_argument("--headless")

# Install Geckodriver
driver = webdriver.Firefox(executable_path=GeckoDriverManager(version="v0.20.0").install(),
                          options=options)

# Go to login page
driver.get("https://davos.primate.ucdavis.edu/login/")

login() # Login to website

# Run function to scraped records from webvitals
if args.query=='location':
    print('Running location query')
    time.sleep(2)
    location.location(driver, query_list)

elif args.query=='diarrhea_observations':
    print('Running diarrhea observation query')
    time.sleep(2)
    diarrhea_observations.diarrhea_observations(driver, query_list)

elif args.query=='weight':
    print('Running weight query')
    time.sleep(2)
    weight.weight()

elif args.query=='snomed':
    print('Running snomed query')
    time.sleep(2)
    snomed.snomed(driver, query_list)

print('')
print('Driver Title:',driver.title)
print('Driver Name:',driver.name)
driver.quit()