import os
from aix import load_data_in_pandas
import torch.nn as nn
from torch import flatten, save, load, Tensor, squeeze, sigmoid, no_grad
import torch.optim as optim
from pandas import DataFrame


class Net(nn.Module):
    def __init__(self, shape):
        super().__init__()
        self.fc1 = nn.Linear(shape, 1)

    def forward(self, x):
        x = flatten(x, 1)  # flatten all dimensions except batch
        x = sigmoid(self.fc1(x))
        return x


def process(input_directory=None, output_directory=None):

    # Read locally (inputs folder)
    data_dict = load_data_in_pandas(input_directory)
    train_df = data_dict['d_train']
    Y = train_df['TARGET_VARIABLE'].copy()
    X = train_df.drop(columns=['TARGET_VARIABLE', 'OBS_DATE', 'Ticker']).fillna(value=0)

    net = Net(X.shape[1])

    criterion = nn.BCELoss()
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

    for epoch in range(2):  # loop over the dataset multiple times

        optimizer.zero_grad()  # Setting our stored gradients equal to zero
        outputs = net(Tensor(X.values))
        loss = criterion(squeeze(outputs), Tensor(Y.values))

        loss.backward()  # Computes the gradient of the given tensor w.r.t. the weights/bias

        optimizer.step()  # Updates weights and biases with the optimizer (SGD)

    # Write artifact
    model_name = os.path.join(output_directory, 'torch_model.pth')
    save(net.state_dict(), model_name)


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

    trained_net = Net(d.shape[1])
    trained_model_name = os.path.join(input_directory, 'torch_model.pth')
    trained_state_dict = load(trained_model_name)
    trained_net.load_state_dict(trained_state_dict)

    # Predict
    with no_grad():
        tmp = DataFrame(trained_net(Tensor(d.values)))
    tmp.rename(columns={0:'pred'}, inplace=True)
    tmp['OBS_DATE'] = obs_date
    tmp['Ticker'] = Ticker
    predictions = tmp[['OBS_DATE', 'Ticker', 'pred']]

    # Write
    prediction_filename = os.path.join(output_directory, 'predictions.csv')
    DataFrame(predictions).to_csv(prediction_filename, index=False)
