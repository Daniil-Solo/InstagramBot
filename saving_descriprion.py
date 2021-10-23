import csv
import re
import datetime


def save_description(text):
    only_letters_and_digits_text = ' '.join(re.findall("[A-Za-zЁёА-Яа-я\d#]+", text))
    only_lower_register_text = only_letters_and_digits_text.lower()
    row = [only_lower_register_text, "Заполнить"]
    with open('.ipynb_checkpoints/data.csv', 'a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(row)


def save_statistics(count_list):
    current_date = datetime.datetime.now()
    row = [str(current_date)]
    for count in count_list:
        row.append(str(count))

    with open('filter_data.csv', 'a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(row)
