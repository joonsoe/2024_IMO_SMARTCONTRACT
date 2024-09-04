from flask import Flask, render_template
from flask_socketio import SocketIO
import random
import time
from threading import Thread, Event
from web3 import Web3
from solcx import compile_source, install_solc

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Solidity 컴파일러 설치
install_solc('0.8.0')

# 스마트 계약 코드 읽기
with open('AutoTrader.sol', 'r') as file:
    contract_source_code = file.read()

# Solidity 코드 컴파일
compiled_sol = compile_source(contract_source_code, output_values=['abi', 'bin'])
contract_interface = compiled_sol['<stdin>:AutoTrader']

# Ganache에 연결
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# 계정 설정
account = w3.eth.accounts[0]

# 스마트 계약 배포
AutoTrader = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
tx_hash = AutoTrader.constructor().transact({'from': account})
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = tx_receipt.contractAddress
contract = w3.eth.contract(address=contract_address, abi=contract_interface['abi'])

print(f'Contract deployed at address: {contract_address}')

# 거래 수행 함수
def perform_transaction(value):
    try:
        if value > 500:
            print('Value exceeds 500, purchasing...')
            tx_hash = contract.functions.purchase().transact({
                'from': account,
                'value': w3.toWei(0.01, 'ether')  # 0.01 ETH를 전송
            })
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f'Purchase completed with transaction hash: {receipt.transactionHash.hex()}')
        elif value < 300:
            print('Value below 300, selling...')
            tx_hash = contract.functions.sell().transact({'from': account})
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f'Sale completed with transaction hash: {receipt.transactionHash.hex()}')
    except Exception as e:
        print(f'Error during transaction: {e}')

# 백그라운드 스레드와 이벤트 설정
thread = None
thread_stop_event = Event()

# 거래를 주기적으로 수행하는 백그라운드 스레드
def background_transaction_thread():
    while not thread_stop_event.is_set():
        carbon_emission = random.uniform(100, 1000)  # 예시로 탄소 배출량 생성

        # 거래 수행
        perform_transaction(carbon_emission)

        # 거래 간의 대기 시간 설정 (예: 3초)
        time.sleep(3)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    if thread is None or not thread.is_alive():
        thread = Thread(target=background_transaction_thread)
        thread.start()

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
