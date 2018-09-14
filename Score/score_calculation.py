import json
import csv
import re

fname = "DataScrapper/tools/testData.txt"
fref = "Score/EnvironmentalData.csv"

with open(fname) as f:
    content = f.read()
    recipe = json.loads(content)[1]

#get ingredients and their amount
ingredients = recipe['Ingredients']  
print(ingredients)

pattern = r'(?P<quantity>[0-9] [a-z]+) (?P<ingredient>[a-zA-Z ]+)'
regex_ = re.compile(pattern, re.DOTALL)  
for ing in ingredients:
    x = re.match(regex_, ing)
    if x is not None:
        print(x.groupdict())

#get number of servings
servings = recipe['Servings']



with open(fref) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    for row in csv_reader:
        print(row)
    



