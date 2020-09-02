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

def scrape_all_releases(shoeReleaseDB, chromeOptions):
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
    shoeReleases = soup.findAll('div', attrs={"class": [
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
            "releaseRegion":shoeDetails.findAll("p")[3].text[8:].strip(),
            "sizeRun":shoeDetails.findAll("p")[0].text[10:].strip(),
            "shoeCW":shoeDetails.findAll("p")[1].text[7:].strip(),
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

def scrape_jordan_releases(shoeReleaseDB, chromeOptions):
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
    jordanReleases = soup.findAll('div', attrs={"class": ["releases-box col lg-2 sm-6 paged-1", 
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
            "releaseRegion":jShoeDetails.findAll("p")[3].text[8:].strip(),
            "sizeRun":jShoeDetails.findAll("p")[0].text[10:].strip(),
            "shoeCW":jShoeDetails.findAll("p")[1].text[7:].strip(),
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


def scrape_yeezy_releases(shoeReleaseDB, chromeOptions):
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
    yeezyReleases = soup.findAll('div', attrs={"class": ["releases-box col lg-2 sm-6 paged-1", 
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
            "releaseRegion":yShoeDetails.findAll("p")[3].text[8:].strip(),
            "sizeRun":yShoeDetails.findAll("p")[0].text[10:].strip(),
            "shoeCW":yShoeDetails.findAll("p")[1].text[7:].strip(),
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

# Sale Running Shoes
def scrape_nike_runner_sales(shoeReleaseDB, chromeOptions):
    allSaleNikeRunner = []

    nikeRunnerSaleCollection = shoeReleaseDB.nikeRunnerSales
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chromeOptions)
    driver.get("https://www.nike.com/ca/w/sale-running-shoes-37v7jz3yaepzy7ok")
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

    runnerSales = soup.findAll('div', attrs={"class":"product-card__body"})

    for shoe in runnerSales:
        shoeDetails = shoe.find('div', attrs={"class":"product-card__info disable-animations"})
        shoeImageData = shoe.find('a', attrs={"class":"product-card__img-link-overlay"})

        nikeRunnerObject = {
            "shoeName":shoeDetails.find('div', attrs={"class":"product-card__title"}).text,
            "shoeType":shoeDetails.find('div', attrs={"class":"product-card__subtitle"}).text,
            "shoeReducedPrice":shoeDetails.find('div', attrs={"class":"product-price is--current-price css-s56yt7"}).text,
            "shoeOldPrice":shoeDetails.find('div', attrs={"class":"product-price css-1h0t5hy"}).text,
            "shoeImg":shoeImageData.find('div', attrs={"class":"image-loader css-zrrhrw product-card__hero-image is--loaded"}).find("source", attrs={"srcset":True})["srcset"],
            "shoeCW":shoeDetails.find('div', attrs={"class":"product-card__product-count"}).find('span').text
        }
        allSaleNikeRunner.append(nikeRunnerObject)

    if (nikeRunnerSaleCollection.count_documents({}) != 0):
        nikeRunnerSaleCollection.delete_many({})
        nikeRunnerSaleCollection.insert_many(allSaleNikeRunner)
    else:
        nikeRunnerSaleCollection.insert_many(allSaleNikeRunner)

def scrape_nike_lifestyle_sales(shoeReleaseDB, chromeOptions):
    allSaleNikeLifestyle = []

    nikeLifestyleSaleCollection = shoeReleaseDB.nikeLifestyleSales
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chromeOptions)
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

    lifestyleSales = soup.findAll('div', attrs={"class":"product-card__body"})
    print(lifestyleSales)

    for shoe in lifestyleSales:
        shoeDetails = shoe.find('div', attrs={"class":["product-card__info disable-animations", 
                                                       "product-card__info for--product disable-animations"]})
        print(shoeDetails)
        shoeImageData = shoe.find('a', attrs={"class":"product-card__img-link-overlay"})
        print(shoeImageData)

        nikeLifestyleObject = {
            "shoeName":shoeDetails.find('div', attrs={"class":"product-card__title"}).text,
            "shoeType":shoeDetails.find('div', attrs={"class":"product-card__subtitle"}).text,
            "shoeReducedPrice":shoeDetails.find('div', attrs={"class":"product-price is--current-price css-s56yt7"}).text,
            "shoeOldPrice":shoeDetails.find('div', attrs={"class":"product-price css-1h0t5hy"}).text,
            "shoeImg":shoeImageData.find('div', attrs={"class":"image-loader css-zrrhrw product-card__hero-image is--loaded"}).find("source", attrs={"srcset":True})["srcset"],
            "shoeCW":shoeDetails.find('div', attrs={"class":"product-card__product-count"}).find('span').text
        }
        allSaleNikeLifestyle.append(nikeLifestyleObject)

    if (nikeLifestyleSaleCollection.count_documents({}) != 0):
        nikeLifestyleSaleCollection.delete_many({})
        nikeLifestyleSaleCollection.insert_many(allSaleNikeLifestyle)
    else:
        nikeLifestyleSaleCollection.insert_many(allSaleNikeLifestyle)

# Adidas has the issue where we cannot simply gather all data on the page by spam-scrolling down
# We must scrape subsequent pages with differing URLs
def scrape_adidas_running_sales(shoeReleaseDB, chromeOptions):
    allAdidasRunningSale = []

    adidasRunningSaleCollection = shoeReleaseDB.adidasRunnerSales
    #driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chromeOptions) # FOR HEROKU ONLY
    driver = webdriver.Chrome(options=chromeOptions, executable_path='./chromedriver') # FOR LOCAL ONLY
    driver.get("https://www.sportinglife.ca/en-CA/adidas/sale/shoe-sale/")
    time.sleep(1)
    body = driver.find_element_by_tag_name("body")

    response = driver.page_source
    driver.quit()

    soup = BeautifulSoup(response, "html.parser")
    print(soup)
    #shoe = soup.find("div", attrs={"class":"ProductCard"})
    #print(shoe)

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

    scrape_adidas_running_sales(shoeReleaseDB, chromeOptions) #- Will fix later (to bypass blocked sites lol)

    # while True:
    #     print("NIKE RUNNING SALE")
    #     scrape_nike_runner_sales(shoeReleaseDB, chromeOptions)
    #     time.sleep(3)
    #     print("NIKE LIFESTYLE SALE")
    #     scrape_nike_lifestyle_sales(shoeReleaseDB, chromeOptions)
    #     time.sleep(3)
    #     print("ALL SHOES")
    #     scrape_all_releases(shoeReleaseDB, chromeOptions)
    #     time.sleep(3)
    #     print("JORDANS")
    #     scrape_jordan_releases(shoeReleaseDB, chromeOptions)
    #     time.sleep(3)
    #     print("YEEZYS")
    #     scrape_yeezy_releases(shoeReleaseDB, chromeOptions)
    #     time.sleep(3)

main()