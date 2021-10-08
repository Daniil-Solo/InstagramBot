import csv
import re


def save_description(text):
    only_letters_and_digits_text = ' '.join(re.findall("[А-Яа-я\d]+", text))
    only_lower_register_text = only_letters_and_digits_text.lower()
    row = [only_lower_register_text, "Заполнить"]
    with open('data.csv', 'a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(row)
