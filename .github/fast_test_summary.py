#!/usr/bin/env python3

import os
import sys


def clean_string(string):
    # Remove null bytes (\x00) and double newline character (\n\n)
    new_string = string.replace('\x00', '')

    while '\n\n' in new_string:
        new_string = new_string.replace('\n\n', '\n')
    
    return new_string


def get_test_result(file_path):
    with open('test_results/' + file_path, 'r') as result_file:
        # Get full result
        full_result = clean_string(result_file.read())

        # Get result in final line
        result = full_result.split('\n')[-2]

        return result


def get_test_status():
    # Get mypy status
    mypy_result = get_test_result('mypy_result.txt')

    if 'no issues found' in mypy_result:
        mypy_status = ':heavy_check_mark:'
    else:
        mypy_status = ':x:'

    # Get pytest status
    pytest_result = get_test_result('pytest_result.txt')

    if 'failed' in pytest_result:
        pytest_status = ':x:'
    else:
        pytest_status = ':heavy_check_mark:'

    # Get coverage status
    coverage_status = get_test_result('coverage_result.txt').split()[-1]

    return mypy_status, pytest_status, coverage_status


def write_test_results():

    job_name = sys.argv[1]

    (mypy_status,
     pytest_status,
     coverage_status) = get_test_status()

    if 'GITHUB_STEP_SUMMARY' in os.environ:
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary_env_var:
            print(f'| {job_name} '
                  f'| {mypy_status} '
                  f'| {pytest_status} '
                  f'| {coverage_status} |',
                  file=summary_env_var)


if __name__ == '__main__':
    write_test_results()
