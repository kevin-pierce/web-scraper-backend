import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, abort
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import os
import asyncio

import pymongo
from pymongo import MongoClient
import dns
from bson import BSON
from bson import json_util
from bson.json_util import dumps
import json

def scrape_all_releases_sneakerNews(shoeReleaseDB, chromeOptions):
    allShoeReleasesCollection = shoeReleaseDB.shoeReleases
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chromeOptions)
    driver.get("https://sneakernews.com/release-dates/")
    time.sleep(2)
    body = driver.find_element_by_tag_name("body")

    # Ensure entire page is loaded prior to parsing (Using selenium, we simulate a scroll function to load all release entries)
    numPageDowns = 60
    while numPageDowns:
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.5)
        numPageDowns-=1

    response = driver.page_source
    driver.quit()
    soup = BeautifulSoup(response, "html.parser")
    # Now finds all release-containing divs, including the ones that load on scroll
    shoeReleases = soup.find_all('div', attrs={"class": [
                                                        "releases-box col lg-2 sm-6 paged-1", 
                                                        "releases-box col lg-2 sm-6 paged-1 just_added", 
                                                        "releases-box col lg-2 sm-6 paged-2",
                                                        "releases-box col lg-2 sm-6 paged-2 just_added", 
                                                        "releases-box col lg-2 sm-6 paged-3",
                                                        "releases-box col lg-2 sm-6 paged-3 just_added"]}) 

    shoes = []

    for deal in shoeReleases:
        shoeContent = deal.find('div', attrs={"class":"content-box"})
        shoeDetails = shoeContent.find("div", attrs={"class":"post-data"})
        
        shoeObject = {
            "releaseRegion":shoeDetails.find_all("p")[3].text[8:].strip(),
            "sizeRun":shoeDetails.find_all("p")[0].text[10:].strip(),
            "shoeCW":shoeDetails.find_all("p")[1].text[7:].strip(),
            "shoeName":shoeContent.find("h2").find("a").text,
            "shoePrice":shoeContent.find("span", attrs={"class":"release-price"}).text.strip(),
            "shoeReleaseDate":shoeContent.find("div", attrs={"class":"release-date-and-rating"}).find("span", attrs={"class":"release-date"}).text.strip(),
            "shoeImg":deal.find('div', attrs={"class":"image-box"}).find("a").find("img")['src'],
        }
        shoes.append(shoeObject);

    if (allShoeReleasesCollection.count_documents({}) == 0):
        allShoeReleasesCollection.insert_many(shoes)
    else:
        allShoeReleasesCollection.delete_many({})
        allShoeReleasesCollection.insert_many(shoes)

def scrape_jordan_releases_sneakerNews(shoeReleaseDB, chromeOptions):
    allJordans = []
    jordanShoeReleasesCollection = shoeReleaseDB.jordanReleases
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chromeOptions)
    driver.get("https://sneakernews.com/air-jordan-release-dates/")
    time.sleep(2)
    body = driver.find_element_by_tag_name("body")

    # Ensure entire page is loaded prior to parsing (Using selenium, we simulate a scroll function to load all release entries)
    numPageDowns = 60
    while numPageDowns:
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.5)
        numPageDowns-=1
    response = driver.page_source
    driver.quit()
    soup = BeautifulSoup(response, "html.parser")
    jordanReleases = soup.find_all('div', attrs={"class": ["releases-box col lg-2 sm-6 paged-1", 
                                                        "releases-box col lg-2 sm-6 paged-1 just_added", 
                                                        "releases-box col lg-2 sm-6 paged-2",
                                                        "releases-box col lg-2 sm-6 paged-2 just_added", 
                                                        "releases-box col lg-2 sm-6 paged-3",
                                                        "releases-box col lg-2 sm-6 paged-3 just_added", 
                                                        "releases-box col lg-2 sm-6 paged-4",
                                                        "releases-box col lg-2 sm-6 paged-4 just_added",
                                                        "releases-box col lg-2 sm-6 paged-5",
                                                        "releases-box col lg-2 sm-6 paged-5 just_added"]})
    jordans = []

    for deal in jordanReleases:
        jShoeContent = deal.find('div', attrs={"class":"content-box"})
        jShoeDetails = jShoeContent.find("div", attrs={"class":"post-data"})
        
        jordanShoeObject = {
            "releaseRegion":jShoeDetails.find_all("p")[3].text[8:].strip(),
            "sizeRun":jShoeDetails.find_all("p")[0].text[10:].strip(),
            "shoeCW":jShoeDetails.find_all("p")[1].text[7:].strip(),
            "shoeName":jShoeContent.find("h2").find("a").text,
            "shoePrice":jShoeContent.find("span", attrs={"class":"release-price"}).text.strip(),
            "shoeReleaseDate":jShoeContent.find("div", attrs={"class":"release-date-and-rating"}).find("span", attrs={"class":"release-date"}).text.strip(),
            "shoeImg":deal.find('div', attrs={"class":"image-box"}).find("a").find("img")['src'],
        }
        jordans.append(jordanShoeObject);

    # Wipe the DB prior to pushing all new entries
    if (jordanShoeReleasesCollection.count_documents({}) != 0):
        jordanShoeReleasesCollection.delete_many({}) 
        jordanShoeReleasesCollection.insert_many(jordans)
    else:
        jordanShoeReleasesCollection.insert_many(jordans)

def scrape_yeezy_releases_sneakerNews(shoeReleaseDB, chromeOptions):
    allYeezys = []
    yeezyShoeReleasesCollection = shoeReleaseDB.yeezyReleases
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chromeOptions)
    driver.get("https://sneakernews.com/adidas-yeezy-release-dates/")
    time.sleep(2)
    body = driver.find_element_by_tag_name("body")

    # Ensure entire page is loaded prior to parsing (Using selenium, we simulate a scroll function to load all release entries)
    numPageDowns = 40
    while numPageDowns:
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.5)
        numPageDowns-=1
        
    response = driver.page_source
    driver.quit()
    soup = BeautifulSoup(response, "html.parser")
    yeezyReleases = soup.find_all('div', attrs={"class": ["releases-box col lg-2 sm-6 paged-1", 
                                                        "releases-box col lg-2 sm-6 paged-1 just_added", 
                                                        "releases-box col lg-2 sm-6 paged-2",
                                                        "releases-box col lg-2 sm-6 paged-2 just_added", 
                                                        "releases-box col lg-2 sm-6 paged-3",
                                                        "releases-box col lg-2 sm-6 paged-3 just_added"]})
    yeezys = []

    for deal in yeezyReleases:
        yShoeContent = deal.find('div', attrs={"class":"content-box"})
        yShoeDetails = yShoeContent.find("div", attrs={"class":"post-data"})
        
        yeezyShoeObject = {
            "releaseRegion":yShoeDetails.find_all("p")[3].text[8:].strip(),
            "sizeRun":yShoeDetails.find_all("p")[0].text[10:].strip(),
            "shoeCW":yShoeDetails.find_all("p")[1].text[7:].strip(),
            "shoeName":yShoeContent.find("h2").find("a").text,
            "shoePrice":yShoeContent.find("span", attrs={"class":"release-price"}).text.strip(),
            "shoeReleaseDate":yShoeContent.find("div", attrs={"class":"release-date-and-rating"}).find("span", attrs={"class":"release-date"}).text.strip(),
            "shoeImg":deal.find('div', attrs={"class":"image-box"}).find("a").find("img")['src'],
        }
        yeezys.append(yeezyShoeObject)

    # Wipe the DB prior to pushing all new entries
    if (yeezyShoeReleasesCollection.count_documents({}) != 0):
        yeezyShoeReleasesCollection.delete_many({})
        yeezyShoeReleasesCollection.insert_many(yeezys)
    else:
        yeezyShoeReleasesCollection.insert_many(yeezys)

def scrape_all_releases_footlocker(shoeReleaseDB, chromeOptions):
    allReleases = []
    allShoeReleasesCollection = shoeReleaseDB.shoeReleases # We are not going to be using a "Line-specific" shoe DB
    #footlockerHeader = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
    print("Getting RELEASES")
    #response = requests.get("https://www.footlocker.ca/en/release-dates", headers=footlockerHeader, timeout=15)
    driver = webdriver.Chrome(options=chromeOptions, executable_path='./chromedriver') # FOR LOCAL ONLY
    driver.get("https://www.footlocker.ca/en/release-dates")
    time.sleep(2)
   
    response = driver.page_source

    soup = BeautifulSoup(response, 'html.parser')
    print(soup)

    # shoeReleases = soup.find_all('div', attrs={"class":"c-release-product-wrap flex col"})
    # print(len(shoeReleases))

    # for shoe in shoeReleases:
    #     print(shoe.find('span', attrs={"class":"c-release-product-month"}).text) # Found Date
    #     print(shoe.find('span', attrs={"class":"c-image"}))
    

# Sale Running Shoes
def scrape_nike_runner_sales(shoeReleaseDB, chromeOptions):
    allSaleNikeRunner = []
    shoeSubLinks = []

    nikeRunnerSaleCollection = shoeReleaseDB.nikeRunnerSales
    #driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chromeOptions)
    driver = webdriver.Chrome(options=chromeOptions, executable_path='./chromedriver') # FOR LOCAL ONLY
    driver.get("https://www.nike.com/ca/w/sale-running-shoes-37v7jz3yaepzy7ok")
    time.sleep(2)
    body = driver.find_element_by_tag_name("body")

    numPageDowns = 15
    while numPageDowns:
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.5)
        numPageDowns-=1

    response = driver.page_source
    driver.quit()
    soup = BeautifulSoup(response, "html.parser")

    runnerSales = soup.find_all('div', attrs={"class":"product-card__body"})

    # Compile Links
    for shoe in runnerSales:
        shoeLink = shoe.find('a', attrs={"class":"product-card__img-link-overlay"})
        shoeSubLinks.append(shoeLink["href"])

    for link in shoeSubLinks:
        driver = webdriver.Chrome(options=chromeOptions, executable_path='./chromedriver') # FOR LOCAL ONLY
        #driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chromeOptions)
        driver.get(str(link))
        time.sleep(0.5)

        response = driver.page_source
        driver.quit()
        soup = BeautifulSoup(response, "html.parser")

        # Scrape all available sizes, strip tags and place the data into an array
        shoeSizeAvailability = []
        sizeData = soup.find('fieldset', attrs={"class":"mt5-sm mb3-sm body-2 css-1pj6y87"}).find_all('div', attrs={"class":False})
        for size in sizeData:
            if ("disabled" in str(size)):
                continue
            else:
                availableSize = size.find("label").text
                shoeSizeAvailability.append(str(size.get_text()))
                print(shoeSizeAvailability)
    
        nikeRunnerObject = {
            "shoeName":soup.find('div', attrs={"class":"pr2-sm css-1ou6bb2"}).find('h1', attrs={"class":"headline-2 css-zis9ta"}).text,
            "shoeType":soup.find('div', attrs={"class":"pr2-sm css-1ou6bb2"}).find('h2', attrs={"class":"headline-5-small pb1-sm d-sm-ib css-1ppcdci"}).text,
            "shoeReducedPrice":soup.find('div', attrs={"class":"product-price is--current-price css-s56yt7"}).text,
            "shoeOldPrice":soup.find('div', attrs={"class":"product-price css-1h0t5hy"}).text,
            "shoeImg":soup.find('source', attrs={"srcset":True})["srcset"],
            "shoeCW":soup.find('li', attrs={"class":"description-preview__color-description ncss-li"}).text[14:],
            "shoeDesc":soup.find('div', attrs={"class":"pt4-sm prl6-sm prl0-lg"}).find('p').text,
            "shoeSizeAvailability":shoeSizeAvailability,
            "shoeLink":str(link)
        }
        allSaleNikeRunner.append(nikeRunnerObject)

    if (nikeRunnerSaleCollection.count_documents({}) != 0):
        nikeRunnerSaleCollection.delete_many({})
        nikeRunnerSaleCollection.insert_many(allSaleNikeRunner)
    else:
        nikeRunnerSaleCollection.insert_many(allSaleNikeRunner)

def scrape_nike_lifestyle_sales(shoeReleaseDB, chromeOptions):
    allSaleNikeLifestyle = []
    shoeSubLinks = []

    nikeLifestyleSaleCollection = shoeReleaseDB.nikeLifestyleSales
    #driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chromeOptions)
    driver = webdriver.Chrome(options=chromeOptions, executable_path='./chromedriver') # FOR LOCAL ONLY
    driver.get("https://www.nike.com/ca/w/sale-lifestyle-shoes-13jrmz3yaepzy7ok")
    time.sleep(2)
    body = driver.find_element_by_tag_name("body")

    numPageDowns = 30
    while numPageDowns:
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.5)
        numPageDowns-=1

    response = driver.page_source
    driver.quit()
    soup = BeautifulSoup(response, "html.parser")

    lifestyleSales = soup.find_all('div', attrs={"class":"product-card__body"})
    
    # Compile Links
    for shoe in lifestyleSales:
        shoeLink = shoe.find('a', attrs={"class":"product-card__img-link-overlay"})
        shoeSubLinks.append(shoeLink["href"])

    for link in shoeSubLinks:
        driver = webdriver.Chrome(options=chromeOptions, executable_path='./chromedriver') # FOR LOCAL ONLY
        #driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chromeOptions)
        driver.get(str(link))
        time.sleep(0.5)

        response = driver.page_source
        driver.quit()
        soup = BeautifulSoup(response, "html.parser")

        # Scrape all available sizes, strip tags and place the data into an array - ALSO ignore sizes that are "greyed out"
        shoeSizeAvailability = []
        sizeData = soup.find('fieldset', attrs={"class":"mt5-sm mb3-sm body-2 css-1pj6y87"}).find_all('div', attrs={"class":False})
        for size in sizeData:
            if ("disabled" in str(size)):
                continue
            else:
                availableSize = size.find("label").text
                shoeSizeAvailability.append(str(size.get_text()))
                print(shoeSizeAvailability)

        nikeLifestyleObject = {
            "shoeName":soup.find('div', attrs={"class":"pr2-sm css-1ou6bb2"}).find('h1', attrs={"class":"headline-2 css-zis9ta"}).text,
            "shoeType":soup.find('div', attrs={"class":"pr2-sm css-1ou6bb2"}).find('h2', attrs={"class":"headline-5-small pb1-sm d-sm-ib css-1ppcdci"}).text,
            "shoeReducedPrice":soup.find('div', attrs={"class":"product-price is--current-price css-s56yt7"}).text,
            "shoeOldPrice":soup.find('div', attrs={"class":"product-price css-1h0t5hy"}).text,
            "shoeImg":soup.find('source', attrs={"srcset":True})["srcset"],
            "shoeCW":soup.find('li', attrs={"class":"description-preview__color-description ncss-li"}).text[14:],
            "shoeDesc":soup.find('div', attrs={"class":"pt4-sm prl6-sm prl0-lg"}).find('p').text,
            "shoeSizeAvailability":shoeSizeAvailability,
            "shoeLink":str(link)
        }
        allSaleNikeLifestyle.append(nikeLifestyleObject)

    if (nikeLifestyleSaleCollection.count_documents({}) != 0):
        nikeLifestyleSaleCollection.delete_many({})
        nikeLifestyleSaleCollection.insert_many(allSaleNikeLifestyle)
    else:
        nikeLifestyleSaleCollection.insert_many(allSaleNikeLifestyle)

# Adidas has the issue where we cannot simply gather all data on the page by spam-scrolling down
# We must scrape subsequent pages with differing URLs
# Also, we must rely SOLELY on requests, and cannot use Selenium for Adidas at all (Selenium CANNOT pass headers in a request, meaning Adidas will block us everytime in --headless mode)
def scrape_adidas_running_sales(shoeReleaseDB, chromeOptions):
    allShoes = []
    allAdidasRunningLinks = []
    allAdidasRunningSale = []
    adidasHeader = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
    adidasRunningSaleCollection = shoeReleaseDB.adidasRunnerSales

    # Obtain JUST the first page, where we will scrape the total num of pages
    print("Getting MAIN page")
    response = requests.get("https://www.adidas.ca/en/running-shoes-outlet?start=0", headers=adidasHeader, timeout=15)
    soup = BeautifulSoup(response.content, "html.parser")
    numPages = soup.find('span', attrs={"data-auto-id":"pagination-pages-container"}).text[3:]
    print(numPages)

    # Scrape each page and compile all products
    for page in range(1, int(numPages) + 1):
        pageResponse = requests.get("https://www.adidas.ca/en/running-shoes-outlet?start=" + str(48 * int(page-1)), headers=adidasHeader, timeout=15)
        pageSoup = BeautifulSoup(pageResponse.content, "html.parser")
        allShoes += soup.find_all('div', attrs={"class":"gl-product-card color-variations__fixed-size glass-product-card___1dpKX"})
        
    # Using all products, acquire link
    for shoe in allShoes:
        shoeLink = shoe.find('a', attrs={"class":"gl-product-card__assets-link"})["href"]
        allAdidasRunningLinks.append("https://www.adidas.ca" + shoeLink)

    # Begin visiting each individual product page
    for link in allAdidasRunningLinks:
        response = requests.get(str(link), headers=adidasHeader, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")

        # Some shoes may have a placeholder value (Dynamically) - because we are using Requests, we cannot actually "wait until element has loaded"
        if ("placeholder" in str(soup.find('div', attrs={"class":"product-description___2cJO2"}).find('span', attrs={"class":True}))):
            print("SKIPPING")
            continue
        
        adidasRunnerObject = {
            "shoeName":soup.find('h1', attrs={"data-auto-id":"product-title"}).text,
            "shoeReducedPrice":soup.find('span', attrs={"class":"gl-price__value gl-price__value--sale"}).text,
            "shoeType":soup.find('div', attrs={"data-auto-id":"product-category"}).text,
            "shoeOldPrice":soup.find('span', attrs={"class":"gl-price__value gl-price__value--crossed"}).text,
            "shoeImg":soup.find("div", attrs={"class":"view___CgbJj"}).find('img')["src"],
            "shoeCW":soup.find('h5').text,
            "shoeDesc":soup.find('div', attrs={"class":"text-content___1EWJO"}).find('p').text,
            "shoeLink":str(link)
        }
        allAdidasRunningSale.append(adidasRunnerObject)
        print(len(allAdidasRunningSale))

    if (adidasRunningSaleCollection.count_documents({}) != 0):
        adidasRunningSaleCollection.delete_many({})
        adidasRunningSaleCollection.insert_many(allAdidasRunningSale)
    else:
        adidasRunningSaleCollection.insert_many(allAdidasRunningSale)

def scrape_footlocker_jordan_sales(shoeReleaseDB, chromeOptions):
    allJordans = []
    allJordanLinks = []
    allJordansOnSale = []
    footlockerHeader = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
    footlockerJordanSaleCollection = shoeReleaseDB.footlockerJordanSales
    
    print("Getting MAIN page")
    response = requests.get("https://www.footlocker.ca/en/category/sale.html?query=sale%3Arelevance%3AstyleDiscountPercent%3ASALE%3Abrand%3AJordan%3Aproducttype%3AShoes%3Agender%3AMen%27s%3Ashoestyle%3ACasual+Sneakers&sort=relevance", headers=footlockerHeader, timeout=15)
    

    soup = BeautifulSoup(response.content, "html.parser")
    numPages = soup.find('li', attrs={"class":"col col-shrink Pagination-option Pagination-option--digit"}).find('a').text

    # Scrape each page and compile all products
    for page in range(0, int(numPages)):
        # First page has no currentPage param - inputting it will break all subsequent links
        if (page == 0):
            pageResponse = requests.get("https://www.footlocker.ca/en/category/sale.html?query=sale%3Arelevance%3AstyleDiscountPercent%3ASALE%3Abrand%3AJordan%3Aproducttype%3AShoes%3Agender%3AMen%27s%3Ashoestyle%3ACasual+Sneakers&sort=relevance", headers=footlockerHeader, timeout=15)
        else:
            pageResponse = requests.get("https://www.footlocker.ca/en/category/sale.html?query=sale%3Arelevance%3AstyleDiscountPercent%3ASALE%3Abrand%3AJordan%3Aproducttype%3AShoes%3Agender%3AMen%27s%3Ashoestyle%3ACasual%2BSneakers&sort=relevance&currentPage=" + str(page), headers=footlockerHeader, timeout=15)

        pageSoup = BeautifulSoup(pageResponse.content, "html.parser")
        allJordans += soup.find_all('li', attrs={"class":"product-container col"})

    # Compile all links
    for jordan in allJordans:
        jordanLink = jordan.find('a', attrs={"class":"ProductCard-link ProductCard-content"})["href"]
        allJordanLinks.append("https://www.footlocker.ca" + str(jordanLink))

    for link in allJordanLinks:
        response = requests.get(str(link), headers=footlockerHeader, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Footlocker doesn't update their sale page regularly, so certain shoes may have been sold out, prompting us with an error page
        # If we receive this error page (Denoted by a single Heading class) then we skip the link
        # Also weirdly some shoes load a FRENCH page first, resulting in weird stuff happening when we request
        if (not soup.find('div', attrs={"class":"ProductDetails-info"}) or ("homme" in soup.find('h1', attrs={"id":"pageTitle"}).find('span').text)): #<- THIS IS BUGGED OUT FOR SOME REASON
            continue
        else:
            shoeSizeAvailability = []
            for size in soup.find('div', attrs={"class":"ProductSize-group"}).find_all('div', attrs={"class":"c-form-field c-form-field--radio ProductSize"}):
                if ("unavailable" in str(size)):
                    continue
                else:
                    shoeSizeAvailability.append(size.find('span').text if size.find('span').text[0] != '0' else size.find('span').text[1:]) # Formatting for shoe sizes such at 8.5, which are scraped as '08.5'

            shoeDescUnformatted = soup.find('div', attrs={"class":"ProductDetails-description"}).find('p').text.split('.')

            jordanShoeObject = {
                "shoeName":soup.find('h1', attrs={"id":"pageTitle"}).find('span').text,
                "shoeType":soup.find('h1', attrs={"id":"pageTitle"}).find('span', attrs={"class":"ProductName-alt"}).text,
                "shoeReducedPrice":soup.find('div', attrs={"class":"ProductPrice"}).find('span', attrs={"class":"ProductPrice-final"}).text,
                "shoeOldPrice":soup.find('div', attrs={"class":"ProductPrice"}).find('span', attrs={"class":"ProductPrice-original"}).text,
                "shoeImg":soup.find('div', attrs={"class":"AltImages"}).find('img')["src"],
                "shoeCW":soup.find('div', attrs={"class":"ProductDetails-form__info"}).find('p', attrs={"class":"ProductDetails-form__label"}).text.split('|')[0].strip(),
                "shoeDesc":shoeDescUnformatted[0] + "." + (shoeDescUnformatted[1] + "." if shoeDescUnformatted[1] != "" else ""),
                "shoeSizeAvailability":shoeSizeAvailability,
                "shoeLink":str(link)
            }
            allJordansOnSale.append(jordanShoeObject)

        if (footlockerJordanSaleCollection.count_documents({}) != 0):
            footlockerJordanSaleCollection.delete_many({})
            footlockerJordanSaleCollection.insert_many(allJordansOnSale)
        else:
            footlockerJordanSaleCollection.insert_many(allJordansOnSale)

def scrape_footlocker_adidas_runner_sales(shoeReleaseDB, chromeOptions):
    allAdidasRunners = []
    allRunnerLinks = []
    allAdidasRunnersOnSale = []
    footlockerHeader = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
    adidasRunningSaleCollection = shoeReleaseDB.adidasRunnerSales
    
    print("Getting MAIN page")
    response = requests.get("https://www.footlocker.ca/en/category/mens/adidas.html?query=Men%27s+adidas%3AtopSellers%3Agender%3AMen%27s%3Asport%3ARunning%3AstyleDiscountPercent%3ASALE", headers=footlockerHeader, timeout=15)

    soup = BeautifulSoup(response.content, "html.parser")

    if (str(soup.find('li', attrs={"class":"col col-shrink Pagination-option Pagination-option--digit"})) == "None"):
        runnersOnSale = soup.find_all('li', attrs={"class":"product-container col"})
    else:
        # DO this later
        print("There are multiple pages")

    for runner in runnersOnSale:
        runnerLink = runner.find('a', attrs={"class":"ProductCard-link ProductCard-content"})["href"]
        allRunnerLinks.append("https://www.footlocker.ca" + str(runnerLink))

    for link in allRunnerLinks:
        response = requests.get(str(link), headers=footlockerHeader, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        if (not soup.find('div', attrs={"class":"ProductDetails-info"}) or ("homme" in soup.find('h1', attrs={"id":"pageTitle"}).find('span').text)): #<- THIS IS BUGGED OUT FOR SOME REASON
            continue
        else:
            shoeSizeAvailability = []
            for size in soup.find('div', attrs={"class":"ProductSize-group"}).find_all('div', attrs={"class":"c-form-field c-form-field--radio ProductSize"}):
                if ("unavailable" in str(size)):
                    continue
                else:
                    shoeSizeAvailability.append(size.find('span').text if size.find('span').text[0] != '0' else size.find('span').text[1:]) # Formatting for shoe sizes such at 8.5, which are scraped as '08.5'

            shoeDescUnformatted = soup.find('div', attrs={"class":"ProductDetails-description"}).find('p').text.split('.')

            adidasRunnerObject = {
                "shoeName":soup.find('h1', attrs={"id":"pageTitle"}).find('span').text,
                "shoeType":soup.find('h1', attrs={"id":"pageTitle"}).find('span', attrs={"class":"ProductName-alt"}).text,
                "shoeReducedPrice":soup.find('div', attrs={"class":"ProductPrice"}).find('span', attrs={"class":"ProductPrice-final"}).text,
                "shoeOldPrice":soup.find('div', attrs={"class":"ProductPrice"}).find('span', attrs={"class":"ProductPrice-original"}).text,
                "shoeImg":soup.find('div', attrs={"class":"AltImages"}).find('img')["src"],
                "shoeCW":soup.find('div', attrs={"class":"ProductDetails-form__info"}).find('p', attrs={"class":"ProductDetails-form__label"}).text.split('|')[0].strip(),
                "shoeDesc":shoeDescUnformatted[0] + "." + (shoeDescUnformatted[1] + "." if shoeDescUnformatted[1] != "" else ""),
                "shoeSizeAvailability":shoeSizeAvailability,
                "shoeLink":str(link)
            }
            print(adidasRunnerObject)
            allAdidasRunnersOnSale.append(adidasRunnerObject)

    if (adidasRunningSaleCollection.count_documents({}) != 0):
        adidasRunningSaleCollection.delete_many({})
        adidasRunningSaleCollection.insert_many(allAdidasRunnersOnSale)
    else:
        adidasRunningSaleCollection.insert_many(allAdidasRunnersOnSale)

def main():
    # Connect to DB
    client = pymongo.MongoClient("mongodb+srv://webscraper:webscraper2193@webscraper-db.urihh.azure.mongodb.net/shoepicDB?retryWrites=true&w=majority", ssl=True,ssl_cert_reqs='CERT_NONE')
    shoeReleaseDB = client.get_database('shoepicDB')
    print("Connected!")

    # Initialize Chrome web driver for selenium 
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chromeOptions.add_argument("--headless") 
    chromeOptions.add_argument('--disable-gpu')
    chromeOptions.add_argument("--disable-dev-shm-usage")
    chromeOptions.add_argument("--no-sandbox")
    print("Initialized ChromeDrivers!")

    while True:
        #print("NIKE RUNNING SALE")
        #scrape_nike_runner_sales(shoeReleaseDB, chromeOptions)
        #time.sleep(3)
        # print("NIKE LIFESTYLE SALE")
        # scrape_nike_lifestyle_sales(shoeReleaseDB, chromeOptions)
        # time.sleep(3)
        # print("ADIDAS RUNNING SALE")
        # scrape_adidas_running_sales(shoeReleaseDB, chromeOptions) 
        # time.sleep(3)
        # print("FOOTLOCKER JORDANS SALE")
        # scrape_footlocker_jordan_sales(shoeReleaseDB, chromeOptions)
        # time.sleep(3)
        # print("FOOTLOCKER ADIDAS RUNNER SALES")
        # scrape_footlocker_adidas_runner_sales(shoeReleaseDB, chromeOptions)
        # time.sleep(3)

        #"""THE ABOVE WORKS"""       

        scrape_all_releases_footlocker(shoeReleaseDB, chromeOptions)
        time.sleep(3)

        # print("ALL SHOES")
        # scrape_all_releases_sneakerNews(shoeReleaseDB, chromeOptions)
        # time.sleep(3)
        # print("JORDANS")
        # scrape_jordan_releases_sneakerNews(shoeReleaseDB, chromeOptions)
        # time.sleep(3)
        # print("YEEZYS")
        # scrape_yeezy_releases_sneakerNews(shoeReleaseDB, chromeOptions)
        # time.sleep(3)

main()