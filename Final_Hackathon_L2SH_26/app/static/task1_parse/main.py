import os
import re
import csv
import json

base_dir = '/workspaces/KE_Hackathon/Материалы'
tours = {
    'Первый тур': [120, 150, 180, 190, 200, 220, 240, 260, 280, 295, 300],
    'Второй тур': [30, 45, 75, 90, 95, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 280, 290, 295, 300]
}

def parse_html_table(filepath):
    if not os.path.exists(filepath):
        print(f"Файл не найден: {filepath}")
        return []
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    tbody_match = re.search(r'<tbody>(.*?)</tbody>', content, re.DOTALL | re.IGNORECASE)
    if not tbody_match:
        return []
        
    tbody = tbody_match.group(1)
    trs = re.findall(r'<tr[^>]*>(.*?)</tr>', tbody, re.DOTALL | re.IGNORECASE)
    
    parsed_data = []
    
    for tr in trs:
        tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.DOTALL | re.IGNORECASE)
        tds_clean = [re.sub(r'<[^>]*>', '', td).strip() for td in tds]
        
        if len(tds_clean) >= 7:
            rank = tds_clean[0]
            party = tds_clean[1]
            t1, t2, t3, t4 = tds_clean[2:6]
            total = tds_clean[-1]
            
            m = re.match(r'^(.*?)\s*\((.*?),\s*(\d+)\s*класс\)$', party)
            if m:
                name, region, grade = m.groups()
            else:
                name, region, grade = party, '', ''
                
            parsed_data.append({
                'Место': rank,
                'Участник': name,
                'Регион': region,
                'Класс': grade,
                'Задача 1': t1,
                'Задача 2': t2,
                'Задача 3': t3,
                'Задача 4': t4,
                'Итог': total
            })
            
    return parsed_data

def main():
    all_results = {}
    
    for tour_name, minutes_list in tours.items():
        all_results[tour_name] = {}
        print(f"Парсинг: {tour_name}")
        
        for minutes in minutes_list:
            filepath = os.path.join(base_dir, tour_name, f"{minutes}.html")
            data = parse_html_table(filepath)
            all_results[tour_name][minutes] = data
            print(f"  [{minutes} мин.] Данных извлечено: {len(data)} строк")

    output_json = os.path.join(os.path.dirname(__file__), 'parsed_results.json')
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)
    print(f"Данные сохранены в {output_json}")

if __name__ == '__main__':
    main()
    