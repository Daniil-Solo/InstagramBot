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
            aliases = account.get("alias") or []
            if alias in aliases:
                del account['alias']
                return account
        return None
    except FileNotFoundError:
        return None
