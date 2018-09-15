from flask import Flask, jsonify, request
from score_calculation import extract_cost_table
from score import process_recipe, read_scrapped_file

# Initialize the server
app = Flask(__name__)


fref = "Score/EnvironmentalData.csv"
fname = "DataScrapper/tools/scrappedData.txt"
recipes = read_scrapped_file(fname)
costs_table = extract_cost_table(fref_name=fref)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/get/<id>', methods=['GET'])
def handle_get(id):
    if request.method == 'GET':
        return jsonify({"score": 0.4})


if __name__ == '__main__':
    app.run(port=62729, debug=True)
