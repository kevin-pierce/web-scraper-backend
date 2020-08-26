import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, abort
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time

app = Flask(__name__)

options = Options()
options.headless = False
options.add_argument("--window-size=1920,1200")

@app.route('/shoepic/api/prod/v1.0/releases/all', methods=['GET'])
def get_releases():
    driver = webdriver.Chrome(options=options, executable_path='./chromedriver')
    driver.get("https://sneakernews.com/release-dates/")
    time.sleep(0.5)
    body = driver.find_element_by_tag_name("body")

    numPageDowns = 20
    while numPageDowns:
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)
        numPageDowns-=1

    time.sleep(3)
    response = driver.page_source
    driver.quit()
    soup = BeautifulSoup(response, "html.parser")
    shoeReleases = soup.findAll('div', attrs={"class": [
                                                        "releases-box col lg-2 sm-6 paged-1", 
                                                        "releases-box col lg-2 sm-6 paged-1 just_added", 
                                                        "releases-box col lg-2 sm-6 paged-2", 
                                                        "releases-box col lg-2 sm-6 paged-3"]}) 
    print(len(shoeReleases))

    shoes = []

    for deal in shoeReleases:
        shoeContent = deal.find('div', attrs={"class":"content-box"})
        shoeDetails = shoeContent.find("div", attrs={"class":"post-data"})
        
        shoeObject = {
            "releaseRegion":shoeDetails.findAll("p")[3].text[8:].strip(),
            "sizeRun":shoeDetails.findAll("p")[0].text[10:].strip(),
            "shoeCW":shoeDetails.findAll("p")[1].text[7:].strip(),
            "shoeName":shoeContent.find("h2").find("a").text,
            "shoePrice":shoeContent.find("span", attrs={"class":"release-price"}).text,
            "shoeReleaseDate":shoeContent.find("div", attrs={"class":"release-date-and-rating"}).find("span", attrs={"class":"release-date"}).text.strip(),
            "shoeImg":deal.find('div', attrs={"class":"image-box"}).find("a").find("img")['src'],
        }
        shoes.append(shoeObject);

    return jsonify({'shoeData': shoes })

@app.route('/shoepic/api/prod/v1.0/releases/jordan', methods=['GET'])
def get_jordan_releases():

    driver = webdriver.Chrome(options=options, executable_path='./chromedriver')
    driver.get("https://sneakernews.com/air-jordan-release-dates/")
    response = driver.page_source
    driver.quit()
    soup = BeautifulSoup(response, "html.parser")
    jordanReleases = soup.findAll('div', attrs={"class": "releases-box col lg-2 sm-6 paged-1"})

    jordans = []

    for deal in jordanReleases:
        jShoeContent = deal.find('div', attrs={"class":"content-box"})
        jShoeDetails = jShoeContent.find("div", attrs={"class":"post-data"})
        
        jordanShoeObject = {
            "releaseRegion":jShoeDetails.findAll("p")[3].text[8:].strip(),
            "sizeRun":jShoeDetails.findAll("p")[0].text[10:].strip(),
            "shoeCW":jShoeDetails.findAll("p")[1].text[7:].strip(),
            "shoeName":jShoeContent.find("h2").find("a").text,
            "shoePrice":jShoeContent.find("span", attrs={"class":"release-price"}).text,
            "shoeReleaseDate":jShoeContent.find("div", attrs={"class":"release-date-and-rating"}).find("span", attrs={"class":"release-date"}).text.strip(),
            "shoeImg":deal.find('div', attrs={"class":"image-box"}).find("a").find("img")['src'],
        }
        jordans.append(jordanShoeObject);

    return jsonify({'jordanData': jordans })


@app.route('/shoepic/api/prod/v1.0/releases/yeezy', methods=['GET'])
def get_yeezy_releases():

    driver = webdriver.Chrome(options=options, executable_path='./chromedriver')
    driver.get("https://sneakernews.com/adidas-yeezy-release-dates/")
    response = driver.page_source
    driver.quit()
    soup = BeautifulSoup(response, "html.parser")
    yeezyReleases = soup.findAll('div', attrs={"class": "releases-box col lg-2 sm-6 paged-1"})

    yeezys = []

    for deal in yeezyReleases:
        yShoeContent = deal.find('div', attrs={"class":"content-box"})
        yShoeDetails = yShoeContent.find("div", attrs={"class":"post-data"})
        
        yeezyShoeObject = {
            "releaseRegion":yShoeDetails.findAll("p")[3].text[8:].strip(),
            "sizeRun":yShoeDetails.findAll("p")[0].text[10:].strip(),
            "shoeCW":yShoeDetails.findAll("p")[1].text[7:].strip(),
            "shoeName":yShoeContent.find("h2").find("a").text,
            "shoePrice":yShoeContent.find("span", attrs={"class":"release-price"}).text,
            "shoeReleaseDate":yShoeContent.find("div", attrs={"class":"release-date-and-rating"}).find("span", attrs={"class":"release-date"}).text.strip(),
            "shoeImg":deal.find('div', attrs={"class":"image-box"}).find("a").find("img")['src'],
        }
        yeezys.append(yeezyShoeObject);

    return jsonify({'yeezyData': yeezys })

if __name__ == '__main__':
    app.run(debug=True)