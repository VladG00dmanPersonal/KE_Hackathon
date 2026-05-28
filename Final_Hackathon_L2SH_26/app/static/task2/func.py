import csv

spb_file = open('/workspaces/KE_Hackathon/Final_Hackathon_L2SH_26/app/static/task2/spb_results.csv', newline='', encoding='cp1251')
reader_spb = csv.DictReader(spb_file, delimiter=';')

moscow_file = open('/workspaces/KE_Hackathon/Final_Hackathon_L2SH_26/app/static/task2/moscow_results.csv', newline='', encoding='cp1251')
reader_moscow = csv.DictReader(moscow_file, delimiter=';')


def get_school(FULL_NAME):
    surname, name, lastname = FULL_NAME.split()
    print(name, surname, lastname)
    for i in reader_spb:
        name_spb = i['Участник'].split('(')
        NAME_SPB = name_spb[0][:-1]
        school_spb = name_spb[1].split(',')[0]
        print(NAME_SPB, school_spb)
        if NAME_SPB == surname + ' ' + name + ' ' + lastname:
            return (school_spb, 'Санкт-Петербург')
    for i in reader_moscow:
        # print(surname + ' ' + name)
        if i['Участник'] == surname + ' ' + name:
            return (i['Школа'], 'Москва')
    return (None, None)

print(get_school('Епифанов Ярослав Николаевич'))