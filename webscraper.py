import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, abort
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import os

app = Flask(__name__)

chromeOptions = webdriver.ChromeOptions()
chromeOptions.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chromeOptions.add_argument("--headless")
chromeOptions.add_argument("--disable-dev-shm-usage")
chromeOptions.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chromeOptions)

@app.route('/shoepic/api/prod/v1.0/releases/all', methods=['GET'])
def get_releases():
    driver = webdriver.Chrome(options=options, executable_path='./chromedriver')
    driver.get("https://sneakernews.com/release-dates/")
    time.sleep(0.2)
    body = driver.find_element_by_tag_name("body")

    # Ensure entire page is loaded prior to parsing (Using selenium, we simulate a scroll function to load all release entries)
    numPageDowns = 20
    while numPageDowns:
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.1)
        numPageDowns-=1

    response = driver.page_source
    driver.quit()
    soup = BeautifulSoup(response, "html.parser")
    # Now finds all release-containing divs, including the ones that load on scroll
    shoeReleases = soup.findAll('div', attrs={"class": [
                                                        "releases-box col lg-2 sm-6 paged-1", 
                                                        "releases-box col lg-2 sm-6 paged-1 just_added", 
                                                        "releases-box col lg-2 sm-6 paged-2", 
                                                        "releases-box col lg-2 sm-6 paged-3"]}) 
    print(len(shoeReleases)) #temp

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

    return jsonify({'shoeData': shoes })

@app.route('/shoepic/api/prod/v1.0/releases/jordan', methods=['GET'])
def get_jordan_releases():

    driver = webdriver.Chrome(options=options, executable_path='./chromedriver')
    driver.get("https://sneakernews.com/air-jordan-release-dates/")
    time.sleep(0.2)
    body = driver.find_element_by_tag_name("body")

    # Ensure entire page is loaded prior to parsing (Using selenium, we simulate a scroll function to load all release entries)
    numPageDowns = 30
    while numPageDowns:
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.1)
        numPageDowns-=1
    response = driver.page_source
    driver.quit()
    soup = BeautifulSoup(response, "html.parser")
    jordanReleases = soup.findAll('div', attrs={"class": ["releases-box col lg-2 sm-6 paged-1", 
                                                        "releases-box col lg-2 sm-6 paged-1 just_added", 
                                                        "releases-box col lg-2 sm-6 paged-2", 
                                                        "releases-box col lg-2 sm-6 paged-3", 
                                                        "releases-box col lg-2 sm-6 paged-4",
                                                        "releases-box col lg-2 sm-6 paged-5"]})
    print(len(jordanReleases)) #temp
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

    return jsonify({'jordanData': jordans })


@app.route('/shoepic/api/prod/v1.0/releases/yeezy', methods=['GET'])
def get_yeezy_releases():

    driver = webdriver.Chrome(options=options, executable_path='./chromedriver')
    driver.get("https://sneakernews.com/adidas-yeezy-release-dates/")
    time.sleep(0.2)
    body = driver.find_element_by_tag_name("body")

    # Ensure entire page is loaded prior to parsing (Using selenium, we simulate a scroll function to load all release entries)
    numPageDowns = 20
    while numPageDowns:
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.1)
        numPageDowns-=1
        
    response = driver.page_source
    driver.quit()
    soup = BeautifulSoup(response, "html.parser")
    yeezyReleases = soup.findAll('div', attrs={"class": ["releases-box col lg-2 sm-6 paged-1", 
                                                        "releases-box col lg-2 sm-6 paged-1 just_added", 
                                                        "releases-box col lg-2 sm-6 paged-2", 
                                                        "releases-box col lg-2 sm-6 paged-3"]})
    print(len(yeezyReleases))
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
        yeezys.append(yeezyShoeObject);

    return jsonify({'yeezyData': yeezys })

if __name__ == '__main__':
    app.run(debug=True)