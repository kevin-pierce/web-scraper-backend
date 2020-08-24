import requests
from bs4 import BeautifulSoup

url = "https://forums.redflagdeals.com/hot-deals-f9/?c=12"
response = requests.get(url, timeout=5)
soup = BeautifulSoup(response.content, "html.parser")

deals = soup.select('div#site_container div#site_content div#partition_forums div.forums_layout div.primary_content div.forumbg div.inner ul.topiclist.topics.with_categories')

#for deal in deals.findAll('ul', attrs={"class": "topiclist topics with_categories"}):
#    print(deal)

print (deals)

#div div div div div div ul li'

#for deal in soup.findAll('li', attrs={"class": "topiclist topics with_categories"}):
#    print (deal.text.encode('utf-8'))