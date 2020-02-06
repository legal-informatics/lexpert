from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

myUrl = 'https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2'

# ucitavanje htmla stranice i prebacivanje u soup
uClient = uReq(myUrl)
pageHtml = uClient.read()
uClient.close()
soupPage = soup(pageHtml, 'html.parser')

# uzme prvu tabelu koja ima ovo u class i iz nje izvlaci podatke
tabela = soupPage.find('table', {'class': 'wikitable sortable'})
tabela_telo = tabela.find('tbody')
redovi_tabele = tabela_telo.findAll('tr')

with open('zemlje.txt', 'w', encoding='utf-8') as f:
    for red in redovi_tabele[1:]:
        kolone = red.findAll('td')
        f.write(kolone[0].getText().lower() + '\t' + kolone[1].getText() + '\t' + '\n')