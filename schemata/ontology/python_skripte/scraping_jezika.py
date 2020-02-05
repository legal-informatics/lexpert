from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

myUrl = 'https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes'

# ucitavanje htmla stranice i prebacivanje u soup
uClient = uReq(myUrl)
pageHtml = uClient.read()
uClient.close()
soupPage = soup(pageHtml, "html.parser")

# uzme sva glasila sa stranice, bez sluzbenog glasnika RS i sluzbenog lista AP Vojvodine
tabela = soupPage.find(id='Table')
tabela_telo = tabela.find('tbody')
redovi_tabele = tabela_telo.findAll('tr')

with open('jezici.txt', 'w', encoding='utf-8') as f:
    for red in redovi_tabele[1:]:
        kolone = red.findAll('td')
        f.write(kolone[5].getText() + "\t" + kolone[6].getText() + "\t" + kolone[2].getText() + '\n')
