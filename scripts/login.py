def login():
    key="webvitals_config.properties"

    try:
        f = open(key)
        configs = Properties()

        with open(key, 'rb') as config_file:
            configs.load(config_file)

        items_view = configs.items()
        list_keys = []
        print(f"'{key}' found!") 
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
            print("[+] Login successful!")
            
        f.close()
        
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
                print('Access granted')
                break
            except NoSuchElementException:
                print('Access denied. Try again.')
                count += 1