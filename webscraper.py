import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, abort

app = Flask(__name__)

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
            "releaseRegion":shoeDetails.findAll("p")[3].text,
            "sizeRun":shoeDetails.findAll("p")[0].find("span").text[10:],
            "shoeCW":shoeDetails.findAll("p")[1].text[7:],
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
            "releaseRegion":shoeDetails.findAll("p")[3].text.strip(),
            "sizeRun":shoeDetails.findAll("p")[0].find("span").text[10:],
            "shoeCW":shoeDetails.findAll("p")[1].text[7:].strip(),
            "shoeName":shoeContent.find("h2").find("a").text,
            "shoePrice":shoeContent.find("span", attrs={"class":"release-price"}).text,
            "shoeReleaseDate":shoeContent.find("div", attrs={"class":"release-date-and-rating"}).find("span", attrs={"class":"release-date"}).text.strip(),
            "shoeImg":deal.find('div', attrs={"class":"image-box"}).find("a").find("img")['src'],
        }
        jordans.append(jordanShoeObject);

    return jsonify({'jordanData': jordans })

if __name__ == '__main__':
    app.run(debug=True)