import re
import csv
from config import TIME_SLOTS, WEEKDAYS_RU


def get_csv_data():
    """Читает CSV и возвращает список строк"""
    rows = []
    try:
        with open('schedule.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and any(cell.strip() for cell in row):
                    rows.append(row)
        print(f"✅ Загружено {len(rows)} строк")
        return rows
    except FileNotFoundError:
        print("❌ Файл schedule.csv не найден!")
        return []


def extract_rooms_from_cell(cell: str) -> set:
    """Извлекает номера аудиторий из ячейки"""
    if not cell or cell.strip() == '':
        return set()

    rooms = set()
    cell_str = str(cell)

    patterns = [
        r'(?<![а-яА-Яa-zA-Z0-9=_])(\d{3}П)(?![а-яА-Яa-zA-Z0-9=])',
        r'(?<![а-яА-Яa-zA-Z0-9=_])(\d{3}А)(?![а-яА-Яa-zA-Z0-9=])',
        r'(?<![а-яА-Яa-zA-Z0-9=_])(\d{3})(?![а-яА-Яa-zA-Z0-9=])',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, cell_str)
        for room in matches:
            if room not in ['214', '227', '231', '2/25']:
                rooms.add(room)

    return rooms


def parse_schedule(rows):
    """
    Парсит расписание.
    Правило:
    - Строка с временем = ЧИСЛИТЕЛЬ
    - Следующие строки без времени = ЗНАМЕНАТЕЛЬ
    - Если в знаменателе ячейка пустая — копируем аудиторию из числителя
      (объединённые ячейки в Google Таблице)
    """
    schedule = {
        "числитель": {day: {time: set() for time in TIME_SLOTS} for day in WEEKDAYS_RU},
        "знаменатель": {day: {time: set() for time in TIME_SLOTS} for day in WEEKDAYS_RU}
    }

    current_day = None
    current_time = None
    waiting_for_denominator = False
    last_numerator_rooms = {}

    for row_idx, row in enumerate(rows):
        if len(row) < 2:
            continue

        day_cell = row[0].strip() if row[0] else ""
        time_cell = row[1].strip() if len(row) > 1 and row[1] else ""

        if time_cell == 'Часы звонков':
            continue

        # --- НОВЫЙ ДЕНЬ НЕДЕЛИ ---
        if day_cell in WEEKDAYS_RU:
            current_day = day_cell
            current_time = None
            waiting_for_denominator = False
            last_numerator_rooms = {}

        if current_day:
            if time_cell:
                # Нормализуем время
                time_normalized = time_cell.replace(" ", "")
                if '-' in time_normalized:
                    parts = time_normalized.split('-')
                    if len(parts) == 2:
                        time_normalized = f"{parts[0]}-{parts[1]}"

                matched_time = None
                for time_slot in TIME_SLOTS:
                    slot_normalized = time_slot.replace(" ", "")
                    if time_normalized == slot_normalized:
                        matched_time = time_slot
                        break

                if matched_time:
                    current_time = matched_time
                    waiting_for_denominator = True
                    last_numerator_rooms = {}

                    # Парсим аудитории в ЧИСЛИТЕЛЬ
                    for col_idx in range(2, len(row)):
                        cell_value = row[col_idx].strip() if row[col_idx] else ""
                        if cell_value:
                            extracted = extract_rooms_from_cell(cell_value)
                            schedule["числитель"][current_day][current_time].update(extracted)
                            last_numerator_rooms[col_idx] = extracted

            elif waiting_for_denominator and not day_cell:
                # Строка без времени и без дня — это ЗНАМЕНАТЕЛЬ
                for col_idx in range(2, len(row)):
                    cell_value = row[col_idx].strip() if row[col_idx] else ""
                    if cell_value:
                        extracted = extract_rooms_from_cell(cell_value)
                        schedule["знаменатель"][current_day][current_time].update(extracted)
                    elif col_idx in last_numerator_rooms:
                        # Ячейка пустая — копируем из числителя (объединённая ячейка)
                        schedule["знаменатель"][current_day][current_time].update(last_numerator_rooms[col_idx])

    return schedule


def get_occupied_rooms(day_name: str, time_slot: str, week_type: str = "числитель") -> set:
    """
    Возвращает множество занятых аудиторий
    """
    rows = get_csv_data()
    if not rows:
        return set()

    schedule = parse_schedule(rows)

    day_map = {
        'monday': 'Понедельник', 'понедельник': 'Понедельник',
        'tuesday': 'Вторник', 'вторник': 'Вторник',
        'wednesday': 'Среда', 'среда': 'Среда',
        'thursday': 'Четверг', 'четверг': 'Четверг',
        'friday': 'Пятница', 'пятница': 'Пятница',
        'saturday': 'Суббота', 'суббота': 'Суббота'
    }

    day_ru = day_map.get(day_name.lower(), day_name)
    occupied = schedule.get(week_type, {}).get(day_ru, {}).get(time_slot, set())

    return occupied

