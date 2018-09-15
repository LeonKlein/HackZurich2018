import json
import csv
import re
import numpy as np
from mixed_fractions import Mixed

fname = "DataScrapper/tools/scrappedData.txt"
fref = "Score/EnvironmentalData.csv"

with open(fname) as f:
    content = f.read()
    recipes = json.loads(content)[2:3]
for recipe in recipes:
    #get ingredients and their amount
    ingredients = recipe['Ingredients']  

    quantities = (r"(?P<unit>cups|cup|ounce|tablespoons|tablespoon|teaspoons"
        r"|teaspoon|pounds|pound|pints|pint|pinch|pinches|)")
    pattern = r'(?P<quantity>[0-9/ ]+)' + quantities + r' (?P<ingredient>[a-zA-Z, ]+)'
    regex_ = re.compile(pattern, re.DOTALL) 
    ingreds = [] 
    for ing in ingredients:
        x = re.match(regex_, ing)
        if x is not None:
            ingreds.append(x.groupdict())



    #get number of servings
    servings = recipe['Servings']


    #open Environmental costs of different food tpes
    with open(fref) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        costs_table = {}
        for row in csv_reader:
            costs_table[row[0]] = float(row[1])


    #total cost    
    score = 0

    def calc_weight(amount):
        """Calculate the amount in kg
        """
        conversion = {"cup": 0.15, "cups": 0.15, "tablespoon": 0.008, 
        "tablespoons": 0.008, "ounce": 0.03, "ounces": 0.03, "pound": 0.45,
         "pounds": 0.45, "pint": 0.45, "pints": 0.45, "teaspoon": 0,
          "teaspoons": 0, "pinch": 0, "pinches": 0}

        if amount['unit'] in list(conversion.keys()):
            conversion_rate = conversion[amount['unit']]
            print(amount)
        else:
            conversion_rate = 0
            print(amount)
        return float(Mixed(amount['quantity'])) * conversion_rate



    for ing in ingreds:
        if ing['ingredient'] in list(costs_table.keys()):
            score += costs_table[ing['ingredient']] * calc_weight(ing)
        else:
            """Initialise non existing ingredients"""
            value1 = np.around(np.random.random(), decimals=2) * 10 
            value2 = np.around(np.random.random(), decimals=2) * 50 
            value3 = np.around(np.random.random(), decimals=2)
            score += value1 * calc_weight(ing) 
            #print(calc_weight(ing))

            with open(fref, mode='a', newline='') as csv_file:
                fieldnames = [ing['ingredient'] , value1, value2, value3]
                writer = csv.writer(csv_file, delimiter=';')
                writer.writerow(fieldnames)
    #print(score)

