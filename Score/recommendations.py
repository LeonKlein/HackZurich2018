import dataset
from score_calculation import read_scrapped_file, extract_cost_table, regex_matching, recipe_loop


db_file = 'sqlite:///mydb.db'
fname = "DataScrapper/tools/scrappedData.txt"
fref = "Score/EnvironmentalData.csv"

recipes = read_scrapped_file(fname, region=(750, 810))
costs_table = extract_cost_table(fref_name=fref)

def find_matches(ingredients, lookup_table):
    listed_ingreds = {}
    for ing in ingredients:
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
        ingredient_names = [one_ing['ingredient'] for one_ing in ingredients]
        listed_ingreds = find_matches(ingredient_names, lookup_table)
        listed_ingreds.update({"Url": recipe["Url"], "Score": score})
        table.insert(listed_ingreds)
    #[print(row) for row in table.all()]


def find_better(rec):
    "Find recipes with a better score and similar ingredients."
    better_recipe = table.find(table.table.columns.Score > rec["Score"])
    print([bet for bet in better_recipe])
    #better_recipe = table.find(id=[0, 1])

db = dataset.connect(db_file)
table = db['recipes']
data_base = setup_db(recipes, costs_table)
print("done")
find_better({"Score": 0.1})
