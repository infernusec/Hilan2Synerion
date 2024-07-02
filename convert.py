
#!/usr/bin/python
# Written By Snir Sofer
# Repo: https://github.com/infernusec/Hilan2Synerion

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
import re

if not os.getenv('SYNERION_USER') or not os.getenv('SYNERION_PASS'):
    print('SYNERION_USER or SYNERION_PASS is not set!')
    exit(1)

Login_Data = {
	'SynerionUrl':'https://trex.synerioncloud.com/SynerionWeb/Account/Login',
	'username':os.getenv('SYNERION_USER'),
	'password':os.getenv('SYNERION_PASS')
}


def Hilan2Data(filename):
    from bs4 import BeautifulSoup
    import re

    reponse_data = {}
    with open(filename, 'r') as file:
        # Read the entire contents of the file into a string variable
        file_contents = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(file_contents, 'html.parser')

    # Find the table in the HTML (adjust the slector as needed)
    table_rows = soup.select('table')
    reports = table_rows[1].select('tr')
    reports = reports[2:]
    for report in reports:
        data = report.find_all('td')
        date = re.search(r'\d{2}/\d{2}',data[0].text).group(0)
        report_in = data[4].text
        report_out = data[5].text
        if date not in reponse_data:
            reponse_data[date] = []
            
        reponse_data[date].append({"in": report_in, "out": report_out})
    return reponse_data



Hilan_Data = Hilan2Data('test.xls')
HilanDaysKeys = list(Hilan_Data.keys())

# print(Hilan_Data)

# Set up the WebDriver (assuming ChromeDriver is in your PATH)
driver = webdriver.Chrome()
driver.maximize_window()

# actions = ActionChains(driver)


# Navigate to Google
driver.get(Login_Data['SynerionUrl'])

# Find the search box using its name attribute value
search_box = driver.find_element(By.ID, "UserName")
driver.execute_script("arguments[0].setAttribute('type', 'password');", search_box)

search_box.send_keys(Login_Data['username'])
search_box = driver.find_element(By.ID, "Password")
search_box.send_keys(Login_Data['password'])
search_box.send_keys(Keys.RETURN)

wait = WebDriverWait(driver,20)
close_modal = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'span.walkme-action-destroy-1.wm-close-link')))
action = ActionChains(driver)
action.click(close_modal).perform()


time.sleep(2)

def setReport(elm,start,end):
    report_in = elm.find_element(By.CSS_SELECTOR,'div:nth-child(1) > div > div:nth-child(2)')
    inp = report_in.find_element(By.TAG_NAME,'input')
    inp.click()
    inp.send_keys(start)
    
    report_out = elm.find_element(By.CSS_SELECTOR,'div:nth-child(1) > div > div:nth-child(3)')
    outp = report_out.find_element(By.TAG_NAME,'input')
    outp.click()
    #report_out.click()
    outp.send_keys(end)

table = driver.find_element(By.ID,'table1')
table_days = table.find_elements(By.CSS_SELECTOR,'tbody > tr')
total_table_days = len(table_days)


for index, result in enumerate(table_days):
    #action.click(result)
    result.click()
    time.sleep(0.4)
    date = result.find_element(By.CSS_SELECTOR,'td:nth-child(2)')
    current_date = re.search(r'\d{2}/\d{2}',date.text).group(0)
    saved_rows = Hilan_Data[current_date]

    # print(current_date,saved_rows)
    saved_rows_total = len(saved_rows)
    hours_rep = result.find_element(By.CSS_SELECTOR,'td:nth-child(3)')
    # Main div
    main_div = hours_rep.find_element(By.CSS_SELECTOR,'div:nth-child(1)')
    
    if(saved_rows_total > 1):
        for idx in range(saved_rows_total-1):
            hours_rep.find_element(By.CSS_SELECTOR,'button.fa.fa-plus-circle.db-add-punch-btn.flat-button').click()
        
        report_divs = hours_rep.find_elements(By.CSS_SELECTOR,'div.db-in-out-container')
        for idx_mdiv, multi_div in enumerate(report_divs):
            setReport(multi_div,saved_rows[idx_mdiv]['in'],saved_rows[idx_mdiv]['out'])
            saved_rows[idx_mdiv]['exists'] = True
            if current_date in HilanDaysKeys:
                HilanDaysKeys.remove(str(current_date))
            time.sleep(1)
    else:
        setReport(main_div,saved_rows[0]['in'],saved_rows[0]['out'])
        if current_date in HilanDaysKeys:
            HilanDaysKeys.remove(str(current_date))
        saved_rows[0]['exists'] = True

first_elm = table.find_element(By.CSS_SELECTOR,'#table1 > tbody > tr:nth-child(15)')
driver.execute_script("arguments[0].scrollIntoView();", first_elm)
first_elm.click()
time.sleep(4)
#print("last day")
#time.sleep(10000)
print("Missed Dates: ")
for missedDay in HilanDaysKeys:
    print(missedDay,Hilan_Data[missedDay])

# Close the browser
driver.quit()
