# Diarrhea observations

def diarrhea_observations(ids):
    
    data = pd.DataFrame()
    
    with tqdm(total=len(ids)) as progress_bar:
        
        for i in ids:
            # Go to Diarrhea section in Webvitals
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
            df = df.replace(dict.fromkeys(['D', '+D', '~D', '-D'], ['1']))
            # Replace all move obs with 0
            df = df.replace(dict.fromkeys(['M', '+M', '~M', '-M', '+', '-', '~'], ['0']))
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
        df.to_csv(f"{timestr}-diarrhea_obs_{output}")