import json
import csv
import re
import numpy as np
from mixed_fractions import Mixed

fname = "DataScrapper/tools/scrappedData.txt"
fref = "Score/EnvironmentalData.csv"


def read_scrapped_file(fname, region=None):
    with open(fname) as f:
        content = f.read()
        recipes = json.loads(content)
    if region is None:
        return recipes
    else:
        return recipes[region[0]:region[1]]


def extract_cost_table(fref_name):
    # Returns dictionary
    # open Environmental costs of different food tpes
    with open(fref_name, encoding="utf-8", errors='ignore') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        costs_table = {}
        for row in csv_reader:
            costs_table[row[0]] = float(row[1])
    return costs_table


def regex_matching(recipe):
    # get ingredients and their amount
    ingredients = recipe['Ingredients']

    quantities = (r"(?P<unit>cups|cup|ounce|tablespoons|tablespoon|teaspoons"
                  r"|teaspoon|pounds|pound|pints|pint|pinches|pinch|gallons"
                  r"|gallon|)")
    pattern = r'(?P<quantity>[0-9/ ]+)' \
        + quantities    \
        + r' (?P<ingredient>[a-zA-Z, ]+)'
    regex_ = re.compile(pattern, re.DOTALL)
    ingreds = []
    for ing in ingredients:
        x = re.match(regex_, ing)
        if x is not None:
            ingreds.append(x.groupdict())
    return ingreds


def calc_weight(amount):
    """Calculate the amount in kg
    """
    conversion = {"cup": 0.15, "cups": 0.15, "tablespoon": 0.008,
                  "tablespoons": 0.008, "ounce": 0.03, "ounces": 0.03, "pound": 0.45,
                  "pounds": 0.45, "pint": 0.45, "pints": 0.45, "teaspoon": 0,
                  "teaspoons": 0, "pinch": 0, "pinches": 0, "gallons": 3.8, "gallon": 3.8}

    if amount['unit'] in list(conversion.keys()):
        conversion_rate = conversion[amount['unit']]
        #print(amount)
    else:
        conversion_rate = 0
        #print(amount)
    return float(Mixed(amount['quantity'])) * conversion_rate


def calculate_score(ingredients):
    score = 0
    for ing in ingredients:
        if ing['ingredient'] in list(costs_table.keys()):
            score += costs_table[ing['ingredient']] * calc_weight(ing)
        else:
            """Initialise non existing ingredients"""
            value1 = np.around(np.random.random(), decimals=2) * 10
            value2 = np.around(np.random.random(), decimals=2) * 50
            value3 = np.around(np.random.random(), decimals=2)
            score += value1 * calc_weight(ing)
            """
            with open(fref, mode='a', newline='') as csv_file:
                fieldnames = [ing['ingredient'], value1, value2, value3]
                writer = csv.writer(csv_file, delimiter=';')
                writer.writerow(fieldnames)
            """
    return score


recipes = read_scrapped_file(fname, region=(2, 9))
costs_table = extract_cost_table(fref_name=fref)

# Loop over recipes
# Calculate score fore every recipe
for recipe in recipes:
    ingreds = regex_matching(recipe)

    # get number of servings
    servings = recipe['Servings']

    score = calculate_score(ingredients=ingreds)
    print(score)
