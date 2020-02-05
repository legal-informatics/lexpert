import json

file = open('menu.json', 'r', encoding='utf-8')

ofile = open('types.txt', 'w', encoding='utf-8')

types_str = file.read()
types_json = json.loads(types_str)
#print(json.loads(types_json))
for podregistar in types_json:
    ofile.write(podregistar['name'] + '\n')
    for oblast in podregistar['children']:
        ofile.write('\t' + oblast['name'] + '\n')
        for podoblast in oblast['children']:
            ofile.write('\t\t' + podoblast['name'] + '\n')

file.close()
ofile.close()
