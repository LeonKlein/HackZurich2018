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

#def keep_good(ingredients_onehot, cost_table,):


ingredients_onehot = np.array(one_hot_encode(ingredient_lists, possible_ingredients))
print(ingredients_onehot.shape)


split = int(0.8 * len(ingredients_onehot))
train_x = np.array(ingredients_onehot[:split])
validate_x = ingredients_onehot[split:]
print(train_x.shape)

epochs = 50


possible = len(possible_ingredients)
print(possible)

dense_units1 = 100
dense_units2 = 300

latent_units = 100

dense_units3 = 300
dense_units4 = 100
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

    # conditional autoencoder
    latent_input = tf.concat([features["l"], dropout2], axis=-1)

    latent = tf.layers.dense(
        inputs=latent_input, units=latent_units, activation=tf.nn.leaky_relu)
    
    # Decoder

    dense3 = tf.layers.dense(
        inputs=latent, units=dense_units3, activation=tf.nn.leaky_relu)
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
        labels=features['x'], predictions=output_layer)

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
    x={"x": train_x, "l": train_x},
    batch_size=32,
    num_epochs=None,
    shuffle=True)

train_eval_input_fn = tf.estimator.inputs.numpy_input_fn(
    x={"x": train_x, "l": train_x},
    batch_size=100,
    num_epochs=1,
    shuffle=True)


validate_input_fn = tf.estimator.inputs.numpy_input_fn(
    x={"x": validate_x, "l": validate_x},
    num_epochs=1,
    shuffle=False)


predict_input_fn = tf.estimator.inputs.numpy_input_fn(
    x={"x": ingredients_onehot[:2], "l": ingredients_onehot[:2]},
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
[print(predictions.append(pred)) for pred in prediction]
print(find_ingredients(predictions[0], num_ingedients[0], possible_ingredients))
print(ingredient_lists[0])
print(find_ingredients(predictions[1], num_ingedients[1], possible_ingredients))
print(ingredient_lists[1])
