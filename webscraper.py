import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, abort

app = Flask(__name__)

url = "https://sneakernews.com/release-dates/"
response = requests.get(url, timeout=20)
soup = BeautifulSoup(response.content, "html.parser")

shoeReleases = soup.findAll('div', attrs={"class": "releases-box col lg-2 sm-6 paged-1"})

print(len(shoeReleases))

shoes = []

for deal in shoeReleases:
    shoeContent = deal.find('div', attrs={"class":"content-box"})
    shoeDetails = shoeContent.find("div", attrs={"class":"post-data"})
    print(shoeDetails.findAll("p")[0].text[10:])
    
    dealObject = {
        "sizeRun":shoeDetails.findAll("p")[0].find("span").text[10:],
        "shoeName":shoeContent.find("h2").find("a").text,
        "shoePrice":shoeContent.find("span", attrs={"class":"release-price"}).text,
        "shoeReleaseDate":shoeContent.find("div", attrs={"class":"release-date-and-rating"}).find("span", attrs={"class":"release-date"}).text.strip(),
        "shoeImg":deal.find('div', attrs={"class":"image-box"}).find("a").find("img")['src'],
    }
    shoes.append(dealObject);

@app.route('/shoepic/api/prod/v1.0/releases/all', methods=['GET'])
def get_releases():

    

    return jsonify({'shoeData': shoes })

if __name__ == '__main__':
    app.run(debug=True)