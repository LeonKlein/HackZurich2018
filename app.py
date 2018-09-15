from flask import Flask, jsonify, request
import numpy as np
from Score.score_calculation import extract_cost_table, read_scrapped_file
from Score.recommendations import (get_ingredient_lists_and_scores,
                                   find_better, find_current_recipe_and_score)


# Initialize the server
app = Flask(__name__)

fref = "Score/EnvironmentalData.csv"
fname = "DataScrapper/tools/scrappedData.txt"

recipes = read_scrapped_file(fname, region=None)
urls = np.array([recipe["Url"] for recipe in recipes])
costs_table = extract_cost_table(fref_name=fref)

ing_lists, scores = get_ingredient_lists_and_scores(recipes=recipes,
                                                    lookup_table=costs_table)


@app.route('/')
def index():
    return "index"


@app.route('/get/<id>', methods=['GET'])
def handle_get(id):
    if request.method == 'GET':
        the_url = "https://www.allrecipes.com/recipe/"+id
        current_recipe, current_score = find_current_recipe_and_score(
            url=the_url, recipes=recipes, scores=scores)
        suggested_urls, suggested_scores = find_better(
            ing_lists=ing_lists,
            urls=urls,
            current_recipe=current_recipe,
            current_score=current_score,
            scores=scores,
            lookup_table=costs_table)

        suggestions = {"suggestion1": {"url": suggested_urls[0],
                                       "score": suggested_scores[0]},
                       "suggestion2": {"url": suggested_urls[1],
                                       "score": suggested_scores[1]},
                       "suggestion3": {"url": suggested_urls[2],
                                       "score": suggested_scores[2]}}

        return jsonify({"Url": current_recipe["Url"],
                        "score": current_score,
                        "suggestions": suggestions})


if __name__ == '__main__':
    app.run(port=62729, debug=True)
