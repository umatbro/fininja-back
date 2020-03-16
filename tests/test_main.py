import main
import pytest


@pytest.mark.parametrize('value_to_add, current_cell_value, expected_result', [
    (10, '', '=+10,00'),
    (10.5, '', '=+10,50'),
    (5, '10', '=10+5,00'),
    (3.45, '=2+1', '=2+1+3,45'),
])
def test_add_value_to_formula(value_to_add, current_cell_value, expected_result):
    assert main.add_value_to_formula(value_to_add, current_cell_value) == expected_result
