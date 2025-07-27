import os
from os.path import isfile
from os import listdir
from pickle import dump, load
from spike_model import SpikeModel
from pandas import read_csv, DataFrame, concat

def load_data_in_pandas(directory=None):
    try:
        files = [os.path.join(directory, 'data', f) for f in listdir(os.path.join(directory, 'data'))
                 if isfile(os.path.join(directory, 'data', f)) and f.endswith('.csv.gz')]
    except:
        files = [os.path.join(directory, f) for f in listdir(os.path.join(directory))
                 if isfile(os.path.join(directory, f)) and f.endswith('.csv.gz')]
    df_dict = {}
    for file in files:
        table_name = file.split("/")[-1].split(".")[0].split("___")[0]
        try:
            df_dict[table_name].append(read_csv(file))
        except:
            df_dict[table_name] = [read_csv(file)]
    for k, v in df_dict.items():
        df_dict[k] = concat(v)
    return df_dict


def process(input_directory=None, output_directory=None):

    # Read locally (inputs folder)
    data_dict = load_data_in_pandas(input_directory)
    d = data_dict['d_train']
    Y = d['TARGET_VARIABLE'].copy()
    X = d.drop(columns=['TARGET_VARIABLE', 'OBS_DATE', 'Ticker']).fillna(value=0)

    # Process
    clf = SpikeModel(direction=-1, intensity=0.05, sample_fraction=0.1)
    trained_model = clf.fit(X, Y)

    # Write locally (artifacts + results - output folder)
    pickle_file_name = os.path.join(output_directory, 'spike_model.pkl')
    with open(pickle_file_name, 'wb') as f:
        dump(trained_model, f)


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
    trained_model_filename = os.path.join(input_directory, 'spike_model.pkl')
    with open(trained_model_filename, 'rb') as f:
        trained_model = load(f)

    # Predict
    tmp = DataFrame(trained_model.predict_proba(d))
    tmp.rename(columns={0:'pred'}, inplace=True)
    tmp['OBS_DATE'] = obs_date
    tmp['Ticker'] = Ticker
    predictions = tmp[['OBS_DATE', 'Ticker', 'pred']]

    prediction_filename = os.path.join(output_directory, 'predictions.csv')
    DataFrame(predictions).to_csv(prediction_filename, index=False)