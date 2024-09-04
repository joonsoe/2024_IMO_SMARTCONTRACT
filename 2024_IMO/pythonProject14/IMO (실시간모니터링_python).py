import random
import time
import matplotlib.pyplot as plt
from datetime import datetime

# 시뮬레이션 설정
update_interval = 1  # 업데이트 주기 (초)
num = 100  # 그래프에 표시할 데이터 포인트 수(최대)

# 초기 데이터 설정
x_data = []
y_data = []

# 실제 데이터 수집 함수 (모의)
def collect_real_time_emissions():
    # 실제로는 센서 데이터로 대체
    # 예시: fuel_consumption = get_fuel_data_from_sensor()
    fuel_consumption = random.uniform(500, 1500)  # 연료 소비량 (예: 리터)
    emission_factor = 2.134  # 탄소 배출 계수
    carbon_emission = fuel_consumption * emission_factor  # 탄소 배출량 계산 (예: kg)
    return carbon_emission

# 보고 생성 함수
def generate_imo_report(emissions_data):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    report = {
        'timestamp': timestamp,
        'total_emissions': sum(emissions_data),
        'average_emissions': sum(emissions_data) / len(emissions_data) if emissions_data else 0,
        # 추가할 수 있는 필드: 선박 ID, 항로 정보 등
    }

    print(f"Generated IMO Report at {timestamp}: {report}")

# 그래프 설정
plt.ion()
fig, ax = plt.subplots()
line, = ax.plot(x_data, y_data, 'b-')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Emissions (kg)')
ax.set_title('Real-Time Emissions Monitoring')

start_time = time.time()

emissions_data = []  # 탄소 배출량 데이터 저장

try:
    while True:
        # 현재 시간과 탄소 배출량 수집
        crr_time = time.time() - start_time
        carbon_emission = collect_real_time_emissions()

        # 데이터 추가
        x_data.append(crr_time)
        y_data.append(carbon_emission)
        emissions_data.append(carbon_emission)

        # 데이터 포인트 수 제한 == 자동으로 오래된 데이터들은 없어짐
        if len(x_data) > num:
            x_data.pop(0)
            y_data.pop(0)
            emissions_data.pop(0)

        # 그래프 업데이트
        line.set_xdata(x_data)
        line.set_ydata(y_data)
        ax.relim()
        ax.autoscale_view()
        plt.draw()
        plt.pause(update_interval)

        # 주기적으로 보고 생성
        if int(crr_time) % 60 == 0:
            generate_imo_report(emissions_data)

except KeyboardInterrupt:
    print("Program has ended")
    plt.ioff()
    plt.show()
