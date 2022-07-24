import argparse, pathlib, os, time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from argparse import ArgumentParser

from webdriver_manager.firefox import GeckoDriverManager

# Import custom modules
from scripts import login
from scripts import location
from scripts import diarrhea_observations
from scripts import weight
from scripts import snomed

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

# Enter options
options = Options()
options.add_argument("--headless")

# Install Geckodriver
driver = webdriver.Firefox(executable_path=GeckoDriverManager(version="v0.22.0").install(), options=options)
print('')

# Log into website
driver = login.login(driver)

# Start program
print('')
print('Launching Webvitals webscraper')
print('')
time.sleep(2)

# Run function to scrape records from webvitals
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
    weight.weight(driver, query_list)

elif args.query=='snomed':
    print('Running snomed query')
    time.sleep(2)
    snomed.snomed(driver, query_list)

print('')
print('Driver Title:',driver.title)
print('Driver Name:',driver.name)
driver.quit()