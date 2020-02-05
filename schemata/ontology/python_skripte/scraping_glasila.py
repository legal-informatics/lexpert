from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

myUrl = 'https://www.paragraf.rs/glasila.html'

# ucitavanje htmla stranice i prebacivanje u soup
uClient = uReq(myUrl)
pageHtml = uClient.read()
uClient.close()
soupPage = soup(pageHtml, "html.parser")

# uzme sva glasila sa stranice, bez sluzbenog glasnika RS i sluzbenog lista AP Vojvodine
glasila_list = soupPage.findAll("div", {"class": "col-sm-6 glasilo-box"})
for g in glasila_list:
    ime_glasila = g.find('a').getText().strip()
    ime_glasila = ime_glasila.replace('Sl.', 'Službeni')
    print(ime_glasila)