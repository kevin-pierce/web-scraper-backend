import requests
from bs4 import BeautifulSoup

url = "https://forums.redflagdeals.com/hot-deals-f9/?c=12"
response = requests.get(url, timeout=5)
soup = BeautifulSoup(response.content, "html.parser")

deals = soup.findAll('li', attrs={"class": "row topic"})

todaysDeals = []

for deal in deals:
    todaysDeals.append(deal);

print(todaysDeals[0])
#div div div div div div ul li'

#for deal in soup.findAll('li', attrs={"class": "topiclist topics with_categories"}):
#    print (deal.text.encode('utf-8'))