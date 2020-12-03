import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from score_calculation import read_scrapped_file, extract_cost_table
from recommendations import find_matches
import os
import shutil



fname = "DataScrapper/tools/newData.txt"
fref = "Score/EnvironmentalData.csv"
out = 'model'

if os.path.exists(out):
    shutil.rmtree(out, ignore_errors=True)

recipes = read_scrapped_file(fname)
cost_table = extract_cost_table(fref)

possible_ingredients = np.array(list(cost_table.keys()))


#Get ingredients and the number of different ingredients as well as the user rating.
num_ingedients = []
ingredient_lists = []
rating = []
for recipe in recipes:
    matches = find_matches(recipe, cost_table)
    ingredient_lists.append(matches)
    num_ingedients.append(len(matches))
    rating.append(recipe["Stars"])

#one hot
# one hot labels
def one_hot_encode(ingredient_lists, possible_ingredients):
    num = len(possible_ingredients)
    ingredient_matrix = []
    for ing_list in ingredient_lists:
        temp_list = [0]*num
        for ing in ing_list:
            index = np.where(possible_ingredients == ing)[0][0]
            temp_list[index] = 1.
        ingredient_matrix.append(temp_list)
    return ingredient_matrix

def find_ingredients(ingredient_list_onehot, num_ingredients, possible_ingredients):
    ind = (-ingredient_list_onehot).argsort()[:num_ingredients]
    return possible_ingredients[ind]

def back_one_hot(ingredient_list_onehot, possible_ingredients):
    return possible_ingredients[ingredient_list_onehot == 1]

def keep_good(ingredient_lists, cost_table):
    good_ingredient_lists = []
    for ingred_list in ingredient_lists:
        score = []
        for ing in ingred_list:
            score.append(cost_table[ing])
        idx = (-np.array(score)).argsort()[:1]
        new_list = list(np.copy(ingred_list))
        if len(idx) > 0:
            new_list.pop(idx[0])
        good_ingredient_lists.append(new_list)
    return good_ingredient_lists

def calc_carb_loss(output, cost_table):
    """Calculate carbon cost of output. This yields an additional loss."""
    values = np.array(list(cost_table.values()), dtype=np.float32)
    print(type(values))
    return tf.reduce_sum(output * tf.convert_to_tensor(values, dtype=tf.float64))

ingredients_onehot = np.array(one_hot_encode(ingredient_lists, possible_ingredients))


good = np.array(keep_good(ingredient_lists, cost_table))
good_onehot = one_hot_encode(good, possible_ingredients)


split = int(0.8 * len(ingredients_onehot))
train_x = np.array(ingredients_onehot)[:split]
train_l = np.array(good_onehot)[:split]
validate_x = np.array(ingredients_onehot)[split:]
validate_l = np.array(good_onehot)[split:]
print(train_x.shape)

epochs = 2


possible = len(possible_ingredients)
print(possible)

dense_units1 = 150
dense_units2 = 300

latent_units = 200

dense_units3 = 300
dense_units4 = 150
output_units = possible



def autoenc_model_fn(features, mode):

    dense1 = tf.layers.dense(
        inputs=features['x'], units=dense_units1, activation=tf.nn.leaky_relu)

    dropout1 = tf.layers.dropout(inputs=dense1, rate=0.5,
                                training=mode == tf.estimator.ModeKeys.TRAIN)
    
    dense2 = tf.layers.dense(
        inputs=dropout1, units=dense_units2, activation=tf.nn.leaky_relu)

    dropout2 = tf.layers.dropout(inputs=dense2, rate=0.5,
                                training=mode == tf.estimator.ModeKeys.TRAIN)


    latent = tf.layers.dense(
        inputs=dropout2, units=latent_units, activation=tf.nn.leaky_relu)
    
    # Decoder
    latent_output = tf.concat([features["l"], latent], axis=1)
    
    dense3 = tf.layers.dense(
        inputs=latent_output, units=dense_units3, activation=tf.nn.leaky_relu)
    dropout3 = tf.layers.dropout(inputs=dense3, rate=0.5,
                                training=mode == tf.estimator.ModeKeys.TRAIN)
    
    dense4 = tf.layers.dense(
        inputs=dropout3, units=dense_units4, activation=tf.nn.leaky_relu)
    dropout4 = tf.layers.dropout(inputs=dense4, rate=0.5,
                                training=mode == tf.estimator.ModeKeys.TRAIN)
    

    output_layer = tf.layers.dense(
        inputs=dropout4, units=output_units, activation=tf.nn.sigmoid)


    
    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=output_layer)
    
    loss = tf.losses.mean_squared_error(
        labels=features['x'], predictions=output_layer) + 0.01 * calc_carb_loss(output_layer, cost_table)

    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.AdamOptimizer(learning_rate=0.0001)
        train_op = optimizer.minimize(
            loss=loss,
            global_step=tf.train.get_global_step())
        return tf.estimator.EstimatorSpec(
            mode=mode,
            predictions=output_layer,
            loss=loss,
            train_op=train_op)
    
    
    eval_metric_ops = {
        "accuracy": tf.metrics.accuracy(labels=features['x'],
                                        predictions=output_layer)}

    return tf.estimator.EstimatorSpec(
        mode=mode,
        loss=loss,
        eval_metric_ops=eval_metric_ops,
        predictions=output_layer)


config = tf.estimator.RunConfig(
    save_checkpoints_steps=500, keep_checkpoint_max=2)
autoenc = tf.estimator.Estimator(model_fn=autoenc_model_fn, model_dir=out, config=config)


train_input_fn = tf.estimator.inputs.numpy_input_fn(
    x={"x": train_x, "l": train_l},
    batch_size=32,
    num_epochs=None,
    shuffle=True)

train_eval_input_fn = tf.estimator.inputs.numpy_input_fn(
    x={"x": train_x, "l": train_l},
    batch_size=100,
    num_epochs=1,
    shuffle=True)


validate_input_fn = tf.estimator.inputs.numpy_input_fn(
    x={"x": validate_x, "l": validate_l},
    num_epochs=1,
    shuffle=False)


predict_input_fn = tf.estimator.inputs.numpy_input_fn(
    x={"x": ingredients_onehot[60:62], "l": ingredients_onehot[60:62]},
    num_epochs=1,
    shuffle=False)


losses = []
val_loss = []

for i in range(epochs):
    autoenc.train(input_fn=train_input_fn, steps=500)
    #train
    train_results = autoenc.evaluate(input_fn=train_eval_input_fn)
    #validate
    eval_results = autoenc.evaluate(input_fn=validate_input_fn)
    print("Epoch: ", i)
    print("Train_loss: ", train_results['loss'])
    print("Val_loss: ", eval_results['loss'])
    losses.append(train_results['loss'])
    val_loss.append(eval_results['loss'])


print("losses", losses)
print("accuracy", val_loss)

# print training and validation error
plt.plot(np.arange(len(losses)) + 1, losses, 'bo', label='Training loss')
plt.title('Training loss')
plt.xlabel('Epochs ', fontsize=16)
plt.ylabel('Loss', fontsize=16)


plt.plot(np.arange(len(losses)) + 1, val_loss, 'r', label='Validation accuracy')
plt.title('Accuracy')
plt.xlabel('Epochs ', fontsize=16)
plt.ylabel('Accuracy', fontsize=16)
plt.legend()


plt.show()


#predict
predictions = []
prediction = autoenc.predict(input_fn=predict_input_fn)
[predictions.append(pred) for pred in prediction]
print(find_ingredients(predictions[0], num_ingedients[60], possible_ingredients))
print(ingredient_lists[60])
print(good[60])
print(find_ingredients(predictions[1], num_ingedients[61], possible_ingredients))
print(ingredient_lists[61])
print(good[61])
