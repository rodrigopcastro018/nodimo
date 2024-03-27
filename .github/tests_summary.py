#!/usr/bin/env python3

import os
import json
import xml.etree.ElementTree as ET


os.chdir('tests_results')


def get_pytest_status(results_folder, filename='pytest_result.xml'):
    pytest_result = ET.parse(results_folder + '/' + filename)
    root = pytest_result.getroot()

    number_of_errors = int(root[0].get('errors'))
    number_of_failures = int(root[0].get('failures'))

    if number_of_errors == 0 and number_of_failures == 0:
        pytest_status = ':heavy_check_mark:'
    else:
        pytest_status = ':x:'
    
    return pytest_status


def get_coverage_status(results_folder, filename='coverage_result.json'):
    with open(results_folder + '/' + filename) as coverage_result_file:
        coverage_result = json.load(coverage_result_file)
    
    coverage_status = coverage_result['totals']['percent_covered_display'] + '%'

    return coverage_status


def get_mypy_status(results_folder, filename='mypy_result.xml'):
    mypy_result = ET.parse(results_folder + '/' + filename)
    root = mypy_result.getroot()

    number_of_errors = int(root.get('errors'))
    number_of_failures = int(root.get('failures'))

    if number_of_errors == 0 and number_of_failures == 0:
        mypy_status = ':heavy_check_mark:'
    else:
        mypy_status = ':x:'
    
    return mypy_status


def write_table_header():
    if 'GITHUB_STEP_SUMMARY' in os.environ:
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary_env_var:
            print('| **Case** | **mypy** | **pytest** | **coverage** |', file=summary_env_var)
            print('| :------- | :------: | :--------: | :----------: |', file=summary_env_var)
    # For debugging
    else:
        print('| **Case** | **mypy** | **pytest** | **coverage** |')
        print('| :------- | :------: | :--------: | :----------: |')


def write_tests_results():

    for folder_name in os.listdir():

        job_name = folder_name[8:]

        mypy_status = get_mypy_status(folder_name)
        pytest_status = get_pytest_status(folder_name)
        coverage_status = get_coverage_status(folder_name)

        if 'GITHUB_STEP_SUMMARY' in os.environ:
            with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary_env_var:
                print(f'| {job_name} '
                      f'| {mypy_status} '
                      f'| {pytest_status} '
                      f'| {coverage_status} |',
                      file=summary_env_var)
        # For debugging
        else:
            print(f'| {job_name} '
                  f'| {mypy_status} '
                  f'| {pytest_status} '
                  f'| {coverage_status} |')


if __name__ == '__main__':
    write_table_header()
    write_tests_results()
