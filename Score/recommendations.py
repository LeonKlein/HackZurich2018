import dataset
from score_calculation import read_scrapped_file, extract_cost_table, regex_matching


db_file = 'sqlite:///mydb.db'
fname = "DataScrapper/tools/scrappedData.txt"
fref = "Score/EnvironmentalData.csv"

recipes = read_scrapped_file(fname, region=(1, 3))
costs_table = extract_cost_table(fref_name=fref)


def setup_db(db_file, recipes):
    db = dataset.connect(db_file)
    table = db['recipes']
    table.drop()

    for recipe in recipes:
        ingreds = regex_matching(recipe)
        table.insert(dict())


setup_db(db_file, recipes)