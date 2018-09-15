from flask import Flask, jsonify, request
from Score.score_calculation import extract_cost_table
from Score.score_calculation import process_recipe, read_scrapped_file

# Initialize the server
app = Flask(__name__)


fref = "Score/EnvironmentalData.csv"
fname = "DataScrapper/tools/scrappedData.txt"
recipes = read_scrapped_file(fname)
costs_table = extract_cost_table(fref_name=fref)


@app.route('/')
def index():
    return "index"


@app.route('/get/<id>', methods=['GET'])
def handle_get(id):
    if request.method == 'GET':
        the_url = "https://www.allrecipes.com/recipe/"+id
        recipe = [item for item in recipes if item.get('Url') == the_url][0]
        the_score = process_recipe(recipe, costs_table)
        return jsonify({"Url": recipe["Url"], "score": the_score})


if __name__ == '__main__':
    app.run(port=80, debug=True, host='0.0.0.0')
