import os
from os.path import isfile
from os import listdir
from pandas import read_csv, concat


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
