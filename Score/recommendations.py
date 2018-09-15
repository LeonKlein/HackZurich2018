import dataset
from score_calculation import read_scrapped_file, extract_cost_table, regex_matching, recipe_loop
import itertools as it

db_file = 'sqlite:///mydb.db'
fname = "DataScrapper/tools/scrappedData.txt"
fref = "Score/EnvironmentalData.csv"

recipes = read_scrapped_file(fname, region=(800, 810))
costs_table = extract_cost_table(fref_name=fref)

def find_matches(ingredients, lookup_table):
    ingredient_names = [one_ing['ingredient'] for one_ing in ingredients]
    listed_ingreds = {}
    for ing in ingredient_names:
        for key in lookup_table.keys():
            if key in ing:
                listed_ingreds[key] = 1
                break
    return listed_ingreds

def setup_db(recipes, lookup_table):

    table.drop()
    scores = recipe_loop(recipes, lookup_table)


    for recipe, score in zip(recipes, scores):
        ingredients = regex_matching(recipe)
        listed_ingreds = find_matches(ingredients, lookup_table)
        listed_ingreds.update({"Url": recipe["Url"], "Score": score})
        table.insert(listed_ingreds)
    #[print(row) for row in table.all()]


def find_better(score, recipe, lookup_table):
    "Find recipes with a better score and similar ingredients."
    ingredients = regex_matching(recipe)
    print(ingredients)
    ingredient_names = find_matches(ingredients, lookup_table)
    print(ingredient_names)
    ingredient_combinations = list(it.combinations(list(ingredient_names.keys()), len(ingredient_names) - 2))
    print(ingredient_combinations)
    for permutation in ingredient_combinations:
        [print(permute) for permute in permutation]
        better_recipe = table.find(table.table.columns.Score > score, [table.table.columns.permute for permute in permutation] > 0)
    print([bet for bet in better_recipe])
    #better_recipe = table.find(id=[0, 1])

db = dataset.connect(db_file)
table = db['recipes']
data_base = setup_db(recipes, costs_table)
print("done")
current_recipe = read_scrapped_file(fname, region=(800, 801))

score = recipe_loop(current_recipe, costs_table) 
find_better(score, current_recipe[0], costs_table)
