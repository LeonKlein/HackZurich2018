from score_calculation import regex_matching, recipe_loop
import numpy as np


def find_matches(recipe, lookup_table):
    ingredients = regex_matching(recipe)
    ingredient_names = [one_ing['ingredient'] for one_ing in ingredients]
    listed_ingreds = []
    for ing in ingredient_names:
        for key in lookup_table.keys():
            if key in ing:
                listed_ingreds.append(key)
                break
    return list(set(listed_ingreds))


def get_ingredient_lists_and_scores(recipes, lookup_table):
    scores = recipe_loop(recipes, lookup_table)
    db = []
    for recipe in recipes:
        listed_ingreds = find_matches(recipe, lookup_table)

        db.append(listed_ingreds)
    return np.array(db), np.array(scores)


def find_current_recipe_and_score(url, recipes, scores):
    recipe = [item for item in recipes if item.get('Url') == url][0]
    idx = recipes.index(recipe)
    return recipe, scores[idx]


def find_better(
        ing_lists, urls, current_recipe, current_score, scores, lookup_table):
        # Find recipes with a better score and similar ingredients

    current_list = find_matches(current_recipe, lookup_table)
    coincidences = []
    better_data = ing_lists[scores > current_score]
    better_urls = urls[scores > current_score]
    better_scores = scores[scores > current_score]
    for ingredient_list in better_data:
        coincidences.append(
            len(list(set(current_list) & set(ingredient_list))))
    ind = (-np.array(coincidences)).argsort()[:8]
    idx = (-better_scores[ind]).argsort()[:3]
    suggested_lists = better_data[ind[idx]]
    # diffs = [get_diff(current_list, sugg_list) for sugg_list in suggested_lists]
    return better_urls[ind[idx]], better_scores[ind[idx]]


