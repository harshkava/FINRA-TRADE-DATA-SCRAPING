# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 14:32:31 2019

@author: harsh kava

Scrape data for FINRA trade using CUSIP & Trade Date details

"""

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time,csv


def createURL(ticker, tradedate):
    try:
        url = 'http://finra-markets.morningstar.com/BondCenter/BondTradeActivitySearchResult.jsp?'
        #ticker=FGM4361059&startdate=09%2F02%2F2019&enddate=09%2F02%2F2019'
        
        # ----------------- for start and end dates ----------------- 
        #tradedate = '1/2/2019'
        x = ['0'+x if len(x) == 1 else x for x in tradedate.split('/') ]
        
        encodedDate = '%2F'.join(x)
        
        # ----------------- for URL ----------------- 
        tickerString = ticker
        startdate = 'startdate='+encodedDate
        enddate = 'enddate='+encodedDate
        
        finalURL = url+tickerString+'&'+startdate+'&'+enddate
        
        print('finalURL ::',finalURL)
        
        return finalURL

    except Exception as e:
        print(e)
        return None 



#make browser
ua=UserAgent()
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (ua.random)
service_args=['--ssl-protocol=any','--ignore-ssl-errors=true']
driver = webdriver.Chrome('chromedriver.exe',desired_capabilities=dcap,service_args=service_args)


tradeHistoryURl = []

#--------------------  1st Time load  -------------------------------------------------------------------------
link = 'http://finra-markets.morningstar.com/BondCenter/Default.jsp'
driver.get(link)        #visit the link

search = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH,'//*[@id="TabContainer"]/div/div[1]/div[2]/ul/li[3]/a/span')))#
search.click()

inputBond = driver.find_element_by_xpath('//*[@id="firscreener-cusip"]')
inputBond.send_keys('37045XBJ4')

showResults = driver.find_element_by_xpath('//*[@id="ms-finra-advanced-search-form"]/div[2]/input[2]')
showResults.click()
#disclaimer = 'http://finra-markets.morningstar.com/BondCenter/UserAgreement.jsp'
#driver.get(disclaimer)

time.sleep(2)
agree = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH,'//*[@id="ms-agreement"]/input')))#driver.find_element_by_xpath('//*[@id="ms-agreement"]/input')
agree.click()
time.sleep(12)
    

#--------------------  Main Processing  ------------------------------------------------

data = []
head = ['Date',' Time',' Settlement',' Status',' Quantity','Price','Yield','Remuneration','ATS',' Modifier','2nd Modifier','Special','As-Of','Side','Reporting Party Type','Contra Party Type','CUSIP']
print('hardcoded Header ::', head)

#with open('Cusip_Tradedate.csv') as csv_file:
with open('Input_Test_Data.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    next(csv_reader)
    for row in csv_reader:
        try:
            tradedate   = row[0]
            cusip       = row[1]
            
            print(tradedate)
            print(cusip)
            time.sleep(1)
            
            link = 'http://finra-markets.morningstar.com/BondCenter/Default.jsp'
            driver.get(link)        #visit the link
            time.sleep(3)
            
            search = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH,'//*[@id="TabContainer"]/div/div[1]/div[2]/ul/li[3]/a')))#
            search.click()
            
            inputBond = driver.find_element_by_xpath('//*[@id="firscreener-cusip"]')
            inputBond.send_keys(cusip)
            time.sleep(1)
            showResults = driver.find_element_by_xpath('//*[@id="ms-finra-advanced-search-form"]/div[2]/input[2]')
            showResults.click()
            time.sleep(3)
    
            URL = driver.current_url    
            print('URL ::',URL)
            
            s = URL.split('?')
            params = s[1].split('&')
            ticker = params[0]

            print('ticker :: ',ticker)
            
            tradeHistory = createURL(ticker, tradedate)
            print(tradeHistory)
            
            tradeHistoryURl.append(tradeHistory)
            
            driver.get(tradeHistory)
            time.sleep(3)
    
            #get table details
            try:
                table = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="ms-glossary"]/div/table/tbody')))
                
                totalPages = driver.find_element_by_xpath('//*[@id="ms-glossary"]/div/table/tfoot/tr/td/div/span').text.split(' ')[1]
                
                #totalPages = driver.find_element_by_class_name('qs-pageutil-total').text.split(' ')[1]
                print('totalPages in Search Result ::',totalPages)
                totalPagesCount = int(totalPages)
                i = 0
                while i <= totalPagesCount:
                    nextPage = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'qs-pageutil-next')))
                            
                    #data in table
                    rows = table.find_elements_by_tag_name('tr')
                    for tr in rows:
                        tds = tr.find_elements_by_tag_name('td')
                        rowData = [d.text  for d in tds]
                        print(rowData)
                        print(cusip)
                        rd = rowData + [cusip]
                        print(rd)
                        data.append(rd)
    
                    
                    #Click Next Button until it is active
                    if 'disabled' in nextPage.get_attribute('class'):
                        break;
                    nextPage.click()
                    i =i+1
                    time.sleep(3)
                
            except Exception as e:
                print(e)
                continue
        except Exception as e:
                print(e)
                continue
        
#write csv from table
try:
    with open('Finra_Results.csv', mode='w', newline='') as trade_file:
        writer = csv.writer(trade_file, delimiter=',')
    
        writer.writerow(head)
        for d in data:
            writer.writerow(d)
            
        print('Finra_Results.csv file created.')
except Exception as e:
    print(e)
    print('Could not create csv')
        
        
