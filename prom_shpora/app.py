from flask import Flask, render_template, request, url_for
import csv
import json

app = Flask(__name__)

@app.route('/')
def index():
    return "Привет, это базовый Flask!"

@app.route('/hello')
def hello():
    # Ищет файл hello.html внутри папки templates/
    return render_template('hello.html')

@app.route('/user')
def user_page():
    # 1. Создаем словарь с данными
    context = {
        'username': 'Алексей',
        'role': 'Администратор',
        'score': 95
    }
    # 2. Распаковываем словарь в функцию с помощью **
    return render_template('user.html', **context)

@app.route('/list')
def show_list():
    items = ['Яблоко', 'Банан', 'Апельсин']
    is_logged_in = True
    return render_template('list.html', items=items, is_logged_in=is_logged_in)

# <name> - строка, <int:age> - целое число
@app.route('/profile/<name>/<int:age>')
def profile(name, age):
    # Генерация ссылки на эту же страницу с другими параметрами
    link_to_admin = url_for('profile', name='Admin', age=30)
    
    return render_template('profile.html', name=name, age=age, link=link_to_admin)

@app.route('/submit', methods=['GET', 'POST'])
def submit_form():
    message = ""
    if request.method == 'POST':
        # Получаем данные из полей input по атрибуту name
        user_name = request.form.get('username')
        user_email = request.form.get('email')
        message = f"Спасибо, {user_name}! Мы отправили код на {user_email}"
        
    return render_template('form.html', message=message)

@app.route('/csv_demo')
def csv_demo():
    filename = 'data.csv'
    
    # --- ЗАПИСЬ В CSV ---
    # newline='' предотвращает появление пустых строк между записями в Windows
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Имя', 'Возраст', 'Город'])          # Заголовки
        writer.writerow(['Иван', 16, 'Москва'])               # Данные
        writer.writerow(['Мария', 17, 'Санкт-Петербург'])

    # --- ЧТЕНИЕ ИЗ CSV ---
    data = []
    with open(filename, 'r', encoding='utf-8') as file:
        # DictReader превращает каждую строку в словарь, где ключи - это заголовки
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row) # data будет выглядеть как [{'Имя': 'Иван', ...}, ...]
            
    return render_template('csv_view.html', data=data)

@app.route('/json_demo')
def json_demo():
    filename = 'data.json'
    
    # --- ЗАПИСЬ В JSON ---
    my_data = {
        "students": [
            {"name": "Олег", "grade": 5},
            {"name": "Анна", "grade": 4}
        ]
    }
    with open(filename, 'w', encoding='utf-8') as file:
        # ensure_ascii=False сохраняет русские буквы как есть, а не как \u0410
        # indent=4 делает файл красивым и читаемым (с отступами)
        json.dump(my_data, file, ensure_ascii=False, indent=4)

    # --- ЧТЕНИЕ ИЗ JSON ---
    with open(filename, 'r', encoding='utf-8') as file:
        loaded_data = json.load(file) # loaded_data станет обычным Python-словарем/списком
        
    return render_template('json_view.html', students=loaded_data['students'])

if __name__ == '__main__':
    # debug=True позволяет видеть ошибки в браузере и автоперезагружать сервер
    app.run(debug=True) 