from sklearn.metrics import mean_absolute_percentage_error


def official_evaluation_metric(target, predictions):
    return {'MAPE': mean_absolute_percentage_error(target, predictions)}
