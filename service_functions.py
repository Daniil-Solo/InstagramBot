import csv
import datetime
import json
from yaml import load, SafeLoader


def get_parameters(mode_name: str) -> dict or None:
    try:
        filename = load(open("schedule.yml"), Loader=SafeLoader).get("parameters_filename")
        with open(filename, 'r', encoding="UTF-8") as read_file:
            mode = json.load(read_file).get(mode_name)
        parameters = mode.get('parameters')
        for key in parameters:
            parameter = parameters.get(key)
            parameters[key] = parameter.get('value')
        return parameters
    except FileNotFoundError:
        return None


def get_account(alias: str) -> dict or None:
    try:
        filename = load(open("schedule.yml"), Loader=SafeLoader).get("auth_filename")
        with open(filename, 'r') as read_file:
            auth_accounts = json.load(read_file)
        for account in auth_accounts:
            aliases = account.get("alias") or ''
            if alias in aliases:
                return account
        return None
    except FileNotFoundError:
        return None


def save_statistics(count_list: list):
    current_date = datetime.datetime.now()
    row = [str(current_date)]
    for count in count_list:
        row.append(str(count))

    with open('filter_data.csv', 'a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(row)
