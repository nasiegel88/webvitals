def snomed(ids):
    
    data = pd.DataFrame()
    
    with tqdm(total=len(ids)) as progress_bar:
        
        for i in ids:
            
            # Go to snomed in Webvitals
            driver.find_element_by_name("query_input").send_keys(i)
            driver.find_element_by_name("submit").click()

            xpath="/html/body/table[1]/tbody/tr[3]/td/center/table[3]/tbody/tr/td[8]/a"
            driver.find_element_by_xpath(xpath).click()

            xpath="/html/body/table[2]"
            df = driver.find_element_by_xpath(xpath).get_attribute('outerHTML')
            soup = BeautifulSoup(df, 'html.parser')
            df = pd.read_html(str(soup))[0]
            df.drop(index=df.index[0:3], 
                    axis=0, 
                    inplace=True)
            df.drop(df.columns.difference(['Date', 'Info Qualifier', 'Seq', 'Code', 'Nomenclature']),
                    1, inplace=True)
            df.drop(df.tail(5).index,
                    inplace = True)

            # Add column to specify MMU number
            df['MMU'] = i
            first_column = df.pop('MMU')
            df.insert(0, 'MMU', first_column)
            table = df.ffill()

            # Append dataframes into one dataframe
            df = data.append(table, ignore_index=True)

            # Log job progess
            progress_bar.update(1)

        globals()['df'] = df