import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, abort
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")

driver = webdriver.Chrome()
driver.get("https://www.nintendo.com/")
print(driver.page_source)
driver.quit()


app = Flask(__name__)
"""
@app.route('/shoepic/api/prod/v1.0/releases/all', methods=['GET'])
def get_releases():
    url = "https://sneakernews.com/release-dates/"
    response = requests.get(url, timeout=20)
    soup = BeautifulSoup(response.content, "html.parser")
    shoeReleases = soup.findAll('div', attrs={"class": "releases-box col lg-2 sm-6 paged-1"})

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

    url = "https://sneakernews.com/air-jordan-release-dates/"
    response = requests.get(url, timeout=20)
    soup = BeautifulSoup(response.content, "html.parser")
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
    url = "https://sneakernews.com/adidas-yeezy-release-dates/"
    response = requests.get(url, timeout=20)
    soup = BeautifulSoup(response.content, "html.parser")
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
"""

if __name__ == '__main__':
    app.run(debug=True)