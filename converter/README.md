## Automatsko konvertovanje pravnih propisa Republike Srbije u Akoma-Ntoso v3.0 format podataka

Projekat se bavi automatskim anotiranjem pravnih propisa Republike Srbije u Akoma-Ntoso v3.0 format podataka. Uključuje anotiranje 3 sloja Akoma-Ntoso formata:
1. Strukture dokumenta
1. Tekstualni sadržaj sa referencama
1. Metapodaci dokumenta (_Top level class (TLC)_ sa [_FRBR_](https://www.oclc.org/research/activities/frbr.html) ontologijom)

Propisi su skinuti sa [pravno informacionog sistema Srbije](http://www.pravno-informacioni-sistem.rs/reg-search)

### Uputsva za nameštanje okruženja
Potrebne su 2 verzije pythona da budu instalirane: [3.7 ili novija](https://www.python.org/downloads/release/python-370/) i [2.7.16](https://www.python.org/downloads/release/python-2716/). 
Preporuka je instaliranje pomoću [anaconde](https://www.anaconda.com/distribution/) za python 3.

Sledeći potprojekti koriste odgovarajuće verzije:
```
Akoma = python 3.7 intrepreter
reldi-tagger = python 2.7 intrepreter
```

Za 2.7 potrebne su sledeće biblioteke:
```cmd
python2 -m pip install marisa-trie==0.7.5
python2 -m pip install python-crfsuite==0.9.6
python2 -m pip install scikit-learn==0.20.4
```
Potrebno je instalirati [_Microsoft Visual C++ Compiler for Python 2.7_](https://www.microsoft.com/en-us/download/details.aspx?id=44266)

[ReLDI taggeru](https://github.com/clarinsi/reldi-tagger) je potrebno skinuti [srpski lexicon (1.2 GB)](http://nlp.ffzg.hr/data/reldi/sr.lexicon.guesser), nakon čega je neophodno pozicionirati ga kao na sledećem primeru:
```
project_root_dir/reldi-tagger/sr.lexicon.guesser
```

Za 3.7 potrebne su sledeće biblioteke (idealno unutar izabranog okruženja `conda activate venv`):
```cmd
pip install beautifulsoup4
pip install lxml
pip install termcolor
pip install numpy
pip install pandas
pip install sklearn
pip install sklearn_crfsuite
pip install matplotlib
```
__Napomena__: Možda bude potrebno instalirati dodatne biblioteke ukoliko nije kreirano okruženje za 3.7 verziju sa anacondom (`conda create -n myenv python=3.7`).

Sledeća upustva su samo ukoliko nije prepoznat poziv `python2 --version ` u cmdu/terminalu (što je standardno ponašanje na _Mac OS_).
Koraci potrebni da _connector.py_ radi pod _Windows_ platformom između različitih verzija _python_-a:
```
Dodati python u envirment variables u Windows
(Windows search env) -> Envirment Variables -> (Variable) Path - Edit -> 
(Dodati) C:\Python27 i C:\Python27\Scripts (Python27 ime foldera koji se instalirao python2.7)
Kod python27 Preimenovati "python.exe" u "python2.exe" i "pythonw.exe" u "pythonw2.exe"
```

## Upustva za pokretanje

Za pokretanje samo već skinutih podataka koji se nalaze u projektu može da se koristi [convert_all.py]( https://github.com/Gorluxor/MasterProject/blob/master/converting_rs_legal_acts_to_akoma_ntoso/convert_all.py) sa promenom _nastavi_ varijable. 

### Pozivanje metode za konvertovanje
```python
from Akoma.convert_all import apply_akn_tags
```
Nakon importovanja metode može da se koristi zaglavnje u sledećem obliku:
```python
def apply_akn_tags(text: str, meta_name: str, skip_tfidf_ner=False):
    """
    Applies to text Akoma Ntoso 3.0 tags for Republic of Serbia regulations
    :param text: HTML or plain text
    :param meta_name: name which was meta added 15 tag in meta
    :param skip_tfidf_ner: Don't add references> TLCconcept for document and TLC for ner
    :return: Labeled xml string
    """
```

