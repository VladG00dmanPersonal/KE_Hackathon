Отлично! Давай сделаем максимально мощную и подробную шпаргалку. Я объединил темы так, чтобы примеры из одной плавно переходили в другую (например, читаем данные из SQLite и строим по ним график в Matplotlib).

---

# 📊 ШПАРГАЛКА: Matplotlib + SQLiteStudio + SQL

## 📌 Единая схема базы данных (для всех примеров)
Договоримся, что во всех SQL-запросах и графиках мы используем эту БД:
```
📁 school.db
├── classes (id INTEGER PRIMARY KEY, name TEXT)
├── students (id INTEGER PRIMARY KEY, full_name TEXT, age INTEGER, class_id INTEGER)
├── subjects (id INTEGER PRIMARY KEY, title TEXT)
└── grades (id INTEGER PRIMARY KEY, student_id INTEGER, subject_id INTEGER, score INTEGER, exam_date DATE)
```

---

# 🟢 ЧАСТЬ 1. Библиотека `matplotlib`

### ⚙️ 1.1. Базовая настройка (ОБЯЗАТЕЛЬНО в начале файла!)
*Без этих строк русские буквы будут отображаться как квадратики.*

```python
import matplotlib.pyplot as plt
import numpy as np

# Настройка поддержки русского языка
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['axes.unicode_minus'] = False  # чтобы минус показывался нормально
```

---

### 📈 1.2. Линейный график (`plot`) — тренд изменения величин
```python
months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май']
temperature = [-5, -3, 2, 10, 18]

plt.figure(figsize=(10, 6))  # Размер фигуры в дюймах (ширина, высота)

# linewidth - толщина линии, marker - точки на графике, linestyle - стиль линии
# color - цвет (можно 'red', '#FF5733', 'c' для cyan)
plt.plot(months, temperature, 
         color='blue', 
         linewidth=2.5, 
         marker='o', 
         markersize=8,
         linestyle='--',
         label='Температура')

plt.title('Изменение температуры по месяцам', fontsize=16, fontweight='bold')
plt.xlabel('Месяц', fontsize=12)
plt.ylabel('Температура (°C)', fontsize=12)
plt.grid(True, linestyle=':', alpha=0.7)  # Сетка с прозрачностью
plt.legend(loc='upper left')  # Легенда в левом верхнем углу
plt.tight_layout()  # Автоматическая подгонка отступов

# Сохранение графика в файл (dpi - качество)
plt.savefig('temperature.png', dpi=300, bbox_inches='tight')
plt.show()
```

---

### 📊 1.3. Столбчатая диаграмма (`bar` и `barh`) — сравнение величин
```python
subjects = ['Математика', 'Физика', 'Информатика', 'История']
avg_scores = [4.5, 4.2, 4.8, 3.9]
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']

fig, axes = plt.subplots(1, 2, figsize=(14, 5))  # 1 строка, 2 столбца графиков

# ВЕРТИКАЛЬНЫЕ СТОЛБЦЫ (слева)
axes[0].bar(subjects, avg_scores, color=colors, edgecolor='black', linewidth=1.2)
axes[0].set_title('Средний балл по предметам')
axes[0].set_ylabel('Балл')
axes[0].set_ylim(0, 5)  # Ограничение оси Y

# Добавим подписи значений НАД столбцами
for i, v in enumerate(avg_scores):
    axes[0].text(i, v + 0.1, f'{v:.1f}', ha='center', fontweight='bold')

# ГОРИЗОНТАЛЬНЫЕ СТОЛБЦЫ (справа) — barh = bar horizontal
axes[1].barh(subjects, avg_scores, color=colors, height=0.6)
axes[1].set_title('Горизонтальная диаграмма')
axes[1].set_xlabel('Балл')

plt.tight_layout()
plt.show()
```

---

### 🥧 1.4. Круговая диаграмма (`pie`) — доли целого
```python
classes = ['9А', '9Б', '9В', '10А']
students_count = [25, 28, 22, 30]
colors_pie = ['gold', 'lightcoral', 'lightskyblue', 'lightgreen']
explode = [0.05, 0.05, 0.05, 0.15]  # "Выдвинуть" 10А сильнее остальных

plt.figure(figsize=(8, 8))
plt.pie(students_count, 
        labels=classes,           # Подписи
        autopct='%1.1f%%',        # Подпись процентами (1 знак после запятой)
        startangle=90,            # Начать с верха
        colors=colors_pie,
        explode=explode,          # Выделение сектора
        shadow=True,              # Тень
        textprops={'fontsize': 12})

plt.title('Распределение учеников по классам')
plt.axis('equal')  # Делает круг кругом, а не овалом
plt.show()
```

---

### 📉 1.5. Гистограмма (`hist`) — распределение значений
```python
# 100 случайных оценок от 20 до 100
np.random.seed(42)
scores = np.random.randint(20, 100, 100)

plt.figure(figsize=(10, 6))

# bins - количество столбцов, alpha - прозрачность, edgecolor - границы
plt.hist(scores, bins=15, color='steelblue', edgecolor='black', alpha=0.8)

# Добавим среднее значение как вертикальную линию
plt.axvline(np.mean(scores), color='red', linestyle='dashed', linewidth=2, 
            label=f'Средний балл: {np.mean(scores):.1f}')

plt.title('Распределение баллов за экзамен')
plt.xlabel('Балл')
plt.ylabel('Количество учеников')
plt.legend()
plt.grid(axis='y', alpha=0.7)
plt.show()
```

---

### 🔵 1.6. Точечный график (`scatter`) — корреляция между двумя величинами
```python
study_hours = [2, 3, 5, 1, 4, 6, 3, 7, 2, 5]
exam_score = [55, 62, 78, 45, 70, 88, 65, 95, 52, 82]
classes_num = [9, 9, 10, 9, 10, 11, 10, 11, 9, 10]  # Размер точек

plt.figure(figsize=(10, 6))
# s - размер точек, c - цвет, alpha - прозрачность, cmap - цветовая схема
scatter = plt.scatter(study_hours, exam_score, 
                      s=[c*30 for c in classes_num],  # размер зависит от класса
                      c=exam_score, 
                      cmap='viridis', 
                      alpha=0.7,
                      edgecolor='black')

plt.colorbar(scatter, label='Экзаменационный балл')  # Цветовая легенда
plt.title('Зависимость оценки от часов подготовки')
plt.xlabel('Часы подготовки в день')
plt.ylabel('Балл на экзамене')
plt.grid(True)
plt.show()
```

---

### 🎨 1.7. Несколько графиков в одном (`subplots`) — сравнение
```python
fig, axes = plt.subplots(2, 2, figsize=(12, 10))  # Сетка 2x2

# График 1 (верхний левый)
axes[0, 0].plot([1, 2, 3], [10, 20, 15], 'r-o')
axes[0, 0].set_title('График 1')

# График 2 (верхний правый)
axes[0, 1].bar(['A', 'B', 'C'], [5, 8, 3], color='orange')
axes[0, 1].set_title('График 2')

# График 3 (нижний левый)
axes[1, 0].scatter([1, 2, 3, 4], [1, 4, 2, 3], c='green')
axes[1, 0].set_title('График 3')

# График 4 (нижний правый) - скрыт
axes[1, 1].pie([30, 40, 30], labels=['X', 'Y', 'Z'])
axes[1, 1].set_title('График 4')

plt.suptitle('Дашборд из 4 графиков', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.show()
```

---

# 🟡 ЧАСТЬ 2. SQLiteStudio — графический клиент для БД

### 🚀 2.1. Установка и создание БД (пошагово)
1. Скачай с [sqlitestudio.pl](https://sqlitestudio.pl/) (портативная версия — просто распакуй).
2. Запусти `SQLiteStudio.exe`.
3. **База данных → Добавить базу данных** (или `Ctrl+O`).
4. Выбери папку и имя файла: `school.db` → **Создать**.
5. В левом дереве появится `school.db` — кликай правой кнопкой → **Открыть**.

---

### 🏗️ 2.2. Создание таблицы (3 способа)

**Способ А. Через визуальный редактор (рекомендую на экзамене):**
1. Правой кнопкой по БД → **Создать таблицу**.
2. Вводишь имя таблицы: `students`.
3. Нажимаешь **+** для добавления столбцов:
   - `id` → Тип: `INTEGER` → Галочки: `Primary Key` и `Autoincrement` ✅
   - `full_name` → Тип: `TEXT` → `Not NULL` ✅
   - `age` → Тип: `INTEGER`
   - `class_id` → Тип: `INTEGER`
4. Жмешь **галочку** (Применить) вверху → готово!

**Способ Б. SQL-запросом (вкладка "SQL Editor"):**
```sql
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    age INTEGER CHECK(age > 0 AND age < 100),
    class_id INTEGER,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL
);
```

---

### 🔗 2.3. Внешние ключи (связи между таблицами)
Чтобы связи работали, нужно **включить поддержку FK**:
```sql
-- Вставь в начало каждого запроса (или в настройках SQLiteStudio)
PRAGMA foreign_keys = ON;
```

Правила поведения при удалении (`ON DELETE`):
- `CASCADE` — удалить связанные записи вместе с родителем.
- `SET NULL` — в связанных записях поставить `NULL`.
- `RESTRICT` — запретить удаление родителя (самое частое).
- `NO ACTION` — то же самое, что `RESTRICT`.

---

### 📥 2.4. Добавление данных
**Визуально:** двойной клик по таблице → вкладка **Данные** → кнопка **+** → Заполняешь → Галочка (сохранить).

**SQL:**
```sql
INSERT INTO classes (name) VALUES ('9А'), ('9Б'), ('10А');

INSERT INTO students (full_name, age, class_id) VALUES 
    ('Иванов Иван', 15, 1),
    ('Петров Петр', 16, 2),
    ('Сидорова Анна', 15, 1);
```

---

### 💾 2.5. Экспорт и импорт данных
- **Экспорт** таблицы в CSV/JSON: ПКМ по таблице → **Копировать** или **Экспорт таблицы**.
- **Импорт** из CSV: ПКМ по БД → **Импорт** → выбираешь файл → сопоставляешь столбцы.

---

# 🔵 ЧАСТЬ 3. Язык SQL — запросы SELECT (от простого к сложному)

### 🎯 3.1. Базовый SELECT
```sql
-- Выбрать все столбцы из таблицы
SELECT * FROM students;

-- Выбрать конкретные столбцы
SELECT full_name, age FROM students;

-- Уникальные значения (без повторов)
SELECT DISTINCT age FROM students;
```

---

### 🎯 3.2. Алиасы (переименование столбцов и таблиц через `AS`)
```sql
SELECT 
    full_name AS "ФИО ученика",      -- алиас столбца (кавычки для пробелов)
    age AS "Возраст",
    age + 1 AS "Возраст через год"    -- можно вычислять прямо в SELECT
FROM students AS s;                   -- алиас таблицы (короткое имя)
```

---

### 🎯 3.3. Фильтрация через `WHERE`
```sql
SELECT full_name, age FROM students WHERE age > 15;

-- AND / OR / NOT
SELECT * FROM students WHERE age = 15 AND class_id = 1;

-- IN (один из списка)
SELECT * FROM students WHERE age IN (14, 15, 16);

-- BETWEEN (диапазон, включительно)
SELECT * FROM students WHERE age BETWEEN 14 AND 16;

-- IS NULL / IS NOT NULL
SELECT * FROM students WHERE class_id IS NULL;
```

---

### 🎯 3.4. Поиск по шаблону (`LIKE`)
```sql
-- % = любое количество символов, _ = ровно один символ

-- Имя начинается на "Иван"
SELECT * FROM students WHERE full_name LIKE 'Иван%';

-- Имя заканчивается на "ов"
SELECT * FROM students WHERE full_name LIKE '%ов';

-- Ровно 6 букв в имени
SELECT * FROM students WHERE full_name LIKE '______';

-- Содержит букву "а"
SELECT * FROM students WHERE full_name LIKE '%а%';
```

---

### 🎯 3.5. Сортировка и ограничение
```sql
SELECT full_name, age 
FROM students 
ORDER BY age DESC, full_name ASC;  -- DESC = по убыванию, ASC = по возрастанию

-- LIMIT и OFFSET (постраничный вывод)
SELECT * FROM students LIMIT 10;              -- Первые 10
SELECT * FROM students LIMIT 10 OFFSET 20;    -- Пропустить 20, взять 10
```

---

### 🎯 3.6. Агрегатные функции
```sql
SELECT 
    COUNT(*) AS "Всего учеников",               -- Количество строк
    COUNT(DISTINCT class_id) AS "Уникальных классов",
    SUM(age) AS "Сумма возрастов",
    AVG(age) AS "Средний возраст",
    MIN(age) AS "Самый младший",
    MAX(age) AS "Самый старший"
FROM students;

-- COUNT с условием (хитрый трюк)
SELECT COUNT(CASE WHEN age >= 16 THEN 1 END) AS "Старше 16" FROM students;
```

---

### 🎯 3.7. `GROUP BY` + `HAVING` (Группировка)
⚠️ **Важно:** В SELECT могут быть ТОЛЬКО:
- столбцы из GROUP BY,
- агрегатные функции.

```sql
-- Количество учеников в каждом классе
SELECT 
    class_id,
    COUNT(*) AS student_count,
    AVG(age) AS avg_age
FROM students
GROUP BY class_id
HAVING COUNT(*) > 5;   -- HAVING фильтрует ГРУППЫ (WHERE фильтрует СТРОКИ)
```

---

### 🎯 3.8. `JOIN` — объединение таблиц (Самое важное!)

**📍 INNER JOIN** — только совпадающие записи (самое частое):
```sql
SELECT 
    s.full_name,
    c.name AS class_name,
    s.age
FROM students s
INNER JOIN classes c ON s.class_id = c.id;
```

**📍 LEFT JOIN** — все из левой + совпадения из правой (или NULL):
```sql
-- Покажет ВСЕХ учеников, даже если у них нет класса
SELECT 
    s.full_name,
    COALESCE(c.name, 'Без класса') AS class_name  -- COALESCE заменяет NULL
FROM students s
LEFT JOIN classes c ON s.class_id = c.id;
```

**📍 Несколько JOIN подряд:**
```sql
SELECT 
    s.full_name AS "Ученик",
    sub.title AS "Предмет",
    g.score AS "Оценка",
    c.name AS "Класс"
FROM grades g
INNER JOIN students s ON g.student_id = s.id
INNER JOIN subjects sub ON g.subject_id = sub.id
LEFT JOIN classes c ON s.class_id = c.id
WHERE g.score >= 4;
```

**📍 SELF JOIN** — таблица с самой собой (например, найти однофамильцев):
```sql
SELECT 
    s1.full_name AS "Ученик 1",
    s2.full_name AS "Ученик 2"
FROM students s1
INNER JOIN students s2 
    ON SUBSTR(s1.full_name, 1, 3) = SUBSTR(s2.full_name, 1, 3)
    AND s1.id < s2.id;  -- Чтобы не было пар (А-А) и повторов (А-Б и Б-А)
```

---

### 🎯 3.9. Подзапросы (SELECT внутри SELECT)
```sql
-- Ученики со средним баллом выше среднего по школе
SELECT full_name, age 
FROM students 
WHERE id IN (
    SELECT student_id 
    FROM grades 
    GROUP BY student_id
    HAVING AVG(score) > (SELECT AVG(score) FROM grades)
);

-- Подзапрос в SELECT (посчитать кол-во оценок)
SELECT 
    s.full_name,
    (SELECT COUNT(*) FROM grades g WHERE g.student_id = s.id) AS grades_count
FROM students s;
```

---

### 🎯 3.10. `CASE WHEN` (условия прямо в SELECT)
```sql
SELECT 
    full_name,
    score,
    CASE 
        WHEN score >= 5 THEN 'Отлично'
        WHEN score >= 4 THEN 'Хорошо'
        WHEN score >= 3 THEN 'Удовлетворительно'
        ELSE 'Неудовлетворительно'
    END AS grade_description
FROM grades g
INNER JOIN students s ON g.student_id = s.id;
```

---

### 🎯 3.11. `UNION` — объединение результатов двух SELECT
```sql
-- Взять учеников 9 класса и отличников 10 класса в один список
SELECT full_name, '9 класс' AS category FROM students WHERE class_id = 1
UNION
SELECT full_name, 'Отличник 10' AS category FROM students 
WHERE class_id = 3 AND id IN (
    SELECT student_id FROM grades GROUP BY student_id HAVING AVG(score) >= 5
)
ORDER BY full_name;
```
⚠️ **UNION** убирает дубликаты, **UNION ALL** оставляет все.

---

### 🎯 3.12. Работа с датами (SQLite)
```sql
SELECT 
    exam_date,
    strftime('%Y', exam_date) AS year,       -- Год
    strftime('%m', exam_date) AS month,      -- Месяц
    strftime('%d', exam_date) AS day,        -- День
    date('now') AS today,                    -- Сегодняшняя дата
    date('now', '-1 day') AS yesterday,      -- Вчера
    julianday('now') - julianday(exam_date) AS days_passed  -- Дней прошло
FROM grades;
```

---

# 🚀 ЧАСТЬ 4. МЕГА-КОМБО: SQLite → Python → Matplotlib

**Типичная экзаменационная задача:** достать данные из БД и построить график.

```python
import sqlite3
import matplotlib.pyplot as plt

# 1. Подключаемся к БД
conn = sqlite3.connect('school.db')
cursor = conn.cursor()

# 2. Делаем SQL-запрос с JOIN и GROUP BY
query = """
    SELECT 
        c.name AS class_name,
        AVG(g.score) AS avg_score,
        COUNT(g.id) AS total_grades
    FROM classes c
    LEFT JOIN students s ON c.id = s.class_id
    LEFT JOIN grades g ON s.id = g.student_id
    GROUP BY c.id
    ORDER BY avg_score DESC;
"""

cursor.execute(query)
results = cursor.fetchall()  # Получаем список кортежей

# 3. Распаковываем данные для графика
classes = [row[0] for row in results]
avg_scores = [row[1] for row in results]
colors = ['green' if score >= 4 else 'red' for score in avg_scores]

# 4. Строим график
plt.figure(figsize=(10, 6))
bars = plt.bar(classes, avg_scores, color=colors, edgecolor='black')

# Подписи над столбцами
for bar, score in zip(bars, avg_scores):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
             f'{score:.2f}', ha='center', fontweight='bold')

plt.title('Средний балл по классам')
plt.ylabel('Средняя оценка')
plt.ylim(0, 5.5)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('class_performance.png', dpi=300)
plt.show()

# 5. ОБЯЗАТЕЛЬНО закрываем соединение!
conn.close()
```

---

## ✅ ФИНАЛЬНЫЙ ЧЕК-ЛИСТ НА ЭКЗАМЕНЕ

### Для Matplotlib:
- [ ] В начале файла `plt.rcParams` для русского языка.
- [ ] `plt.figure(figsize=(x, y))` — чтобы график был не крохотным.
- [ ] `plt.title()`, `plt.xlabel()`, `plt.ylabel()` — ОБЯЗАТЕЛЬНЫ для смысла.
- [ ] `plt.tight_layout()` — чтобы надписи не обрезались.
- [ ] `plt.savefig('file.png')` **ДО** `plt.show()`, иначе сохранится пустой график.

### Для SQLiteStudio:
- [ ] `PRAGMA foreign_keys = ON;` — если используешь внешние ключи.
- [ ] Сохраняй изменения после правки таблицы (галочка сверху).
- [ ] Делай бэкап `.db` файла перед большими правками.

### Для SQL:
- [ ] В GROUP BY должны быть все НЕ агрегатные столбцы из SELECT.
- [ ] WHERE применяется ДО группировки, HAVING — ПОСЛЕ.
- [ ] При JOIN-ах используй алиасы таблиц (`s.`, `c.`) для краткости.
- [ ] `COALESCE(столбец, 'Значение по умолчанию')` — защита от NULL.
- [ ] Для дат в SQLite используй `strftime()` и `julianday()`.

---

🎯 **Совет от эксперта:** на экзамене первым делом напиши на листочке структуру таблиц и примерные данные. Тогда любой SELECT и любой график ты напишешь за 5 минут, потому что будешь понимать, **что именно** ты достаешь из БД. Удачи! 🚀