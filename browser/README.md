Instalacija:
  1. Instalirati Python na sistemu
  2. Instalirati biblioteke Flask, SPARQLWrapper, xmltodict, lxml, pdfkit
  3. Za koriscenje pdfkit-a potreban je wkhtmltopdf (https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf) - ako se koristi Windows za rad pdfkit-a potrebno je instalirati binarni fajl na outanji 'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
  
  4. Skinuti Apache Jena Fuseki (https://downloads.apache.org/jena/binaries/apache-jena-fuseki-3.14.0.zip)


Pokretanje:
  1. Potrebno je prvo setovati: set FLASK_APP=run_server.py
  2. Za rad u debug modu (automatsko refresovanje server pri promeni fajla) setovati: set FLASK_DEBUG=1
  3. U komandnoj liniji pokrenuti flask: flask run
  4. Flask server je pokrenut na http://127.0.0.1:5000
  
  5. Otici gde je skinut Apache Jena Fuseki i pokrenuti: fuseki-server.jar
  6. Server je pokrenut na http://localhost:3030/index.html
  7. Napraviti novu bazu ako je prvo pokretanje
  8. Uvesti u bazu fajlove: 
                   lexpert/schemata/ontology/akn_meta_combined_full.owl
                   lexpert/schemata/ontology/akn_meta_combined_full_examples.owl
                   
  
  
