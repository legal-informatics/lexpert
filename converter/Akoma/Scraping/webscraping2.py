"""
Scrape text of legal document and metadata, manually change DOC_TYPE, file_name
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import path
import json
import io

attribute = ['Назив прописа', 'ELI', 'Напомена издавача', 'Додатне информације', 'Врста прописа', 'Доносилац',
             'Област', 'Група', 'Датум усвајања', 'Гласило и датум објављивања',
             'Датум ступања на снагу основног текста',
             'Датум примене', 'Правни претходник', 'Издавач']

propisi = []


def write_json_file(file_name, data):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def write_csv_file(file_name, row):
    fd = open(file_name, 'a', encoding="utf-8")
    fd.write(row)
    fd.write('\n')
    fd.close()


if __name__ == '__main__':
    option = webdriver.ChromeOptions()
    option.add_argument("--incognito")
    option.add_argument("--start-maximized")

    # TO CHANGE
    DOC_TYPE = "uredba" # NAME OF FOLDER IN DATA
    file_name = '..\\data\\links\\links_uredba.txt'
    # END TO CHANGE
    META_DATA = "..\\data\\meta\\" + DOC_TYPE

    # If it does not work download new chrome driver at https://sites.google.com/a/chromium.org/chromedriver/
    # For your working chrome version and put it in scraping folder
    exe_path = path.dirname(__file__) + '\\chromedriver.exe'
    browser = webdriver.Chrome(executable_path=exe_path, chrome_options=option)

    file = open(file_name, "r")

    row = ""
    for i in range(0, len(attribute)):
        row += attribute[i]
        if i < len(attribute) - 1:
            row += "#"
    row += "#filename"
    write_csv_file(META_DATA + ".csv", row)

    brojac = 7188  # 1321(acts), 4015(odluke), 7196(pravilnik)
    for line in file:
        browser.get(line)

        brojac += 1
        print(brojac)

        try:
            o_aktu = WebDriverWait(browser, 30).until(
                EC.visibility_of_element_located((By.XPATH, '//h5[@class="panel-title panel-title"]/a')))
            o_aktu.click()
        except:
            continue
        try:
            tabela = WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="actContentSecondary"]/table')))
        except:
            continue

        redovi = tabela.find_elements(By.TAG_NAME, "tr")

        labele = []
        vrednosti = []

        for red in redovi:
            labela = red.find_element(By.CLASS_NAME, "act-idcard-label-cell-1")
            vrednost = red.find_element(By.CLASS_NAME, "act-idcard-value-cell-1")

            p_labela = labela.find_element(By.TAG_NAME, "p")
            p_vrednost = vrednost.find_element(By.TAG_NAME, "p")

            if p_labela.text not in attribute:
                continue

            if p_labela.text not in labele:
                labele.append(p_labela.text)
                vrednosti.append(p_vrednost.text)
                #print(p_labela.text)  Za ispis na konzolu kako cuva
                #print(p_vrednost.text)

        propis = "{"
        row = ""
        j = 0
        for i in range(0, len(attribute)):
            if len(labele) > j:
                if labele[j] == attribute[i]:
                    propis += '"' + labele[j] + '" : ' + '"' + vrednosti[j].replace('"', '').replace('\n', '') + '"'
                    row += vrednosti[j].replace('"', '').replace('\n', '')
                    j += 1
                else:
                    propis += '"' + attribute[i] + '" : ' + '""'
            else:
                propis += '"' + attribute[i] + '" : ' + '""'

            if i < len(attribute) - 1:
                propis += ","
                row += "#"
        ime = str(brojac) + ".html"
        row += "#" + ime
        propis += ',\n"filename": "' + ime + '"'
        propis += "}"
        propis_json = json.loads(propis)

        propisi.append(propis_json)

        write_json_file(META_DATA + '.json', propisi)
        write_csv_file(META_DATA + ".csv", row)
        
        try:
            article = WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.XPATH, '//article')))
        except:
            continue
        ## skidanje samog teksta akta u html foramtu
        fajl = io.open("../data/" + DOC_TYPE + "/"+str(brojac)+".html", mode="w", encoding="utf-8")
        fajl.write(article.get_attribute('innerHTML'))
        fajl.close()