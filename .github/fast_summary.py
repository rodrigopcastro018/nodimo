#!/usr/bin/env python3

import os

def clean_string(string):
    # Remove null bytes (\x00) and double newline character (\n\n)
    new_string = string.replace('\x00', '')

    while '\n\n' in new_string:
        new_string = new_string.replace('\n\n', '\n')
    
    return new_string


def get_test_results():

    with open('test_results/mypy_result.txt', 'r') as mypy_result_file:
        # Get full mypy result
        full_mypy_result = clean_string(mypy_result_file.read())

        # Get mypy status
        mypy_result = full_mypy_result.split('\n')[-2]

        if 'no issues found' in mypy_result:
            is_mypy_successful = True
        else:
            is_mypy_successful = False

    with open('test_results/pytest_result.txt', 'r') as pytest_result_file:
        # Get full pytest result
        full_pytest_result = clean_string(pytest_result_file.read())
        full_pytest_result_splitted = full_pytest_result.split('\n')

        # Get pytest status
        pytest_result = full_pytest_result_splitted[-2]

        if 'failed' in pytest_result:
            is_pytest_successful = False
        else:
            is_pytest_successful = True

        # Get coverage value
        coverage_value = full_pytest_result_splitted[-3].split()[-1]

    return is_mypy_successful, is_pytest_successful, coverage_value

def write_test_results():

    (is_mypy_successful,
     is_pytest_successful,
     coverage_value) = get_test_results()
    
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary_env_var:
        print(f'| linux-latest_dependencies '
              f'| {is_mypy_successful} '
              f'| {is_pytest_successful} '
              f'| {coverage_value} |',
              file=summary_env_var)

if __name__ == '__main__':
    write_test_results()

# | **Case** | mypy | pytest | coverage |
# | :------- | :--: | :----: | :------: |

# | {} | {} | {} | {} |

# "| **Case** | mypy | pytest | coverage |\n| :------- | :--: | :----: | :------: |\n|    a     |  b   |   c    |    d     |"