from flask import Flask, render_template
from flask_socketio import SocketIO
from web3 import Web3
from threading import Thread, Event
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Ganache에 연결
ganache_url = "http://0.0.0.0:7545"
w3 = Web3(Web3.HTTPProvider(ganache_url))

# Ganache 연결 확인
if w3.is_connected():
    print("가나슈에 연결 성공")
else:
    print("가나슈에 연결 실패")

# 전체 트랜잭션을 추적하기 위한 변수
transaction_hashes = set()
thread = None
thread_stop_event = Event()


# 트랜잭션 추적 및 소켓 전송 함수
def track_transactions():

    current_block = w3.eth.block_number
    print(f"현재 블록: {current_block}")

    # 0부터 현재 블록까지 모든 블록의 트랜잭션 확인
    for block_number in range(0, current_block + 1):
        block = w3.eth.get_block(block_number, full_transactions=True)
        for tx in block.transactions:
            if tx.hash.hex() not in transaction_hashes:
                transaction_hashes.add(tx.hash.hex())

                # 기본 트랜잭션 정보 수집
                tx_details = {
                    "hash": tx.hash.hex(),
                    "from": tx['from'],
                    "to": tx['to'],
                    "value": w3.fromWei(tx['value'], 'ether'),
                    "gas": tx['gas'],
                    "blockNumber": tx['blockNumber'],
                }

                # 트랜잭션이 스마트 계약 생성인지 확인
                if tx['to'] is None:
                    tx_details["type"] = "contract_creation"
                    tx_details["description"] = "Smart contract creation transaction"
                else:
                    # 트랜잭션이 스마트 계약 호출인지 확인
                    contract_code = w3.eth.get_code(tx['to'])
                    if contract_code != b"":  # 비어 있지 않으면 스마트 계약
                        tx_details["type"] = "contract_call"
                        tx_details["description"] = "Smart contract function call transaction"
                    else:
                        tx_details["type"] = "standard_transaction"
                        tx_details["description"] = "Standard transaction between addresses"

                # 클라이언트에 트랜잭션 정보 전송
                socketio.emit('new_transaction', tx_details, namespace='/test')


@app.route('/')
def index():
    return render_template('server.html')


@socketio.on('connect', namespace='/test')
def on_connect():
    print("클라이언트 연결.")
    global thread
    if thread is None or not thread.is_alive():
        thread = Thread(target=track_transactions)
        thread.start()


@socketio.on('disconnect', namespace='/test')
def on_disconnect():
    print("클라이언트 연결 해제")


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, allow_unsafe_werkzeug=True)
