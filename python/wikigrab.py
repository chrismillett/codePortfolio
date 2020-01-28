from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException

from pprint import pprint
import csv
import time
import math
import os

start = time.time()

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15'

class BrowserSet:
    def __init__(self):
        self.user_agent()

    def user_agent(self):
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference("general.useragent.override", user_agent)
        self.profile.set_preference('permissions.default.image', 2)
        self.driver = webdriver.Firefox(firefox_profile=self.profile)
        self.driver.set_page_load_timeout(80)


driver = BrowserSet().driver
driver.install_addon(r'C:\Users\Charlotte\AppData\Roaming\Mozilla\Firefox\Profiles\4r6nmp7c.default\extensions\{c7c3483c-0e96-45f4-8772-f84462cdc047}.xpi')
driver.install_addon(r'C:\Users\Charlotte\AppData\Roaming\Mozilla\Firefox\Profiles\4r6nmp7c.default\extensions\uBlock0@raymondhill.net.xpi')
driver.maximize_window()
driver.log_path=os.devnull


baseUrl = "https://en.wikipedia.org/wiki/Main_Page"
articles = []

driver.get(baseUrl)
time.sleep(10)

articleCount = input('Number of articles to grab: ')

articleCount = int(articleCount) + 1

for i in range(1, articleCount):
    randomPage = driver.find_element_by_xpath('/html/body/div[5]/div[2]/div[2]/div/ul/li[5]/a')
    randomPage.click()

    time.sleep(5)

    article = {}

    try:
        article['Title'] = driver.find_element_by_css_selector('h1').text
    except:
        article['Title'] = ''
    
    article['URL'] = driver.current_url
    
    try:
        article['Summary'] = driver.find_element_by_css_selector('p:nth-of-type(1)').text
    except:
        article['Summary'] = ''
    try:
        article['Information 1'] = driver.find_element_by_css_selector('.infobox > tbody > tr:nth-child(2)').text
    except:
        article['Information 1'] = ''
    try:
        article['Information 2'] = driver.find_element_by_css_selector('.infobox > tbody > tr:nth-child(3)').text
    except:
        article['Information 2'] = ''
    try:
        article['Information 3'] = driver.find_element_by_css_selector('.infobox > tbody tr:nth-child(4)').text
    except:
        article['Information 3'] = ''
    try:
        article['Information 4'] = driver.find_element_by_css_selector('.infobox > tbody > tr:nth-child(5)').text
    except:
        article['Information 4'] = ''
    try:
        article['Information 5'] = driver.find_element_by_css_selector('.infobox > tbody > tr:nth-child(6)').text
    except:
        article['Information 5'] = ''
    try:
        article['Information 6'] = driver.find_element_by_css_selector('.infobox > tbody > tr:nth-child(7)').text
    except:
        article['Information 6'] = ''
    try:
        article['Information 7'] = driver.find_element_by_css_selector('.infobox > tbody > tr:nth-child(8)').text
    except:
        article['Information 7'] = ''
    try:
        article['Information 8'] = driver.find_element_by_css_selector('.infobox > tbody > tr:nth-child(9)').text
    except:
        article['Information 8'] = ''
    try:
        article['External Link 1'] = driver.find_element_by_css_selector('ul li:nth-of-type(1) a.external')
    except:
        article['External Link 1'] = ''
    try:
        article['External Link 2'] = driver.find_element_by_css_selector('ul li:nth-of-type(2) a.external')
    except:
        article['External Link 2'] = ''
    try:
        article['External Link 3'] = driver.find_element_by_css_selector('ul li:nth-of-type(3) a.external')
    except:
        article['External Link 3'] = ''
    try:
        article['Category 1'] = driver.find_element_by_css_selector('#mw-normal-catlinks > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1)').text
    except:
        article['Category 1'] = ''
    try:
        article['Category 2'] = driver.find_element_by_css_selector('#mw-normal-catlinks > ul:nth-child(2) > li:nth-child(2) > a:nth-child(1)').text
    except:
        article['Category 2'] = ''
    try:
        article['Category 3'] = driver.find_element_by_css_selector('#mw-normal-catlinks > ul:nth-child(2) > li:nth-child(3) > a:nth-child(1)').text
    except:
        article['Category 3'] = ''
    try:
        article['Category 4'] = driver.find_element_by_css_selector('#mw-normal-catlinks > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1)').text
    except:
        article['Category 4'] = ''
    try:
        article['Category 5'] = driver.find_element_by_css_selector('#mw-normal-catlinks > ul:nth-child(2) > li:nth-child(2) > a:nth-child(1)').text
    except:
        article['Category 5'] = ''
    try:
        article['Category 6'] = driver.find_element_by_css_selector('#mw-normal-catlinks > ul:nth-child(2) > li:nth-child(3) > a:nth-child(1)').text
    except:
        article['Category 6'] = ''
    try:
        article['Category 7'] = driver.find_element_by_css_selector('#mw-normal-catlinks > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1)').text
    except:
        article['Category 7'] = ''
    try:
        article['Category 8'] = driver.find_element_by_css_selector('#mw-normal-catlinks > ul:nth-child(2) > li:nth-child(2) > a:nth-child(1)').text
    except:
        article['Category 8'] = ''
    try:
        article['Category '] = driver.find_element_by_xpath('/html/body/div[3]/div[3]/div[4]/div/div[5]/table/tbody/tr[1]/th/div[2]/a').text
    except:
        article['Category '] = ''

    articles.append(article)

driver.quit()


#write to file
with open("randomWikiPages.csv", 'a', newline='', encoding='utf-8-sig') as new_file:
    headers = ['Title', 'URL', 'Information 1', 'Information 2', 'Information 3', 'Information 4',
     'Information 5', 'Information 6', 'Information 7', 'Information 8', 'Summary', 'External Link 1', 
     'External Link 2', 'External Link 3', 'Category 1', 'Category 2', 'Category 3', 'Category 4', ]
    writer = csv.DictWriter(new_file, fieldnames=headers,
                            extrasaction='ignore', dialect='excel')
    writer.writeheader()
    writer.writerows(articles)


end = time.time()
print('Total time taken: ' + str(math.ceil((end - start) / 60)) + ' minutes.')

