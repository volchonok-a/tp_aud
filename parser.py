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

    # Ищем аудитории: 3 цифры или 3 цифры + П
    patterns = [
        r'(?<![а-яА-Яa-zA-Z0-9=_])(\d{3}П)(?![а-яА-Яa-zA-Z0-9=])',
        r'(?<![а-яА-Яa-zA-Z0-9=_])(\d{3})(?![а-яА-Яa-zA-Z0-9=])',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, cell_str)
        for room in matches:
            # Фильтруем явно не аудитории
            if room not in ['190', '190А', '190A', '214', '227', '231', '2/25']:
                rooms.add(room)
                # Отладка: показываем, что нашли
                # print(f"      🔍 Найдена аудитория: {room} из ячейки: {cell_str[:80]}...")

    return rooms


def parse_schedule(rows):
    """Парсит расписание, правильно разделяя числитель и знаменатель."""
    schedule = {
        "числитель": {day: {time: set() for time in TIME_SLOTS} for day in WEEKDAYS_RU},
        "знаменатель": {day: {time: set() for time in TIME_SLOTS} for day in WEEKDAYS_RU}
    }

    current_day = None
    current_time = None
    rows_in_current_pair = 0

    DEBUG_DAY = "Понедельник"
    DEBUG_TIME = "8:00 - 9:35"

    for row_idx, row in enumerate(rows):
        if len(row) < 2:
            continue

        day_cell = row[0].strip() if row[0] else ""
        time_cell = row[1].strip() if len(row) > 1 and row[1] else ""

        # Пропускаем служебные строки ДО начала любого дня
        if time_cell == 'Часы звонков':
            continue

        # --- ОБНАРУЖЕН НОВЫЙ ДЕНЬ НЕДЕЛИ ---
        if day_cell in WEEKDAYS_RU:
            if current_day == DEBUG_DAY or day_cell == DEBUG_DAY:
                print(f"\n📅 НОВЫЙ ДЕНЬ: {day_cell} (строка {row_idx})")
            current_day = day_cell
            current_time = None
            rows_in_current_pair = 0
            # НЕ делаем continue! Идём дальше и проверяем time_cell

        # --- МЫ ВНУТРИ ДНЯ НЕДЕЛИ ---
        if current_day:
            # --- ОБНАРУЖЕНО ВРЕМЯ ---
            if time_cell:
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
                    rows_in_current_pair = 1  # Первая строка пары — числитель

                    rooms = set()
                    for col_idx in range(2, len(row)):
                        cell_value = row[col_idx].strip() if row[col_idx] else ""
                        if cell_value:
                            extracted = extract_rooms_from_cell(cell_value)
                            rooms.update(extracted)

                    schedule["числитель"][current_day][current_time].update(rooms)

                    if current_day == DEBUG_DAY and current_time == DEBUG_TIME:
                        print(f"   ⏰ {current_time} | ЧИСЛИТЕЛЬ | ауд: {sorted(rooms) if rooms else '(пусто)'}")

            # --- НЕТ ДНЯ И НЕТ ВРЕМЕНИ (знаменатель) ---
            elif not day_cell and not time_cell:
                if rows_in_current_pair > 0:
                    rows_in_current_pair += 1

                    rooms = set()
                    for col_idx in range(2, len(row)):
                        cell_value = row[col_idx].strip() if row[col_idx] else ""
                        if cell_value:
                            extracted = extract_rooms_from_cell(cell_value)
                            rooms.update(extracted)

                    schedule["знаменатель"][current_day][current_time].update(rooms)

                    if current_day == DEBUG_DAY and current_time == DEBUG_TIME and rooms:
                        print(f"      {current_time} | ЗНАМЕНАТЕЛЬ (строка {row_idx}) | ауд: {sorted(rooms)}")

                    # Защита от бесконечного знаменателя
                    if rows_in_current_pair >= 8:
                        rows_in_current_pair = 0
                # else: просто пустая строка между блоками, игнорируем

    # ИТОГОВЫЙ ВЫВОД
    print(f"\n🔍 ИТОГО для {DEBUG_DAY} {DEBUG_TIME}:")
    print(f"   📘 ЧИСЛИТЕЛЬ: {sorted(schedule['числитель'][DEBUG_DAY][DEBUG_TIME]) if schedule['числитель'][DEBUG_DAY][DEBUG_TIME] else '(пусто)'}")
    print(f"   📗 ЗНАМЕНАТЕЛЬ: {sorted(schedule['знаменатель'][DEBUG_DAY][DEBUG_TIME]) if schedule['знаменатель'][DEBUG_DAY][DEBUG_TIME] else '(пусто)'}")

    return schedule

def get_occupied_rooms(day_name: str, time_slot: str, week_type: str = "числитель") -> set:
    """
    Возвращает множество занятых аудиторий
    """
    rows = get_csv_data()
    if not rows:
        return set()

    schedule = parse_schedule(rows)

    # Конвертация дня
    day_map = {
        'monday': 'Понедельник', 'понедельник': 'Понедельник',
        'tuesday': 'Вторник', 'вторник': 'Вторник',
        'wednesday': 'Среда', 'среда': 'Среда',
        'thursday': 'Четверг', 'четверг': 'Четверг',
        'friday': 'Пятница', 'пятница': 'Пятница',
        'saturday': 'Суббота', 'суббота': 'Суббота'
    }

    day_ru = day_map.get(day_name.lower(), day_name)

    # Получаем занятые аудитории для выбранной недели
    occupied = schedule.get(week_type, {}).get(day_ru, {}).get(time_slot, set())

    # Для отладки показываем обе недели
    numerator = schedule["числитель"][day_ru].get(time_slot, set())
    denominator = schedule["знаменатель"][day_ru].get(time_slot, set())

    print(f"\n🔍 Расписание на {day_ru} {time_slot}:")
    print(f"   📘 ЧИСЛИТЕЛЬ ({len(numerator)} ауд.): {sorted(numerator) if numerator else 'нет занятий'}")
    print(f"   📗 ЗНАМЕНАТЕЛЬ ({len(denominator)} ауд.): {sorted(denominator) if denominator else 'нет занятий'}")
    print(f"   ➡️ Выбрана неделя: {week_type}")
    print(f"   🚫 Занятые аудитории: {sorted(occupied) if occupied else 'ПРЕДУПРЕЖДЕНИЕ: нет данных для этой недели!'}")

    return occupied