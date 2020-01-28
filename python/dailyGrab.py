import csv
import requests
from bs4 import BeautifulSoup as bs
import math
from pprint import pprint
import time
import os

start = time.time()
time_out = 60
user_agent = {
    'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'}
proxies = {'https': 'https://lum-customer-ai-zone-static:uvc1vshl7xhi@zproxy.lum-superproxy.io:22225','http': 'http://lum-customer-ai-zone-static:uvc1vshl7xhi@zproxy.lum-superproxy.io:22225'}
    

baseUrl = 'https://www.bbc.co.uk/'

r = requests.get(baseUrl)
soup = bs(r.text, 'lxml')


#grab URLs for ten of the top articles currently on the BBC website
headlines = soup.select('[data-bbc-asset-type="article"] a')


articleCount = 0
totalArticles = 50

articles = []

headlineUrls = set()

for headline in headlines:
    articleCount += 1

    try:
        if articleCount <= totalArticles: 
            url = headline['href']
            headlineUrls.add(url)
        else:
            break
    except:
        break

for url in headlineUrls:
    try:
        r = requests.get(url)
        soup = bs(r.text, 'lxml')
    except:
        continue

    article = {}
    article['URL'] = url

    try:
        article['Headline'] = soup.select_one('h1.story-body__h1').text
    except:
        article['Headline'] = ''
    try:
        article['Region/Country'] = soup.select_one('.navigation-wide-list ul .selected .navigation-wide-list__link span').text
    except:
        article['Region/Country'] = ''
    try:
        article['Type'] = soup.select_one('.navigation-wide-list__link.navigation-arrow--open span').text
    except:
        article['Type'] = ''
    try:
        article['Relative Date-Time'] = soup.select_one('.mini-info-list__item div.relative-time').text
    except:
        article['Relative Date-Time'] = ''
    try:
        article['Intro'] = soup.select_one('p.story-body__introduction').text
    except:
        article['Intro'] = ''


    try:
        article['Story'] = soup.select_one('.story-body__inner p:nth-of-type(n+2)').text
    except:
        article['Story'] = ''
    try:
        article['Topic 1'] = soup.select_one('li.tags-list__tags:nth-of-type(1) a').text
    except:
        article['Topic 1'] = ''
    try:
        article['Topic 2'] = soup.select_one('li.tags-list__tags:nth-of-type(2) a').text
    except:
        article['Topic 2'] = ''    
    try:
        article['Topic 3'] = soup.select_one('li.tags-list__tags:nth-of-type(3) a').text
    except:
        article['Topic 3'] = ''
    try:
        article['Topic 4'] = soup.select_one('li.tags-list__tags:nth-of-type(4) a').text
    except:
        article['Topic 4'] = ''    
    try:
        article['Topic 5'] = soup.select_one('li.tags-list__tags:nth-of-type(5) a').text
    except:
        article['Topic 5'] = ''
    try:
        urlement = soup.select_one('[data-entityid="more-on-this-story#1"] a')
        article['Related Story 1'] = urlement['href']
    except:
        article['Related Story 1'] = ''    
    try:
        urlement = soup.select_one('[data-entityid="more-on-this-story#2"] a')
        article['Related Story 2'] = urlement['href']
    except:
        article['Related Story 2'] = ''
    try:
        urlement = soup.select_one('[data-entityid="more-on-this-story#3"] a')
        article['Related Story 3'] = urlement['href']
    except:
        article['Related Story 3'] = ''    
    try:
        urlement = soup.select_one('[data-entityid="more-on-this-story#4"] a')
        article['Related Story 4'] = urlement['href']
    except:
        article['Related Story 4'] = ''
    try:
        urlement = soup.select_one('[data-entityid="more-on-this-story#5"] a')
        article['Related Story 5'] = urlement['href']
    except:
        article['Related Story 5'] = ''


    if article['Headline']:
        pprint(article)
        articles.append(article)
    else:
        articleCount = articleCount - 1




#write to file
with open("bbcHeadlines.csv", 'a', newline='', encoding='utf-8-sig') as new_file:
    headers = ['Headline','Region/Country','Type','Relative Date-Time','Intro','Story','Topic 1','Topic 2','Topic 3','Topic 4','Topic 5',
    'Related Story 1','Related Story 2','Related Story 3','Related Story 4','Related Story 5']
    writer = csv.DictWriter(new_file, fieldnames=headers,
                            extrasaction='ignore', dialect='excel')
    writer.writeheader()
    writer.writerows(articles)


end = time.time()
print('Total time taken: ' + str(math.ceil((end - start) / 60)) + ' minutes.')

