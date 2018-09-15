import dataset
from score_calculation import read_scrapped_file, extract_cost_table, regex_matching, recipe_loop
import itertools as it
import numpy as np

db_file = 'sqlite:///mydb.db'
fname = "DataScrapper/tools/scrappedData.txt"
fref = "Score/EnvironmentalData.csv"

recipes = read_scrapped_file(fname, region=None)
urls = np.array([recipe["Url"] for recipe in recipes])
costs_table = extract_cost_table(fref_name=fref)

def find_matches(recipe, lookup_table):
    ingredients= regex_matching(recipe)
    ingredient_names = [one_ing['ingredient'] for one_ing in ingredients]
    listed_ingreds = []
    for ing in ingredient_names:
        for key in lookup_table.keys():
            if key in ing:
                listed_ingreds.append(key)
                break
    return list(set(listed_ingreds))

def setup_db(recipes, lookup_table):

    scores = recipe_loop(recipes, lookup_table)

    db = []
    for recipe in recipes:
        listed_ingreds = find_matches(recipe, lookup_table)

        db.append(listed_ingreds)
    return np.array(db), np.array(scores)
    #[print(row) for row in table.all()]



def find_current_score(url, recipes, scores):
    recipe = [item for item in recipes if item.get('Url') == url][0]
    idx = recipes.index(recipe)
    return scores[idx]


def find_better(current_recipe, scores, lookup_table):
    "Find recipes with a better score and similar ingredients."
    current_list = find_matches(current_recipe, lookup_table)
    current_score = find_current_score(current_recipe["Url"], recipes, scores)
    coincidences = []
    coin = []
    better_data = data_base[scores > current_score]
    better_urls = urls[scores > current_score]
    better_scores = scores[scores > current_score]
    for ingredient_list in better_data:
        coin.append(list(set(current_list) & set(ingredient_list)))
        coincidences.append(len(list(set(current_list) & set(ingredient_list))))
    ind = (-np.array(coincidences)).argsort()[:10]
    idx = (-better_scores[ind]).argsort()[:3]
    return better_urls[ind[idx]], better_scores[ind[idx]]


current_recipe = read_scrapped_file(fname, region=(1219, 1220))[0]
data_base, scores = setup_db(recipes, costs_table)

