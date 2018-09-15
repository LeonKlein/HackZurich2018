import json
import csv
import re
import numpy as np

fname = "DataScrapper/tools/testData.txt"
fref = "Score/EnvironmentalData.csv"

with open(fname) as f:
    content = f.read()
    recipe = json.loads(content)[1]

#get ingredients and their amount
ingredients = recipe['Ingredients']  

pattern = r'(?P<quantity>[0-9] [a-z]+) (?P<ingredient>[a-zA-Z ]+)'
regex_ = re.compile(pattern, re.DOTALL) 
ingreds = [] 
for ing in ingredients:
    x = re.match(regex_, ing)
    if x is not None:
        ingreds.append(x.groupdict())

print(ingreds)
#get number of servings
servings = recipe['Servings']


#open Environmental costs of different food tpes
with open(fref) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    costs_table = {}
    for row in csv_reader:
        costs_table[row[0]] = float(row[1])
    print(costs_table)

#total cost    
score = 0

for ing in ingreds:
    if ing['ingredient'] in list(costs_table.keys()):
        score += costs_table[ing['ingredient']]
    else:
        score += np.random.random() * 10
print(score)

