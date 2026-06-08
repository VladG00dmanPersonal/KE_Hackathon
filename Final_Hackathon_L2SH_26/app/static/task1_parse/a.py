import json

import csv

def get_school(FULL_NAME):
    spb_file = open('/workspaces/KE_Hackathon/Final_Hackathon_L2SH_26/app/static/task2/spb_results.csv', newline='', encoding='cp1251')
    reader_spb = csv.DictReader(spb_file, delimiter=';')

    moscow_file = open('/workspaces/KE_Hackathon/Final_Hackathon_L2SH_26/app/static/task2/moscow_results.csv', newline='', encoding='cp1251')
    reader_moscow = csv.DictReader(moscow_file, delimiter=';')

    surname, name, lastname = FULL_NAME.split()
    # print(name, surname, lastname)
    for i in reader_spb:
        name_spb = i['Участник'].split('(')
        NAME_SPB = name_spb[0][:-1]
        school_spb = name_spb[1].split(',')[0]
        # print(NAME_SPB, school_spb)
        if NAME_SPB == surname + ' ' + name + ' ' + lastname:
            return (school_spb, 'Санкт-Петербург')
    for i in reader_moscow:
        # print(surname + ' ' + name)
        if i['Участник'] == surname + ' ' + name:
            return (i['Школа'], 'Москва')
    return (None, None)

schools_moscow = set()
schools_spb = set()
other_schools = set()
A = json.load(open("/workspaces/KE_Hackathon/Final_Hackathon_L2SH_26/app/static/task1_parse/parsed_results.json", "r", encoding="utf-8"))
for i in A["Второй тур"]["300"]:
    uch = i["Участник"]
    school, city = get_school(uch)
    if city == "Москва":
        schools_moscow.add(school)
    elif city == "Санкт-Петербург":
        schools_spb.add(school)
    else:
        other_schools.add(school)

w = open("/workspaces/KE_Hackathon/Final_Hackathon_L2SH_26/app/static/task1_parse/schools_moscow.txt", "w", encoding="utf-8")
for i in schools_moscow:
    w.write(i + "\n")
w.close()
w_new = open("/workspaces/KE_Hackathon/Final_Hackathon_L2SH_26/app/static/task1_parse/schools_spb.txt", "w", encoding="utf-8")
for i in schools_spb:
    w_new.write(i + "\n")
w_new.close()