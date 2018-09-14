import json
import csv


fname = "DataScrapper/tools/testData.txt"
fref = "Score/EnvironmentalData.csv"

with open(fname) as f:
    content = f.read()
    data = json.loads(content)[1]
    print(data)

#get number of servings
servings = data['Servings']

#get ingredients and their amount
ingredients = data['Ingredients']
print(ingredients)

with open(fref) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    for row in csv_reader:
        print(row)
    