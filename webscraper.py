import requests
from bs4 import BeautifulSoup

url = "https://forums.redflagdeals.com/hot-deals-f9/?c=12"
response = requests.get(url, timeout=5)
content = BeautifulSoup(response.content, "html.parser")

for deal in content.findAll('li', attrs={"class": "topiclist topics with_categories"}):
    print (deal.text.encode('utf-8'))