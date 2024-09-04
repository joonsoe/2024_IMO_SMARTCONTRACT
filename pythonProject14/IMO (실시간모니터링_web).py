from flask import Flask, render_template
from flask_socketio import SocketIO
import random
import time
from threading import Thread, Event

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

thread = Thread()
thread_stop_event = Event()

# 실제 데이터 수집 함수 (모의)
def collect_real_time_emissions():
    fuel_consumption = random.uniform(500, 1500)  # 연료 소비량 (예: 리터)
    emission_factor = 2.134  # 탄소 배출 계수
    carbon_emission = fuel_consumption * emission_factor  # 탄소 배출량 계산 (예: kg)
    return carbon_emission

# 데이터 전송을 위한 백그라운드 스레드
def background_thread():
    x_data = []
    y_data = []
    count = 0  # 횟수 카운터
    start_time = time.time()

    while not thread_stop_event.isSet():
        crr_time = time.time() - start_time
        carbon_emission = collect_real_time_emissions()

        count += 1  # 데이터 포인트 횟수 증가
        x_data.append(count)  # 횟수를 x_data에 추가
        y_data.append(carbon_emission)  # 탄소 배출량을 y_data에 추가

        # 콘솔에 값 출력
        print(f'Count: {count}, Carbon Emission: {carbon_emission:.2f} kg')

        # 데이터 포인트 수 제한
        if len(x_data) > 100:
            x_data.pop(0)
            y_data.pop(0)

        socketio.emit('update', {'x': x_data, 'y': y_data}, namespace='/test')
        socketio.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    if not thread.is_alive():
        thread = Thread(target=background_thread)
        thread.start()

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
