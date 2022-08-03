import getpass

import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

from jproperties import Properties

from webdriver_manager.firefox import GeckoDriverManager

def login(driver):
    '''
    This module will log into webvitals. Create a `webvitals_config.properties` file with your username
    and password if you want to avoid entering your login credentials each time the program is ran.
    '''

    driver=driver

    # Go to login page
    driver.get("https://davos.primate.ucdavis.edu/login/")
    
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
                
    return driver