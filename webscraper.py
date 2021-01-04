import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, abort
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import time
import os
import asyncio

import socket

import pymongo
from pymongo import MongoClient
import dns
from bson import BSON
from bson import json_util
from bson.json_util import dumps
import json

##################################################
#                                                #
#            GLOBAL HEADERS (requests)           #
#                                                #
##################################################

ADIDAS_HEADER = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4147.105 Safari/537.36'}
FOOTLOCKER_HEADER = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4147.105 Safari/537.36'}
RELEASE_HEADER = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}

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
    response = requests.get("https://www.kicksonfire.com/app/", headers=RELEASE_HEADER, timeout=15)
    soup = BeautifulSoup(response.content, 'html.parser')
    print(soup)
    
    allShoes = soup.find_all('div', attrs={"class":"col-xs-12 col-sm-6 col-md-4 release-date-item-continer clear-padding"})
    print(allShoes)


# WILL FIX LATER
def scrape_all_releases_footlocker(shoeReleaseDB):
    allReleases = []
    allShoeReleasesCollection = shoeReleaseDB.shoeReleases # We are not going to be using a "Line-specific" shoe DB
    
    print("Getting RELEASES")
    response = requests.get("https://www.footlocker.ca/en/release-dates", headers=FOOTLOCKER_HEADER, timeout=15)

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
#                 NIKE.CA - GENERAL              # 
#                                                #
##################################################
def scrape_nike_sales(shoeReleaseDB, chromeOptions, prodType):
    allProductsOnSale = []
    productLinks = []

    if (prodType == "SB"):
        mainLink = "https://www.nike.com/ca/w/sale-skateboarding-shoes-3yaepz8mfrfzy7ok"
        dbCollection = shoeReleaseDB.nikeLifestyleSales
        dbFilter = {"shoeName":{"$regex":"SB"}, "shoeLink":{"$regex":"nike.com"}}

    elif (prodType == "lifestyle"):
        mainLink = "https://www.nike.com/ca/w/sale-lifestyle-shoes-13jrmz3yaepzy7ok"
        dbCollection = shoeReleaseDB.nikeLifestyleSales
        dbFilter = {"shoeName":{"$ne":{"$regex":"SB"}}, "shoeLink":{"$regex":"nike.com"}}
    
    elif (prodType == "jordan"):
        mainLink = "https://www.nike.com/ca/w/sale-jordan-shoes-37eefz3yaepzy7ok"
        dbCollection = shoeReleaseDB.jordanSales
        dbFilter = {"shoeLink":{"$regex":"nike.com"}}

    elif (prodType == "running"):
        mainLink = "https://www.nike.com/ca/w/sale-running-shoes-37v7jz3yaepzy7ok"
        dbCollection = shoeReleaseDB.nikeRunnerSales
        dbFilter = {"shoeLink":{"$regex":"nike.com"}}

    #driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chromeOptions)
    driver = webdriver.Chrome(options=chromeOptions, executable_path='./chromedriver') # FOR LOCAL ONLY
    driver.get(mainLink)
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

    availProducts = soup.find_all('div', attrs={"class":"product-card__body"})
    
    # Compile Links
    for product in availProducts:
        productLink = str(product.find('a', attrs={"class":"product-card__img-link-overlay"})["href"])
        productLinks.append(productLink)
        print(productLink)

    # Update the current time at which availability was checked
    curTime = datetime.now()

    for link in productLinks:
        driver = webdriver.Chrome(options=chromeOptions, executable_path='./chromedriver') # FOR LOCAL ONLY
        #driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chromeOptions)
        driver.get(link)
        time.sleep(0.5)

        response = driver.page_source
        driver.quit()
        soup = BeautifulSoup(response, "html.parser")

        # Checks if there is a valid size array (This will omit BY YOU products / other custom products)
        if (not soup.find('fieldset', attrs={"class":"mt5-sm mb3-sm body-2 css-1pj6y87"})):
            print("\nINVALID PRODUCT - SKIPPING\n")
            continue

        # Scrape all available sizes, strip tags and place the data into an array - ALSO ignore sizes that are "greyed out"
        else:
            print("VALID PRODUCT")
            shoeSizeAvailability = []
            sizeData = soup.find('fieldset', attrs={"class":"mt5-sm mb3-sm body-2 css-1pj6y87"}).find_all('div', attrs={"class":False})
            for size in sizeData:
                if ("disabled" in str(size)):
                    continue
                else:
                    availableSize = size.find("label").text
                    shoeSizeAvailability.append(str(size.get_text()))   

            nikeObject = {
                "shoeName":soup.find('div', attrs={"class":"pr2-sm css-1ou6bb2"}).find('h1', attrs={"class":"headline-2 css-zis9ta"}).text,
                "shoeType":soup.find('div', attrs={"class":"pr2-sm css-1ou6bb2"}).find('h2', attrs={"class":"headline-5-small pb1-sm d-sm-ib css-1ppcdci"}).text,
                "shoeReducedPrice":float(soup.find('div', attrs={"class":"product-price is--current-price css-s56yt7"}).text[1:]),
                "shoeOriginalPrice":float(soup.find('div', attrs={"class":"product-price css-1h0t5hy"}).text[1:]),
                "shoeImg":soup.find('source', attrs={"srcset":True})["srcset"],
                "shoeCW":soup.find('li', attrs={"class":"description-preview__color-description ncss-li"}).text[14:],
                "shoeDesc":soup.find('div', attrs={"class":"pt4-sm prl6-sm prl0-lg"}).find('p').text,
                "shoeSizeAvailability":shoeSizeAvailability,
                "shoeLink":str(link),
                "lastUpdated":curTime.strftime("%H:%M:%S, %m/%d/%Y")
            }
            # Obtain the sale value (Rounded to 1 decimal)
            nikeObject["salePercent"] = str(round((100 - ((nikeObject["shoeReducedPrice"]) / (nikeObject["shoeOriginalPrice"])) * 100), 1)) + "%"
            allProductsOnSale.append(nikeObject)
            print(nikeObject)

    # Only delete documents that are from nike.ca
    if (dbCollection.count_documents({}) != 0):
        dbCollection.delete_many(dbFilter)
        dbCollection.insert_many(allProductsOnSale)
    else:
        dbCollection.insert_many(allProductsOnSale)

# WORKS FOR NOW
##################################################
#                                                #
#                ADIDAS.CA - GENERAL             #
#                                                #
##################################################
def scrape_adidas_sales(shoeReleaseDB, chromeOptions, prodType):
    availProducts = []
    allProductLinks = []
    allAdidasProdOnSale = []

    if (prodType == "originals"):
        mainLink = "https://www.adidas.ca/en/originals-shoes-outlet?start=0"
        dbCollection = shoeReleaseDB.adidasOriginalsSales
        dbFilter = {"shoeLink":{"$regex":"adidas.ca"}}
    
    elif (prodType == "running"):
        mainLink = "https://www.adidas.ca/en/running-shoes-outlet?start=0"
        dbCollection = shoeReleaseDB.adidasRunnerSales
        dbFilter = {"shoeLink":{"$regex":"adidas.ca"}}

    elif (prodType == "tiro"):
        mainLink = "https://www.adidas.ca/en/tiro-clothing-outlet?start=0"
        dbCollection = shoeReleaseDB.adidasTiroSales
        dbFilter = {"shoeLink":{"$regex":"adidas.ca"}}
    

    # Obtain JUST the first page, where we will scrape the total num of pages
    print("Getting MAIN page")
    response = requests.get(mainLink, headers=ADIDAS_HEADER, timeout=15)
    soup = BeautifulSoup(response.content, "html.parser")

    # If the span containing the page numbers is present (THERE IS MORE THAN ONE PAGE)
    if (soup.find('span', attrs={"data-auto-id":"pagination-pages-container"})):
        numPages = soup.find('span', attrs={"data-auto-id":"pagination-pages-container"}).text[3:]

        # Scrape each page and compile all products
        for page in range(0, int(numPages)):
            pageResponse = requests.get(mainLink[0:len(mainLink)-1]+ str(48 * int(page)), headers=ADIDAS_HEADER, timeout=15)
            pageSoup = BeautifulSoup(pageResponse.content, "html.parser").find('div', attrs={"class":"plp-grid___hCUwO"})
            availProducts += pageSoup.find_all('div', attrs={"class":"gl-product-card-container"})        # We use this array for data obtaining (This one is necessary for obtaining the correct number of products)

    # If there is only one page
    else: 
        availProducts += soup.find_all('div', attrs={"class":"gl-product-card-container"})  

    #Iterate through the list of all shoes, and acquire all our links
    for product in availProducts:
        productLink = str(product.find('a')["href"])
        allProductLinks.append("https://www.adidas.ca" + productLink)

    # Update the current time at which availability was checked
    curTime = datetime.now()

    # Iterate through each individual product page
    for link in allProductLinks:
        response = requests.get(str(link), headers=ADIDAS_HEADER, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")

        # Some shoes may have a placeholder value (Dynamically) - because we are using Requests, we cannot actually "wait until element has loaded"
        # WILL ADD SELENIUM SUPPORT FOR THIS
        if ("placeholder" in str(soup.find('div', attrs={"class":"product-description___2cJO2"}).find('span', attrs={"class":True}))):
            print("SKIPPING")
            continue
        
        # Isolate the product code
        productCode = get_prod_code(link)

        # Isolate the string containing the image data for the shoe, and from it devise an array
        # The SECOND LAST element of this array has the highest-res image of the shoe
        imgString = soup.find('div', attrs={"id":"navigation-target-gallery"}).find('img')['srcset'].split()

        # Make call to Adidas API for size availability (the link is the following, with the product code inserted)
        allAvailSizes = []
        availability = requests.get(("https://www.adidas.ca/api/products/" + productCode + "/availability?sitePath=en"), headers=ADIDAS_HEADER, timeout=15)
        sizesArr = availability.json()["variation_list"]

        # For each size, check if the product is in stock, and add it to our list of available sizes if so
        for size in sizesArr:
            if (size['availability_status'] == 'IN_STOCK'):
                print(size)
                allAvailSizes.append(size['size'])

        # FINAL PRODUCT CHECKS
        # - Are there any available sizes
        # - Is the product actually on sale (Occassional glitch)
        if ((len(allAvailSizes) == 0) or (not soup.find('div', attrs={"class":"gl-price-item gl-price-item--sale notranslate"}))):
            print("INVALID PRODUCT - SKIPPING")
            continue

        # If a product passes all of the above checks, only then do we add it to our list
        else: 

            adidasProdObject = {
                "prodName":soup.find('h1', attrs={"data-auto-id":"product-title"}).text,
                "prodType":soup.find('div', attrs={"data-auto-id":"product-category"}).text.split(" ")[0],
                "prodReducedPrice":soup.find('div', attrs={"class":"gl-price-item gl-price-item--sale notranslate"}).text[1:],
                "prodOriginalPrice":soup.find('div', attrs={"gl-price-item gl-price-item--crossed notranslate"}).text[1:],
                "prodImg":imgString[len(imgString)-2],               
                "prodCW":soup.find('h5').text,          
                "prodSizeAvailability":allAvailSizes,           
                "prodLink":str(link),
                "lastUpdated":curTime.strftime("%H:%M:%S, %m/%d/%Y")
            }
            # Obtain the sale value (Rounded to 1 decimal)
            adidasProdObject["salePercent"] = str(round((100 - (float(adidasProdObject["prodReducedPrice"][1:]) / float(adidasProdObject["prodOriginalPrice"][1:])) * 100), 1)) + "%"

            allAdidasProdOnSale.append(adidasProdObject)
            print(adidasProdObject)

    # Empty the DB and then push all new products 
    if (dbCollection.count_documents({}) != 0):
        dbCollection.delete_many({})
        dbCollection.insert_many(allAdidasProdOnSale)
    else:
        dbCollection.insert_many(allAdidasProdOnSale)


# WORKS FOR NOW
##################################################
#                                                #
#           FOOTLOCKER - NIKE LIFESTYLE          #
#    parameterized for gender search (M/W/K)     #
# Prevents crashing due to large num of products #
##################################################
def scrape_footlocker_nike_lifestyle_sales(shoeReleaseDB, chromeOptions, genderParam):
    allNikeLifestyle = []
    allNikeLinks = []
    allNikeLifestyleOnSale = []    
    nikeLifestyleSaleCollection = shoeReleaseDB.nikeLifestyleSales

    if (genderParam == "Kids"):
        mainLink = "https://www.footlocker.ca/en/category/sale.html?query=sale%3AtopSellers%3Abrand%3ANike%3Aproducttype%3AShoes%3Asport%3ACasual%3Ashoestyle%3ACasual%2BSneakers%3Aage%3AGrade%2BSchool&sort=relevance&currentPage=0"
    else:
        mainLink = "https://www.footlocker.ca/en/category/sale.html?query=sale%3AtopSellers%3Abrand%3ANike%3Aproducttype%3AShoes%3Asport%3ACasual%3Ashoestyle%3ACasual%2BSneakers%3Agender%3A"  + str(genderParam) + "%27s&sort=relevance&currentPage=0"

    
    print("Getting MAIN page")
    response = requests.get(mainLink, headers=FOOTLOCKER_HEADER, timeout=15)

    soup = BeautifulSoup(response.content, "html.parser")
    numPages = soup.find('li', attrs={"class":"col col-shrink Pagination-option Pagination-option--digit"}).find('a').text

    # Scrape each page and compile all products
    for page in range(0, int(numPages)):
        # First page has no currentPage param - inputting it will break all subsequent links
        if (page == 0):
            pageResponse = requests.get(mainLink, headers=FOOTLOCKER_HEADER, timeout=15)
        else:
            pageResponse = requests.get(mainLink[0:len(mainLink)] + str(page), headers=FOOTLOCKER_HEADER, timeout=15)

        pageSoup = BeautifulSoup(pageResponse.content, "html.parser")
        allNikeLifestyle += soup.find_all('li', attrs={"class":"product-container col"})

    # Compile all links for each product
    for shoe in allNikeLifestyle:
        nikeLink = shoe.find('a', attrs={"class":"ProductCard-link ProductCard-content"})["href"]
        allNikeLinks.append("https://www.footlocker.ca" + str(nikeLink))

    # Update the current time at which availability was checked
    curTime = datetime.now()

    # Iterate through each product page, creating an object 
    for link in allNikeLinks:
        response = requests.get(str(link), headers=FOOTLOCKER_HEADER, timeout=3)
        soup = BeautifulSoup(response.content, 'html.parser')
        #time.sleep(1)   # This prevents a read time-out error
        
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

            # DESCRIPTION FORMATTING
            # Find the description and all features (stored in a <li>)
            shoeDescFormatted = ""
            shoeDescUnformatted = soup.find('div', attrs={"class":"ProductDetails-description"}).find_all('p')
            shoeDescList = soup.find('div', attrs={"class":"ProductDetails-description"}).find_all('li')
            #print(shoeDescList)
            
            # Format our description string (With the main paragraphs, and then subpoints all appended together into one string)
            for i in range(0, len(shoeDescUnformatted)):
                shoeDescFormatted += shoeDescUnformatted[i].text
            shoeDescFormatted += "\n"
            for i in range(0, len(shoeDescList)):
                shoeDescFormatted += "- " + str(shoeDescList[i].text) + "\n"

            # Create the shoe object with corresponding entries about its information
            nikeLifestyleShoeObject = {
                "shoeName":soup.find('h1', attrs={"id":"pageTitle"}).find('span').text,
                "shoeType":soup.find('h1', attrs={"id":"pageTitle"}).find('span', attrs={"class":"ProductName-alt"}).text,
                "shoeReducedPrice":soup.find('div', attrs={"class":"ProductPrice"}).find('span', attrs={"class":"ProductPrice-final"}).text,
                "shoeOriginalPrice":soup.find('div', attrs={"class":"ProductPrice"}).find('span', attrs={"class":"ProductPrice-original"}).text,
                #"shoeImg":soup.find('div', attrs={"class":"AltImages"}).find('img')["src"], Footlocker screwed us :(
                "shoeCW":soup.find('div', attrs={"class":"ProductDetails-form__info"}).find('p', attrs={"class":"ProductDetails-form__label"}).text.split('|')[0].strip(),
                "shoeDesc":shoeDescFormatted,
                "shoeSizeAvailability":shoeSizeAvailability,
                "shoeLink":str(link),
                "lastUpdated":curTime.strftime("%H:%M:%S, %m/%d/%Y")
            }
            # Obtain the sale value (Rounded to 1 decimal)
            nikeLifestyleShoeObject["salePercent"] = str(round((100 - (float(nikeLifestyleShoeObject["shoeReducedPrice"][1:]) / float(nikeLifestyleShoeObject["shoeOriginalPrice"][1:])) * 100), 1)) + "%"
            allNikeLifestyleOnSale.append(nikeLifestyleShoeObject)
            print(nikeLifestyleShoeObject) # TESTING

    # Wipe all DB entries from Footlocker that have "Grade" in the name (For grade-school kid sizes)
    if (genderParam == "Kids"):
        if (nikeLifestyleSaleCollection.count_documents({}) != 0):
            nikeLifestyleSaleCollection.delete_many({"shoeLink":{"$regex":"footlocker.ca"}, "shoeName":{"$regex":"Grade"}})
            nikeLifestyleSaleCollection.insert_many(allNikeLifestyleOnSale)
        else:
            nikeLifestyleSaleCollection.insert_many(allNikeLifestyleOnSale)
    
    # Wipe all DB entries from Footlocker that have Women's as their type
    elif (genderParam == "Women"): 
        if (nikeLifestyleSaleCollection.count_documents({}) != 0):
            nikeLifestyleSaleCollection.delete_many({"shoeLink":{"$regex":"footlocker.ca"}, "shoeType":{"$regex":"Women's"}})
            nikeLifestyleSaleCollection.insert_many(allNikeLifestyleOnSale)
        else:
            nikeLifestyleSaleCollection.insert_many(allNikeLifestyleOnSale)

    # Wipe all DB entries from Footlocker that have Men's as their type        
    else:
        if (nikeLifestyleSaleCollection.count_documents({}) != 0):
            nikeLifestyleSaleCollection.delete_many({"shoeLink":{"$regex":"footlocker.ca"}, "shoeType":{"$regex":"Men's"}})
            nikeLifestyleSaleCollection.insert_many(allNikeLifestyleOnSale)
        else:
            nikeLifestyleSaleCollection.insert_many(allNikeLifestyleOnSale)


# WORKS FOR NOW
##################################################
#                                                #
#               FOOTLOCKER - GENERAL             #
#                                                #
##################################################
def scrape_footlocker_sales(shoeReleaseDB, chromeOptions, prodType):
    allProductLinks = []
    allProductsOnSale = []
    availProducts = []

    # Specify the collection we wish to access in the DB
    if (prodType == "ao"):
        mainLink = "https://www.footlocker.ca/en/category/sale.html?query=sale%3Arelevance%3Aproducttype%3AShoes%3Abrand%3Aadidas+Originals%3Asport%3ACasual%3Ashoestyle%3ACasual+Sneakers&sort=relevance&currentPage=0"
        dbCollection = shoeReleaseDB.adidasOriginalsSales
        dbFilter = {"shoeLink":{"$regex":"footlocker.ca"}}
    
    elif (prodType == "ar"):
        mainLink = "https://www.footlocker.ca/en/category/sale.html?query=sale%3AtopSellers%3Aproducttype%3AShoes%3Asport%3ARunning%3Abrand%3Aadidas%2BOriginals%3Abrand%3Aadidas&sort=relevance&currentPage=0"
        dbCollection = shoeReleaseDB.adidasRunnerSales
        dbFilter = {"shoeLink":{"$regex":"footlocker.ca"}}
    
    elif (prodType == "nj"):
        mainLink = "https://www.footlocker.ca/en/category/sale.html?query=sale%3Arelevance%3AstyleDiscountPercent%3ASALE%3Abrand%3AJordan%3Aproducttype%3AShoes%3Agender%3AMen%27s%3Ashoestyle%3ACasual%2BSneakers&sort=relevance&currentPage=0"
        dbCollection = shoeReleaseDB.jordanSales
        dbFilter = {"shoeLink":{"$regex":"footlocker.ca"}}
    
    
    # Obtain the main page (Used to create an array of links for each shoe object on the page) and the number of pages
    response = requests.get(mainLink, headers=FOOTLOCKER_HEADER, timeout=15)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find ALL digits at the bottom (for page nav) and isolate the LAST ONE in the list
    pageDigits = soup.find_all('li', attrs={"class":"col col-shrink Pagination-option Pagination-option--digit"})
    numPages = pageDigits[len(pageDigits)-1].find('a').text
    print("Number of Pages " + numPages)

    # Scrape each page and compile all products
    for page in range(0, int(numPages)):
        # First page has no currentPage param - inputting it will break all subsequent links
        if (page == 0):
            pageResponse = requests.get(mainLink, headers=FOOTLOCKER_HEADER, timeout=15)
        else:
            pageResponse = requests.get(mainLink[0:len(mainLink)-1] + str(page), headers=FOOTLOCKER_HEADER, timeout=15)

        pageSoup = BeautifulSoup(pageResponse.content, "html.parser")
        availProducts += soup.find_all('li', attrs={"class":"product-container col"})

    # Fill the links array with each product page
    for product in availProducts:
        productLink = product.find('a', attrs={"class":"ProductCard-link ProductCard-content"})["href"]
        allProductLinks.append("https://www.footlocker.ca" + str(productLink))

    # Update the current time at which availability was checked
    curTime = datetime.now()

    # Parse each page individually with BS4
    for link in allProductLinks:
        response = requests.get(str(link), headers=FOOTLOCKER_HEADER, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Ensure that the product is actually there (Doesn't redirect to Footlocker's default error page)
        if (soup.find('div', attrs={"class":"Page-wrapper Page--large Page--productNotFound"})): 
            print("Empty product page") # TESTING
            continue
        else:
            try:
                # Obtain all available sizes for the product
                shoeSizeAvailability = []
                for size in soup.find('div', attrs={"class":"ProductSize-group"}).find_all('div', attrs={"class":"c-form-field c-form-field--radio ProductSize"}):
                    # Sold out size
                    if ("unavailable" in str(size)):
                        continue

                    else:
                        shoeSizeAvailability.append(size.find('span').text if size.find('span').text[0] != '0' else size.find('span').text[1:]) # Formatting for shoe sizes such at 8.5, which are scraped as '08.5'

                # DESCRIPTION FORMATTING
                # Find the description and all features (stored in a <li>)
                shoeDescFormatted = ""
                shoeDescUnformatted = soup.find('div', attrs={"class":"ProductDetails-description"}).find_all('p')
                shoeDescList = soup.find('div', attrs={"class":"ProductDetails-description"}).find_all('li')
                
                # Format our description string (With the main paragraphs, and then subpoints all appended together into one string)
                for i in range(0, len(shoeDescUnformatted)):
                    shoeDescFormatted += shoeDescUnformatted[i].text
                shoeDescFormatted += "\n"
                for i in range(0, len(shoeDescList)):
                    shoeDescFormatted += "- " + str(shoeDescList[i].text) + "\n"

                # Same strategy as the Adidas scraper - call Footlocker's API directly and pass in the product code as a parameter
                prodCode = get_prod_code(link)

                # Create the shoe object with all corresponding properties
                shoeObject = {
                    "prodName":soup.find('h1', attrs={"id":"pageTitle"}).find('span').text,
                    "prodType":soup.find('h1', attrs={"id":"pageTitle"}).find('span', attrs={"class":"ProductName-alt"}).text,
                    "prodReducedPrice":soup.find('div', attrs={"class":"ProductPrice"}).find('span', attrs={"class":"ProductPrice-final"}).text,
                    "prodOriginalPrice":soup.find('div', attrs={"class":"ProductPrice"}).find('span', attrs={"class":"ProductPrice-original"}).text,
                    "prodImg":"https://images.footlocker.com/is/image/EBFL2/" + str(prodCode) + "_a1?wid=600&hei=600&fmt=png-alpha",
                    "prodCW":soup.find('div', attrs={"class":"ProductDetails-form__info"}).find('p', attrs={"class":"ProductDetails-form__label"}).text.split('|')[0].strip(),
                    "prodDesc":shoeDescFormatted,
                    "prodSizeAvailability":shoeSizeAvailability,
                    "prodLink":str(link),
                    "lastUpdated":curTime.strftime("%H:%M:%S, %m/%d/%Y")
                }
                # Obtain the sale value (Rounded to 1 decimal)
                shoeObject["salePercent"] = str(round((100 - (float(shoeObject["prodReducedPrice"][1:]) / float(shoeObject["prodOriginalPrice"][1:])) * 100), 1)) + "%"
                print(shoeObject) 

                allProductsOnSale.append(shoeObject)

            except:
                print("PROBLEM WITH PRODUCT LOADING - SKIPPING")
                continue

    # Clear the current entries in the DB (if they're from footlocker), and proceed to fill it with the new entries
    if (dbCollection.count_documents({}) != 0):
        dbCollection.delete_many(dbFilter)
        dbCollection.insert_many(allProductsOnSale)
    else:
        dbCollection.insert_many(allProductsOnSale)


##################################################
#                                                #
#              RUNNING ROOM - NIKE               #
#                                                #
##################################################
def scrape_runningRoom_nike_runner_sales(shoeReleaseDB, chromeOptions):
    allSaleNikeRunningRoom = []
    allNikeLinks = []
    nikeRunningRoomSaleCollection = shoeReleaseDB.nikeRunnerSales

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

    # Create a list of the corresponding product links
    for product in runningSales:
        nikeLink = product.find('a')["href"]
        allNikeLinks.append(str(nikeLink))

    # Update the current time at which availability was checked
    curTime = datetime.now()

    # Create each running shoe object with specified fields
    for shoe in runningSales:
        nikeRunnerObject = {
            "shoeName":shoe.find('h2', attrs={"class":"product-name"}).find('a').text,
            "shoeType":"Running",
            "shoeReducedPrice":shoe.find("span", attrs={"class":"price"}).text.split("CAD")[0].strip(),
            "shoeOriginalPrice":shoe.find("span", attrs={"class":"price"}).text.split("CAD")[1].strip(),
            "shoeLink":shoe.find('h2', attrs={"class":"product-name"}).find('a')["href"],
            "lastUpdated":curTime.strftime("%H:%M:%S, %m/%d/%Y")
        }

        # Obtain the sale value (Rounded to one decimal place)
        nikeRunnerObject["salePercent"] = str(round((100 - (float(nikeRunnerObject["shoeReducedPrice"][1:]) / float(nikeRunnerObject["shoeOriginalPrice"][1:])) * 100), 1)) + "%"
        allSaleNikeRunningRoom.append(nikeRunnerObject)

    # Iterate through each corresponding link, and load the product pages
    for index in range(0, len(allNikeLinks)):
        driver = webdriver.Chrome(options=chromeOptions, executable_path='./chromedriver') # FOR LOCAL ONLY
        #driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chromeOptions)
        driver.get(allNikeLinks[index])
        time.sleep(0.5)

        # Parse the page_source
        productResponse = driver.page_source
        driver.quit()
        productSoup = BeautifulSoup(productResponse, "html.parser")

        # The images exist within the script tags, and so we isolate the data by parsing the object within the script tags
        scriptData = productSoup.find_all('script')
        imgLink = json.loads(str(scriptData[1].string))["[data-gallery-role=gallery-placeholder]"]["mage/gallery/gallery"]["data"][0]["img"]
        allSaleNikeRunningRoom[index]["shoeImg"] = imgLink
        print(allSaleNikeRunningRoom[index])

    # If there are presently documents in the collection, ONLY delete documents from RunningRoom
    if (nikeRunningRoomSaleCollection.count_documents({}) != 0):
        nikeRunningRoomSaleCollection.delete_many({"shoeLink":{"$regex":"runningroom"}})
        nikeRunningRoomSaleCollection.insert_many(allSaleNikeRunningRoom)
    else:
        nikeRunningRoomSaleCollection.insert_many(allSaleNikeRunningRoom)

# Returns the specific product code from a link for Footlocker
def get_prod_code(prodLink):
    formattedLink = prodLink.split("/")
    productCode = formattedLink[len(formattedLink)-1].split(".")[0]
    print(productCode)
    return productCode

def main():
    # Connect to DB
    client = pymongo.MongoClient("mongodb+srv://webscraper:webscraper2193@webscraper-db.urihh.azure.mongodb.net/shoepicDB?retryWrites=true&w=majority", ssl=True,ssl_cert_reqs='CERT_NONE')
    shoeReleaseDB = client.get_database('shoepicDB')
    print("Connected!")

    # Initialize Chrome web driver for selenium (must be in Headless mode for Heroku)
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chromeOptions.add_argument("--headless") 
    chromeOptions.add_argument('--disable-gpu')
    chromeOptions.add_argument("--disable-dev-shm-usage")
    chromeOptions.add_argument("--no-sandbox")
    print("Initialized ChromeDrivers!")

    while True:
        # print("NIKE RUNNING SALE")
        # scrape_nike_runner_sales(shoeReleaseDB, chromeOptions)
        # time.sleep(3)
        # print("NIKE RUNNING SALE @ RUNNINGROOM")
        # scrape_runningRoom_nike_runner_sales(shoeReleaseDB, chromeOptions)
        # time.sleep(3);
        # print("NIKE LIFESTYLE SALE")
        # scrape_nike_lifestyle_sales(shoeReleaseDB, chromeOptions)
        # time.sleep(3)
        # print("NIKE SB SALE")
        # scrape_nike_SB_sales(shoeReleaseDB, chromeOptions)
        # time.sleep(3)
        # print("NIKE JORDAN SALE")
        # scrape_nike_jordan_sales(shoeReleaseDB, chromeOptions)
        # time.sleep(3)
        # print("NIKE SB")
        # scrape_nike_sales(shoeReleaseDB, chromeOptions, "SB")
        # time.sleep(3)

        # print("NIKE LIFESTYLE")
        # scrape_nike_sales(shoeReleaseDB, chromeOptions, "lifestyle")
        # time.sleep(3)

        # print("NIKE RUNNING")
        # scrape_nike_sales(shoeReleaseDB, chromeOptions, "jordan")
        # time.sleep(3)

        # print("NIKE JORDAN")
        # scrape_nike_sales(shoeReleaseDB, chromeOptions, "running")
        # time.sleep(3)

        # print("ADIDAS RUNNING SALE")
        # scrape_adidas_running_sales(shoeReleaseDB, chromeOptions) 
        # time.sleep(3)
        # print("ADIDAS ORIGINALS SALE")
        # scrape_adidas_originals_sales(shoeReleaseDB, chromeOptions) 
        # time.sleep(3)
        # print("ADIDAS TIRO SALE")
        # scrape_adidas_tiro_sales(shoeReleaseDB, chromeOptions) 
        # # time.sleep(3)
        print("ADIDAS ORIGINALS")
        scrape_adidas_sales(shoeReleaseDB, chromeOptions, "tiro")
        
        # print("FOOTLOCKER GENERAL SCRAPER")
        # scrape_footlocker_sales(shoeReleaseDB, chromeOptions, "ar")
        # time.sleep(1)

        # print("FOOTLOCKER NIKE LIFESTYLE SALE (MENS)")
        # scrape_footlocker_nike_lifestyle_sales(shoeReleaseDB, chromeOptions, "Men")
        # time.sleep(3)
        # print("FOOTLOCKER NIKE LIFESTYLE SALE (WOMENS)")
        # scrape_footlocker_nike_lifestyle_sales(shoeReleaseDB, chromeOptions, "Women")
        # time.sleep(3)
        # print("FOOTLOCKER NIKE LIFESTYLE SALE (KIDS)")
        # scrape_footlocker_nike_lifestyle_sales(shoeReleaseDB, chromeOptions, "Kids")
        # time.sleep(3)



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