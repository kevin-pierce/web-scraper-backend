import requests
from bs4 import BeautifulSoup

url = "https://sneakernews.com/release-dates/"
response = requests.get(url, timeout=20)
soup = BeautifulSoup(response.content, "html.parser")

deals = soup.findAll('div', attrs={"class": "col lg-12"})
#allShoes = deals.find('div', attrs={"class":"releases-box month-box col lg-2 sm-6 paged-1"})

print(deals)

todaysDeals = []

dealObject = {
    "shoeName":"",
    "shoePrice":0,
    "shoeImg":"",
}

shoeNames = []

for deal in deals:
    shoeContent = deal.find('div', attrs={"class":"content-box"})
    
    dealObject = {
        "shoeName":shoeContent.find("h2").find("a").text,
        "shoePrice":shoeContent.find("span", attrs={"class":"release-price"}).text,
        "shoeReleaseDate":shoeContent.find("div", attrs={"class":"release-date-and-rating"}).find("span", attrs={"class":"release-date"}).text.strip(),
        "shoeImg":deal.find('div', attrs={"class":"image-box"}).find("a").find("img")['src'],
    }
    print (dealObject)