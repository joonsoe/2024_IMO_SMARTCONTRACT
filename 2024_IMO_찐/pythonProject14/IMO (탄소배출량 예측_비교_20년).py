import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import timedelta
from sklearn.metrics import mean_squared_error


# 1. 탄소 배출량 데이터 수집
def generate_carbon_emissions_data(start_date='2004-01-01', years=20):
    date_range = pd.date_range(start=start_date, periods=years * 52, freq='W')
    np.random.seed(12)

    # 장기 트렌드 및 계절성 반영
    seasonal_effect = 50 * np.sin(2 * np.pi * date_range.to_series().dt.isocalendar().week / 52)
    trend = 0.5 * (date_range - date_range[0]).days / 365  # 연도별 변화
    noise = np.random.normal(0, 5, len(date_range))  # 노이즈

    emissions = 300 + seasonal_effect + trend + noise

    data = pd.DataFrame({'Date': date_range, 'Emissions': emissions})
    data.set_index('Date', inplace=True)
    data.index.freq = 'W-SUN'
    return data


# 2. SARIMA 모델 훈련
def sarima_forecast(data, steps=8):
    # 모델 파라미터 조정
    model = SARIMAX(data['Emissions'], order=(1, 1, 0), seasonal_order=(1, 1, 0, 52))
    model_fit = model.fit(disp=False)

    forecast = model_fit.get_forecast(steps=steps)
    forecast_index = pd.date_range(start=data.index[-1] + timedelta(days=7), periods=steps, freq='W-SUN')
    forecast_data = pd.Series(forecast.predicted_mean, index=forecast_index)

    return forecast_data


# 3. 결과 시각화
def plot_results(data, forecast, recent_actual):
    plt.figure(figsize=(14, 7))
    plt.plot(data.index[:-8], data['Emissions'][:-8], label='Actual Emissions (Before Recent 8 Weeks)', color='blue')
    plt.plot(data.index[-8:], recent_actual, label='Actual Emissions (Recent 8 Weeks)', color='green')
    plt.plot(forecast.index, forecast, label='Forecasted Emissions', color='red')
    plt.xlabel('Date')
    plt.ylabel('Emissions')
    plt.title('Carbon Emissions Forecast')
    plt.legend()
    plt.grid()
    plt.show()


# 4. 결과값 출력
def print_results(recent_actual, forecast):
    mse = mean_squared_error(recent_actual, forecast)
    print("\nMSE:", mse)

    print("\n실제 배출량 데이터(최근 8주):")
    print(recent_actual)

    print("\n예측된 배출량 데이터(최근 8주):")
    print(forecast)


# 코드 실행
data = generate_carbon_emissions_data()
recent_actual = data['Emissions'][-8:]
forecast = sarima_forecast(data[:-8])
plot_results(data, forecast, recent_actual)
print_results(recent_actual, forecast)
