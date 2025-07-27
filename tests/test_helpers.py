from helpers import *
from fixtures import *


def test_list2dbstr(db_list):
    actual_output = list2dbstr(db_list)
    expected_output = "(\'ID001\', \'#\', 1, NULL, \'2000-01-01 18:15:00\')"
    assert actual_output == expected_output


def test_build_metamodel(predictions_2models_binary, target_binary):
    actual_fun, actual_weights = build_metamodel(predictions_2models_binary, target_binary)
    expected_weights = {'Model_1': 0.0, 'Model_2': 1.0}
    assert actual_weights == expected_weights
