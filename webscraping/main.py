import requests
from bs4 import BeautifulSoup

r = requests.get('http://pythonhow.com/real-estate/rock-springs-wy/LCWYROCKSPRINGS')
c = r.content

s = BeautifulSoup(c, 'html.parser')

def getRecords(soup):
	return soup.find_all('div', {'class': 'propertyRow'})

def getPrices(rec):
	for i in rec:
		print(i.find_all('h4', {'class': 'propPrice'})[0].text.rstrip())
		print(i.find_all('span', {'class': 'propAddressCollapse'})[0].text)
		print(i.find_all('span', {'class': 'propAddressCollapse'})[1].text)

print(getPrices(getRecords(s)))