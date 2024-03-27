#!/usr/bin/env python3

import os
import sys
import json
import xml.etree.ElementTree as ET


test_results_path = 'tests_results/'


def get_pytest_status(filename='pytest_result.xml'):
    pytest_result = ET.parse(test_results_path + filename)
    root = pytest_result.getroot()

    number_of_errors = int(root[0].get('errors'))
    number_of_failures = int(root[0].get('failures'))

    if number_of_errors == 0 and number_of_failures == 0:
        pytest_status = ':heavy_check_mark:'
    else:
        pytest_status = ':x:'
    
    return pytest_status


def get_coverage_status(filename='coverage_result.json'):
    with open(test_results_path + filename) as coverage_result_file:
        coverage_result = json.load(coverage_result_file)
    
    coverage_status = coverage_result['totals']['percent_covered_display'] + '%'

    return coverage_status


def get_mypy_status(filename='mypy_result.xml'):
    mypy_result = ET.parse(test_results_path + filename)
    root = mypy_result.getroot()

    number_of_errors = int(root.get('errors'))
    number_of_failures = int(root.get('failures'))

    if number_of_errors == 0 and number_of_failures == 0:
        mypy_status = ':heavy_check_mark:'
    else:
        mypy_status = ':x:'
    
    return mypy_status


def write_test_results():

    job_name = sys.argv[1]

    mypy_status = get_mypy_status()
    pytest_status = get_pytest_status()
    coverage_status = get_coverage_status()

    if 'GITHUB_STEP_SUMMARY' in os.environ:
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary_env_var:
            print(f'| {job_name} '
                  f'| {mypy_status} '
                  f'| {pytest_status} '
                  f'| {coverage_status} |',
                  file=summary_env_var)


if __name__ == '__main__':
    write_test_results()
