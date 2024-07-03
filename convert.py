#!/usr/bin/python
# Written By Snir Sofer
# Repo: https://github.com/infernusec/Hilan2Synerion
import os
import argparse
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def parse_arguments():
    parser = argparse.ArgumentParser(description="Synerion Automation Script")
    parser.add_argument('-u', '--username', required=False, help='Synerion username')
    parser.add_argument('-p', '--password', required=False, help='Synerion password')
    parser.add_argument('-f', '--file', required=True, help='Filename to load Hilan data')
    return parser.parse_args()


class SynerionAutomation:
    def __init__(self):
        self.login_data = {
            'SynerionUrl': 'https://trex.synerioncloud.com/SynerionWeb/Account/Login'
        }
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 20)


    def load_hilan_data(self, filename):
        response_data = {}
        with open(filename, 'r') as file:
            file_contents = file.read()
        soup = BeautifulSoup(file_contents, 'html.parser')
        table_rows = soup.select('table')
        reports = table_rows[1].select('tr')[2:]
        for report in reports:
            data = report.find_all('td')
            date = re.search(r'\d{2}/\d{2}', data[0].text).group(0)
            report_in = data[4].text
            report_out = data[5].text
            if date not in response_data:
                response_data[date] = []
            response_data[date].append({"in": report_in, "out": report_out})
        return response_data

    def login(self,username,password):
        self.driver.get(self.login_data['SynerionUrl'])
        self.enter_text(By.ID, "UserName", username)
        self.enter_text(By.ID, "Password", password, submit=True)
        close_modal = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.walkme-action-destroy-1.wm-close-link')))
        ActionChains(self.driver).click(close_modal).perform()
        time.sleep(2)

    def enter_text(self, by, identifier, text, submit=False):
        element = self.driver.find_element(by, identifier)
        self.driver.execute_script("arguments[0].setAttribute('type', 'password');", element)
        element.send_keys(text)
        if submit:
            element.send_keys(Keys.RETURN)

    def set_report(self, elm, start, end):
        report_in = elm.find_element(By.CSS_SELECTOR, 'div:nth-child(1) > div > div:nth-child(2)')
        inp = report_in.find_element(By.TAG_NAME, 'input')
        inp.click()
        inp.send_keys(start)

        report_out = elm.find_element(By.CSS_SELECTOR, 'div:nth-child(1) > div > div:nth-child(3)')
        outp = report_out.find_element(By.TAG_NAME, 'input')
        outp.click()
        outp.send_keys(end)

    def process_table(self):
        table = self.driver.find_element(By.ID, 'table1')
        table_days = table.find_elements(By.CSS_SELECTOR, 'tbody > tr')
        for result in table_days:
            result.click()
            time.sleep(0.4)
            date = result.find_element(By.CSS_SELECTOR, 'td:nth-child(2)')
            current_date = re.search(r'\d{2}/\d{2}', date.text).group(0)
            saved_rows = self.hilan_data.get(current_date, [])

            if not saved_rows:
                continue

            hours_rep = result.find_element(By.CSS_SELECTOR, 'td:nth-child(3)')
            main_div = hours_rep.find_element(By.CSS_SELECTOR, 'div:nth-child(1)')

            if len(saved_rows) > 1:
                for _ in range(len(saved_rows) - 1):
                    hours_rep.find_element(By.CSS_SELECTOR, 'button.fa.fa-plus-circle.db-add-punch-btn.flat-button').click()

                report_divs = hours_rep.find_elements(By.CSS_SELECTOR, 'div.db-in-out-container')
                for idx, multi_div in enumerate(report_divs):
                    self.set_report(multi_div, saved_rows[idx]['in'], saved_rows[idx]['out'])
                    saved_rows[idx]['exists'] = True
                if current_date in self.hilan_days_keys:
                    self.hilan_days_keys.remove(current_date)
                #time.sleep(1)
            else:
                self.set_report(main_div, saved_rows[0]['in'], saved_rows[0]['out'])
                if current_date in self.hilan_days_keys:
                    self.hilan_days_keys.remove(current_date)
                saved_rows[0]['exists'] = True
        time.sleep(10)
        first_elm = table.find_element(By.CSS_SELECTOR,'#table1 > tbody > tr:nth-child(15)')
        self.driver.execute_script("arguments[0].scrollIntoView();", first_elm)
        first_elm.click()
        time.sleep(4)

    def run(self,username,password,xls_file):
        self.hilan_data = self.load_hilan_data(xls_file)
        self.hilan_days_keys = list(self.hilan_data.keys())
        self.login(username,password)
        self.process_table()
        self.print_missed_dates()
        self.driver.quit()

    def print_missed_dates(self):
        print("Missed Dates:")
        for missed_day in self.hilan_days_keys:
            print(missed_day, self.hilan_data[missed_day])


if __name__ == "__main__":
    username = os.getenv('SYNERION_USER')
    password = os.getenv('SYNERION_PASS')
    args = parse_arguments()
    if((not username or not password) and (not args.username or not args.password)):
        print('SYNERION_USER or SYNERION_PASS is not set!')
        exit(1)
    if(args.username and args.password):
        username = args.username
        password = args.password
    automation = SynerionAutomation()
    automation.run(username,password,args.file)
