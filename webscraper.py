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

##################################################
#                                                #
#          SNEAKERNEWS - ALL RELEASES            #
#                                                #
##################################################
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

##################################################
#                                                #
#          SNEAKERNEWS - JORDAN RELEASES         #
#                                                #
##################################################
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

##################################################
#                                                #
#          SNEAKERNEWS - YEEZY RELEASES          #
#                                                #
##################################################
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

##################################################
#                                                #
#            KICKSONFIRE - RELEASES              #
#                                                #
##################################################
def scrape_all_releases_kicksOnFire(shoeReleaseDB):
    allReleases = []
    allShoeReleasesCollection = shoeReleaseDB.shoeReleases

    print("GETTING RELEASES")
    releaseHeader = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
    response = requests.get("https://www.kicksonfire.com/app/", headers=releaseHeader, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    print(soup)
    
    allShoes = soup.find_all('div', attrs={"class":"col-xs-12 col-sm-6 col-md-4 release-date-item-continer clear-padding"})
    print(allShoes)


# WILL FIX LATER
def scrape_all_releases_footlocker(shoeReleaseDB):
    allReleases = []
    allShoeReleasesCollection = shoeReleaseDB.shoeReleases # We are not going to be using a "Line-specific" shoe DB
    footlockerHeader = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
    print("Getting RELEASES")
    response = requests.get("https://www.footlocker.ca/en/release-dates", headers=footlockerHeader, timeout=15)

    soup = BeautifulSoup(response.content, 'html.parser')

    shoeReleases = soup.find_all('div', attrs={"class":"c-release-product-wrap flex col"})
    print(len(shoeReleases))

    for shoe in shoeReleases:
        print(shoe.find('span', attrs={"class":"c-release-product-month"}).text) # Found Date
        # print(shoe.find('span', attrs={"class":"c-image"}).find('span')["src"]) # DOES NOT WORK
        print(shoe.find('p', attrs={"class":"c-prd-name"}).text) # Shoe Name
        print(shoe.find('p', attrs={"class":"c-prd-text-color"}).text) # Shoe Colourway

##################################################
#                                                #
#            NIKE.CA - RUNNING SHOES             #
#                                                #
##################################################
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
            "shoeReducedPrice":float(soup.find('div', attrs={"class":"product-price is--current-price css-s56yt7"}).text[1:]),
            "shoeOriginalPrice":float(soup.find('div', attrs={"class":"product-price css-1h0t5hy"}).text[1:]),
            "shoeImg":soup.find('source', attrs={"srcset":True})["srcset"],
            "shoeCW":soup.find('li', attrs={"class":"description-preview__color-description ncss-li"}).text[14:],
            "shoeDesc":soup.find('div', attrs={"class":"pt4-sm prl6-sm prl0-lg"}).find('p').text,
            "shoeSizeAvailability":shoeSizeAvailability,
            "shoeLink":str(link)
        }
        nikeRunnerObject["shoeDiscount"] = nikeRunnerObject["shoeReducedPrice"] / nikeRunnerObject["shoeOriginalPrice"]
        allSaleNikeRunner.append(nikeRunnerObject)
        print(nikeRunnerObject)

    if (nikeRunnerSaleCollection.count_documents({}) != 0):
        nikeRunnerSaleCollection.delete_many({})
        nikeRunnerSaleCollection.insert_many(allSaleNikeRunner)
    else:
        nikeRunnerSaleCollection.insert_many(allSaleNikeRunner)

##################################################
#                                                #
#            NIKE.CA - LIFESTYLE SHOES           #
#                                                #
##################################################
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
            "shoeOriginalPrice":soup.find('div', attrs={"class":"product-price css-1h0t5hy"}).text,
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

# WORKS FOR NOW
##################################################
#                                                #
#            ADIDAS.CA - ADIDAS RUNNERS          #
#                                                #
##################################################

# Adidas has the issue where we cannot simply gather all data on the page by spam-scrolling down
# We must scrape subsequent pages with differing URLs
# Also, we must rely SOLELY on requests, and cannot use Selenium for Adidas at all (Selenium CANNOT pass headers in a request, meaning Adidas will block us everytime in --headless mode)
def scrape_adidas_running_sales(shoeReleaseDB, chromeOptions):
    allShoes = []
    allShoesTemp = []
    allAdidasRunningLinks = []
    allAdidasRunningSale = []
    adidasHeader = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4147.105 Safari/537.36'}
    adidasRunningSaleCollection = shoeReleaseDB.adidasRunnerSales

    # Obtain JUST the first page, where we will scrape the total num of pages
    print("Getting MAIN page")
    response = requests.get("https://www.adidas.ca/en/running-shoes-outlet?start=0", headers=adidasHeader, timeout=15)
    soup = BeautifulSoup(response.content, "html.parser")
    numPages = soup.find('span', attrs={"data-auto-id":"pagination-pages-container"}).text[3:]

    # Scrape each page and compile all products
    for page in range(0, int(numPages)):
        pageResponse = requests.get("https://www.adidas.ca/en/running-shoes-outlet?start=" + str(48 * int(page)), headers=adidasHeader, timeout=15)
        pageSoup = BeautifulSoup(pageResponse.content, "html.parser").find('div', attrs={"class":"plp-grid___hCUwO"})
        allShoes += pageSoup.find_all('div', attrs={"class":"gl-product-card-container"})        # We use this array for data obtaining (This one is necessary for obtaining the correct number of products)

    print(len(allShoes))
    # Iterate through the list of all shoes, and acquire all our links
    for shoe in allShoes:
        shoeLink = shoe.find('a')["href"]
        allAdidasRunningLinks.append("https://www.adidas.ca" + shoeLink)

    # Iterate through each individual product page
    for link in allAdidasRunningLinks:
        response = requests.get(str(link), headers=adidasHeader, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")

        # Some shoes may have a placeholder value (Dynamically) - because we are using Requests, we cannot actually "wait until element has loaded"
        # WILL ADD SELENIUM SUPPORT FOR THIS
        if ("placeholder" in str(soup.find('div', attrs={"class":"product-description___2cJO2"}).find('span', attrs={"class":True}))):
            print("SKIPPING")
            continue
        
        # Isolate the product code
        formatLink = str(link).split("/")
        productCode = formatLink[len(formatLink) - 1].split(".")[0]

        # Isolate the string containing the image data for the shoe, and from it devise an array
        # The SECOND LAST element of this array has the highest-res image of the shoe
        imgString = soup.find('div', attrs={"id":"navigation-target-gallery"}).find('img')['srcset'].split()

        availability = requests.get(("https://www.adidas.ca/api/products/" + productCode + "/availability?sitePath=en"), headers=adidasHeader, timeout=15)
        print(availability.json())

        adidasRunnerObject = {
            "shoeName":soup.find('h1', attrs={"data-auto-id":"product-title"}).text,
            "shoeType":soup.find('div', attrs={"data-auto-id":"product-category"}).text.split(" ")[0],
            "shoeReducedPrice":soup.find('div', attrs={"class":"gl-price-item gl-price-item--sale notranslate"}).text[1:],
            "shoeOriginalPrice":soup.find('div', attrs={"gl-price-item gl-price-item--crossed notranslate"}).text[1:],
            "shoeImg":imgString[len(imgString)-2],               
            "shoeCW":soup.find('h5').text,
            #"shoeDesc":soup.find('div', attrs={"class":"description___2nN4A"}).find('p').text,                         # Must use Selenium (F in the chat)
            "shoeLink":str(link),
            "salePercent":""
        }
        # Obtain the sale value (Rounded to 1 decimal)
        adidasRunnerObject["salePercent"] = str(round((100 - (float(adidasRunnerObject["shoeReducedPrice"][1:]) / float(adidasRunnerObject["shoeOriginalPrice"][1:])) * 100), 1)) + "%"

        allAdidasRunningSale.append(adidasRunnerObject)
        #print(adidasRunnerObject)

    # Empty the DB and then push all new products 
    if (adidasRunningSaleCollection.count_documents({}) != 0):
        adidasRunningSaleCollection.delete_many({})
        adidasRunningSaleCollection.insert_many(allAdidasRunningSale)
    else:
        adidasRunningSaleCollection.insert_many(allAdidasRunningSale)

# WORKS FOR NOW
##################################################
#                                                #
#            FOOTLOCKER - NIKE JORDANS           #
#                                                #
##################################################
def scrape_footlocker_jordan_sales(shoeReleaseDB, chromeOptions):
    allJordans = []
    allJordanLinks = []
    allJordansOnSale = []
    footlockerHeader = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
    footlockerJordanSaleCollection = shoeReleaseDB.footlockerJordanSales
    
    print("Getting MAIN page")
    response = requests.get("https://www.footlocker.ca/en/category/sale.html?query=sale%3Arelevance%3AstyleDiscountPercent%3ASALE%3Abrand%3AJordan%3Aproducttype%3AShoes%3Agender%3AMen%27s%3Ashoestyle%3ACasual+Sneakers&sort=relevance", headers=footlockerHeader, timeout=3)

    soup = BeautifulSoup(response.content, "html.parser")
    numPages = soup.find('li', attrs={"class":"col col-shrink Pagination-option Pagination-option--digit"}).find('a').text

    # Scrape each page and compile all products
    for page in range(0, int(numPages)):
        # First page has no currentPage param - inputting it will break all subsequent links
        if (page == 0):
            pageResponse = requests.get("https://www.footlocker.ca/en/category/sale.html?query=sale%3Arelevance%3AstyleDiscountPercent%3ASALE%3Abrand%3AJordan%3Aproducttype%3AShoes%3Agender%3AMen%27s%3Ashoestyle%3ACasual+Sneakers&sort=relevance", headers=footlockerHeader, timeout=3)
        else:
            pageResponse = requests.get("https://www.footlocker.ca/en/category/sale.html?query=sale%3Arelevance%3AstyleDiscountPercent%3ASALE%3Abrand%3AJordan%3Aproducttype%3AShoes%3Agender%3AMen%27s%3Ashoestyle%3ACasual%2BSneakers&sort=relevance&currentPage=" + str(page), headers=footlockerHeader, timeout=3)

        pageSoup = BeautifulSoup(pageResponse.content, "html.parser")
        allJordans += soup.find_all('li', attrs={"class":"product-container col"})

    # Compile all links for each product
    for jordan in allJordans:
        jordanLink = jordan.find('a', attrs={"class":"ProductCard-link ProductCard-content"})["href"]
        allJordanLinks.append("https://www.footlocker.ca" + str(jordanLink))

    # Iterate through each product page, creating an object 
    for link in allJordanLinks:
        response = requests.get(str(link), headers=footlockerHeader, timeout=3)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Footlocker doesn't update their sale page regularly, so certain shoes may have been sold out, prompting us with an error page
        # If we receive this error page (Denoted by a single Heading class) then we skip the link
        if (soup.find('div', attrs={"class":"Page-wrapper Page--large Page--productNotFound"})): 
            print("Empty product page") # TESTING
            continue

        # If there is a product available, we acquire all available sizes and the shoe's description
        else:
            shoeSizeAvailability = []
            for size in soup.find('div', attrs={"class":"ProductSize-group"}).find_all('div', attrs={"class":"c-form-field c-form-field--radio ProductSize"}):
                if ("unavailable" in str(size)):
                    continue
                else:
                    shoeSizeAvailability.append(size.find('span').text if size.find('span').text[0] != '0' else size.find('span').text[1:]) # Formatting for shoe sizes such at 8.5, which are scraped as '08.5'

            shoeDescUnformatted = soup.find('div', attrs={"class":"ProductDetails-description"}).find('p').text.split('.')

            # Create the shoe object with corresponding entries about its information
            jordanShoeObject = {
                "shoeName":soup.find('h1', attrs={"id":"pageTitle"}).find('span').text,
                "shoeType":soup.find('h1', attrs={"id":"pageTitle"}).find('span', attrs={"class":"ProductName-alt"}).text,
                "shoeReducedPrice":soup.find('div', attrs={"class":"ProductPrice"}).find('span', attrs={"class":"ProductPrice-final"}).text,
                "shoeOriginalPrice":soup.find('div', attrs={"class":"ProductPrice"}).find('span', attrs={"class":"ProductPrice-original"}).text,
                #"shoeImg":soup.find('div', attrs={"class":"AltImages"}).find('img')["src"], Footlocker screwed us :(
                "shoeCW":soup.find('div', attrs={"class":"ProductDetails-form__info"}).find('p', attrs={"class":"ProductDetails-form__label"}).text.split('|')[0].strip(),
                "shoeDesc":shoeDescUnformatted[0] + "." + (shoeDescUnformatted[1] + "." if shoeDescUnformatted[1] != "" else ""),
                "shoeSizeAvailability":shoeSizeAvailability,
                "shoeLink":str(link),
                "salePercent":"",
            }
            # Obtain the sale value (Rounded to 1 decimal)
            jordanShoeObject["salePercent"] = str(round((100 - (float(jordanShoeObject["shoeReducedPrice"][1:]) / float(jordanShoeObject["shoeOriginalPrice"][1:])) * 100), 1)) + "%"
            allJordansOnSale.append(jordanShoeObject)
            print(jordanShoeObject) # TESTING

        # Wipe the DB and fill with all newly scraped products 
        if (footlockerJordanSaleCollection.count_documents({}) != 0):
            footlockerJordanSaleCollection.delete_many({})
            footlockerJordanSaleCollection.insert_many(allJordansOnSale)
        else:
            footlockerJordanSaleCollection.insert_many(allJordansOnSale)

# WORKS FOR NOW
##################################################
#                                                #
#          FOOTLOCKER - ADIDAS RUNNERS           #
#                                                #
##################################################

def scrape_footlocker_adidas_runner_sales(shoeReleaseDB, chromeOptions):
    allAdidasRunners = []
    allRunnerLinks = []
    allAdidasRunnersOnSale = []
    runnersOnSale = []

    # Create header for Selenium browser (makes us look human)
    footlockerHeader = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

    # Specify the collection we wish to access in the DB
    adidasRunningSaleCollection = shoeReleaseDB.adidasRunnerSales
    
    # Obtain the main page (Used to create an array of links for each shoe object on the page) and the number of pages
    response = requests.get("https://www.footlocker.ca/en/category/mens/adidas.html?query=Men%27s+adidas%3AtopSellers%3Agender%3AMen%27s%3Asport%3ARunning%3AstyleDiscountPercent%3ASALE", headers=footlockerHeader, timeout=15)
    soup = BeautifulSoup(response.content, "html.parser")
    numPages = soup.find('li', attrs={"class":"col col-shrink Pagination-option Pagination-option--digit"}).find('a').text
    print("Number of Pages " + numPages)

    # Scrape each page and compile all products
    for page in range(0, int(numPages)):
        # First page has no currentPage param - inputting it will break all subsequent links
        if (page == 0):
            pageResponse = requests.get("https://www.footlocker.ca/en/category/mens/adidas.html?query=Men%27s+adidas%3AtopSellers%3Agender%3AMen%27s%3Asport%3ARunning%3AstyleDiscountPercent%3ASALE", headers=footlockerHeader, timeout=3)
        else:
            pageResponse = requests.get("https://www.footlocker.ca/en/category/mens/adidas.html?query=Men%27s+adidas%3AtopSellers%3Agender%3AMen%27s%3Asport%3ARunning%3AstyleDiscountPercent%3ASALE&currentPage=" + str(page), headers=footlockerHeader, timeout=3)

        pageSoup = BeautifulSoup(pageResponse.content, "html.parser")
        runnersOnSale += soup.find_all('li', attrs={"class":"product-container col"})

    # Fill the links array with each product page
    for runner in runnersOnSale:
        runnerLink = runner.find('a', attrs={"class":"ProductCard-link ProductCard-content"})["href"]
        allRunnerLinks.append("https://www.footlocker.ca" + str(runnerLink))

    # Parse each page individually with BS4 - TO BE CHANGED TO SELENIUM LATER
    for link in allRunnerLinks:
        response = requests.get(str(link), headers=footlockerHeader, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Ensure that the product is actually there (Doesn't redirect to Footlocker's default error page)
        if (soup.find('div', attrs={"class":"Page-wrapper Page--large Page--productNotFound"})): 
            print("Empty product page") # TESTING
            continue
        else:

            # Obtain all available sizes for the product
            shoeSizeAvailability = []
            for size in soup.find('div', attrs={"class":"ProductSize-group"}).find_all('div', attrs={"class":"c-form-field c-form-field--radio ProductSize"}):
                if ("unavailable" in str(size)):
                    continue
                else:
                    shoeSizeAvailability.append(size.find('span').text if size.find('span').text[0] != '0' else size.find('span').text[1:]) # Formatting for shoe sizes such at 8.5, which are scraped as '08.5'

            # Obtain the shoe's description
            shoeDescUnformatted = soup.find('div', attrs={"class":"ProductDetails-description"}).find('p').text.split('.')

            # Create the shoe object with all corresponding properties
            adidasRunnerObject = {
                "shoeName":soup.find('h1', attrs={"id":"pageTitle"}).find('span').text,
                "shoeType":soup.find('h1', attrs={"id":"pageTitle"}).find('span', attrs={"class":"ProductName-alt"}).text,
                "shoeReducedPrice":soup.find('div', attrs={"class":"ProductPrice"}).find('span', attrs={"class":"ProductPrice-final"}).text,
                "shoeOriginalPrice":soup.find('div', attrs={"class":"ProductPrice"}).find('span', attrs={"class":"ProductPrice-original"}).text,
                #"shoeImg":soup.find('div', attrs={"class":"ProductDetails-image"}).find('div', attrs={"class":"AltImages"}),   Footlocker screwed me, and so images will now not work without Selenium (WILL FIX LATER)
                "shoeCW":soup.find('div', attrs={"class":"ProductDetails-form__info"}).find('p', attrs={"class":"ProductDetails-form__label"}).text.split('|')[0].strip(),
                "shoeDesc":shoeDescUnformatted[0] + "." + (shoeDescUnformatted[1] + "." if shoeDescUnformatted[1] != "" else ""),
                "shoeSizeAvailability":shoeSizeAvailability,
                "shoeLink":str(link),
                "salePercent":"",
            }
            # Obtain the sale value (Rounded to 1 decimal)
            adidasRunnerObject["salePercent"] = str(round((100 - (float(adidasRunnerObject["shoeReducedPrice"][1:]) / float(adidasRunnerObject["shoeOriginalPrice"][1:])) * 100), 1)) + "%"
            print(adidasRunnerObject) 

            allAdidasRunnersOnSale.append(adidasRunnerObject)

    # Clear the current entries in the DB, and proceed to fill it with the new entries
    if (adidasRunningSaleCollection.count_documents({}) != 0):
        adidasRunningSaleCollection.delete_many({})
        adidasRunningSaleCollection.insert_many(allAdidasRunnersOnSale)
    else:
        adidasRunningSaleCollection.insert_many(allAdidasRunnersOnSale)


# NOT FINISHED (MUST ADD TO DB)
##################################################
#                                                #
#               RUNNING ROOM - NIKE              #
#                                                #
##################################################
def scrape_runningRoom_nike_runner_sales(shoeReleaseDB, chromeOptions):

    # Initialize the driver and scrape site
    #driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chromeOptions) # FOR PRODUCTION
    driver = webdriver.Chrome(options=chromeOptions, executable_path='./chromedriver') # FOR LOCAL ONLY
    driver.get("https://ca.shop.runningroom.com/en_ca/sale-1/shoes.html#?profile_id=5a6d1b7d25e905d046cd87722be40a94&session_id=3a91a736-ffb0-11ea-b859-0242ac110003&Category0=Sale&Category1=Shoes&search_return=all&Brand=Nike")
    time.sleep(2)
    body = driver.find_element_by_tag_name("body")
    response = driver.page_source
    driver.quit()

    # Parse the response obtained from the Selenium loaded page, and create a list of all products on the page
    soup = BeautifulSoup(response, "html.parser")
    runningSales = soup.find_all('li', attrs={"class":"item product product-item"})

    # Create each running shoe object with specified fields
    for shoe in runningSales:
        nikeRunnerObject = {
            "shoeName":shoe.find('h2', attrs={"class":"product-name"}).find('a').text,
            "shoeImg":shoe.find("img", attrs={"class":"product-image-photo"})["src"],
            "shoeType":"Running",
            "shoeReducedPrice":shoe.find("span", attrs={"class":"price"}).text.split("CAD")[0].strip(),
            "shoeOriginalPrice":shoe.find("span", attrs={"class":"price"}).text.split("CAD")[1].strip(),
            "shoeLink":shoe.find('h2', attrs={"class":"product-name"}).find('a')["href"],
            "salePercent":""
        }

        # Obtain the sale value (Rounded to one decimal place)
        nikeRunnerObject["salePercent"] = str(round((100 - (float(nikeRunnerObject["shoeReducedPrice"][1:]) / float(nikeRunnerObject["shoeOriginalPrice"][1:])) * 100), 1)) + "%"
        print(nikeRunnerObject)


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
        # print("NIKE RUNNING SALE @ RUNNINGROOM")
        # scrape_runningRoom_nike_runner_sales(shoeReleaseDB, chromeOptions)
        # time.sleep(3);
        #print("NIKE LIFESTYLE SALE")
        #scrape_nike_lifestyle_sales(shoeReleaseDB, chromeOptions)
        #time.sleep(3)
        print("ADIDAS RUNNING SALE")
        scrape_adidas_running_sales(shoeReleaseDB, chromeOptions) 
        time.sleep(3)
        # print("FOOTLOCKER JORDANS SALE")
        # scrape_footlocker_jordan_sales(shoeReleaseDB, chromeOptions)
        # time.sleep(3)
        # print("FOOTLOCKER ADIDAS RUNNER SALES")
        # scrape_footlocker_adidas_runner_sales(shoeReleaseDB, chromeOptions)
        # time.sleep(3)

        
        #scrape_all_releases_redFlagDeals(shoeReleaseDB)
        #time.sleep(5)
        
        #"""THE ABOVE WORKS"""       

        #scrape_all_releases_footlocker(shoeReleaseDB)
        #time.sleep(3)

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