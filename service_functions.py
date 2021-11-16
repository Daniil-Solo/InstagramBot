import csv
import datetime
import json
import time

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
        satisfied_accounts = []
        for account in auth_accounts:
            aliases = account.get("alias") or ''
            if alias in aliases:
                if not account.get("last_time"):
                    account["last_time"] = 0
                satisfied_accounts.append(account)
        if len(satisfied_accounts) != 0:
            satisfied_accounts = sorted(satisfied_accounts, key=lambda a: a.get("last_time"))
            return satisfied_accounts[0]
        return None
    except FileNotFoundError:
        return None


def update_account_last_time(account: dict) -> None:
    try:
        filename = load(open("schedule.yml"), Loader=SafeLoader).get("auth_filename")
        with open(filename, 'r') as read_file:
            auth_accounts = json.load(read_file)
        for auth_account in auth_accounts:
            if account.get('login') == auth_account.get('login') and \
                    account.get('password') == auth_account.get('password'):
                auth_account['last_time'] = int(datetime.datetime.timestamp(datetime.datetime.now()))
        with open(filename, 'w') as write_file:
            json.dump(auth_accounts, write_file)
    except FileNotFoundError:
        pass


def save_statistics(count_list: list):
    current_date = datetime.datetime.now()
    row = [str(current_date)]
    for count in count_list:
        row.append(str(count))

    with open('filter_data.csv', 'a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(row)
