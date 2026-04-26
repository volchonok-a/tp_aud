from flask import Flask, render_template, request, jsonify
from config import TIME_SLOTS, WEEKDAY_MAP, ALL_ROOMS
from parser import get_occupied_rooms

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', time_slots=TIME_SLOTS, weekdays=WEEKDAY_MAP)

@app.route('/api/free_rooms', methods=['POST'])
def api_free_rooms():
    try:
        data = request.get_json()
        weekday = data.get('weekday')
        time_slot = data.get('time_slot')
        week_type = data.get('week_type', 'числитель')

        day_name = WEEKDAY_MAP.get(weekday, weekday)
        occupied = get_occupied_rooms(day_name, time_slot, week_type)
        free_rooms = sorted([r for r in ALL_ROOMS if r not in occupied])

        return jsonify({
            'success': True,
            'free_rooms': free_rooms,
            'occupied_rooms': sorted(list(occupied)),
            'count': len(free_rooms),
            'total_rooms': len(ALL_ROOMS),
            'time_slot': time_slot,
            'weekday_display': day_name.capitalize(),
            'week_type': week_type
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)