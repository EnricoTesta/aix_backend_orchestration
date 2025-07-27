import os
from aix import load_data_in_pandas
import tensorflow as tf
from pandas import DataFrame


def process(input_directory=None, output_directory=None):

    # Read locally (inputs folder)
    data_dict = load_data_in_pandas(input_directory)
    train_df = data_dict['d_train']
    Y = train_df['TARGET_VARIABLE'].copy()
    X = train_df.drop(columns=['TARGET_VARIABLE', 'OBS_DATE', 'Ticker']).fillna(value=0)

    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(2, input_shape=(X.shape[1],), activation='relu'),
        tf.keras.layers.Softmax()
    ])

    model.compile(optimizer='adam',
                  loss=tf.keras.losses.BinaryCrossentropy(),
                  metrics=['accuracy'])

    model.fit(X.values, Y.values, epochs=10)

    # Write artifact
    model_name = os.path.join(output_directory, 'keras_model.h5')
    model.save(model_name)


def transform(input_directory=None, output_directory=None):

    # Read from input
    data_dict = load_data_in_pandas(input_directory)
    if 'd_inference' in data_dict.keys():
        d = data_dict['d_inference']
    else:
        d = data_dict['d_holdout']
    obs_date = d['OBS_DATE'].copy().reset_index(drop=True)
    Ticker = d['Ticker'].copy().reset_index(drop=True)
    d = d.drop(columns=['OBS_DATE', 'Ticker']).fillna(value=0)

    trained_model_name = os.path.join(input_directory, 'keras_model.h5')
    trained_model = tf.keras.models.load_model(trained_model_name)

    # Predict
    tmp = DataFrame(trained_model.predict(d))
    tmp.rename(columns={1:'pred'}, inplace=True)
    tmp['OBS_DATE'] = obs_date
    tmp['Ticker'] = Ticker
    predictions = tmp[['OBS_DATE', 'Ticker', 'pred']]

    # Write
    prediction_filename = os.path.join(output_directory, 'predictions.csv')
    DataFrame(predictions).to_csv(prediction_filename, index=False)
