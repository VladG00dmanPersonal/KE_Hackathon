import csv

spb_file = open('spb_results.csv', newline='', encoding='cp1251')
reader_spb = csv.DictReader(spb_file, delimiter=';')

moscow_file = open('moscow_results.csv', newline='', encoding='cp1251')
reader_moscow = csv.DictReader(moscow_file, delimiter=';')


def get_school(FULL_NAME):
    surname, name, lastname = FULL_NAME.split()
    print(name, surname, lastname)
    for i in reader_spb:
        if i['Участник'] == surname + ' ' + name:
            return (i['Школа'], 'Санкт-Петербург')
    for i in reader_moscow:
        # print(surname + ' ' + name)
        if i['Участник'] == surname + ' ' + name:
            return (i['Школа'], 'Москва')
    return (None, None)

print(get_school('Чеботаренко Никита 1123'))