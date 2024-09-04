from web3 import Web3
from solcx import compile_source
import numpy as np
import pandas as pd
from datetime import timedelta
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Ganache 연결
ganache_url = 'http://127.0.0.1:7545'
web3 = Web3(Web3.HTTPProvider(ganache_url))


if web3.isConnected():
    print("Connected to Ganache")

else:
    raise Exception("Failed to connect to Ganache. Please check the Ganache server status and URL.")

# 스마트 계약 소스 코드
contract_source_code = '''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CarbonCreditContract {
    address public owner;
    uint256 public emissionThreshold;
    uint256 public carbonCredits;
    mapping(address => uint256) public userCredits;

    event CarbonCreditPurchased(address indexed buyer, uint256 amount);

    constructor(uint256 _emissionThreshold, uint256 _initialCredits) {
        owner = msg.sender;
        emissionThreshold = _emissionThreshold;
        carbonCredits = _initialCredits;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    function setEmissionThreshold(uint256 _threshold) external onlyOwner {
        emissionThreshold = _threshold;
    }

    function updateCredits(uint256 _newCredits) external onlyOwner {
        carbonCredits = _newCredits;
    }

    function buyCarbonCredits(uint256 _amount) external payable {
        require(msg.value >= _amount * 1 ether, "Insufficient funds");
        require(carbonCredits >= _amount, "Not enough credits available");

        carbonCredits -= _amount;
        userCredits[msg.sender] += _amount;

        emit CarbonCreditPurchased(msg.sender, _amount);
    }

    function getUserCredits(address _user) external view returns (uint256) {
        return userCredits[_user];
    }
}
'''

# 스마트 계약 컴파일 및 배포
compiled_sol = compile_source(contract_source_code)
contract_id, contract_interface = list(compiled_sol['contracts'].items())[0]

Contract = web3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bytecode'])
account = web3.eth.accounts[0]

# 스마트 계약 배포
tx_hash = Contract.constructor(300, 1000).transact({'from': account})
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = tx_receipt.contractAddress
print(f"Contract deployed at address: {contract_address}")

# 계약 인스턴스 생성
contract = web3.eth.contract(address=contract_address, abi=contract_interface['abi'])


# SARIMA 모델을 이용한 예측 데이터 생성
def generate_carbon_emissions_data(start_date='2004-01-01', years=10):
    date_range = pd.date_range(start=start_date, periods=years * 52, freq='W')
    np.random.seed(12)
    base_emissions = 300 + 50 * np.sin(np.linspace(0, 4 * np.pi, len(date_range)))  # 주기적 변화
    emissions = base_emissions + np.random.randn(len(date_range)) * 10  # 노이즈 추가
    data = pd.DataFrame({'Date': date_range, 'Emissions': emissions})
    data.set_index('Date', inplace=True)
    data.index.freq = 'W-SUN'
    return data


def sarima_forecast(data, steps=8):
    model = SARIMAX(data['Emissions'], order=(1, 1, 1), seasonal_order=(1, 1, 0, 52), enforce_stationarity=False,
                    enforce_invertibility=False)
    model_fit = model.fit(disp=False)
    forecast = model_fit.get_forecast(steps=steps)
    forecast_index = pd.date_range(start=data.index[-1] + timedelta(days=7), periods=steps, freq='W-SUN')
    forecast_data = pd.Series(forecast.predicted_mean, index=forecast_index)
    return forecast_data


# 예측 데이터 및 임계값 설정
data = generate_carbon_emissions_data()
forecast = sarima_forecast(data)
emission_threshold = 350  # 예시로 임계값 설정


# 거래 수행
def auto_trade_emissions(forecast, emission_threshold):
    if forecast.mean() > emission_threshold:
        for _ in range(10):  # 최소 10번 거래
            amount_to_buy = 10  # 예시로 10 단위 구매
            nonce = web3.eth.get_transaction_count(account)
            tx = contract.functions.buyCarbonCredits(amount_to_buy).buildTransaction({
                'chainId': 1337,  # Ganache의 기본 체인 ID
                'gas': 2000000,
                'gasPrice': web3.toWei('20', 'gwei'),
                'nonce': nonce,
            })

            # 거래 서명 및 전송
            private_key = web3.eth.account.privateKeyToAccount(web3.eth.accounts[0]).privateKey  # Ganache에서 개인 키 확인
            signed_tx = web3.eth.account.signTransaction(tx, private_key=private_key)
            tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
            print(f'Transaction hash: {web3.toHex(tx_hash)}')


auto_trade_emissions(forecast, emission_threshold)
