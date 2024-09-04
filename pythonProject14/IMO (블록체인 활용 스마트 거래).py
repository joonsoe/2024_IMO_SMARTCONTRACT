from web3 import Web3
from solcx import compile_source, install_solc
import time

# Solidity 컴파일러 설치
install_solc('0.8.0')

# 스마트 계약 코드 읽기
with open('BlockChainAutoTrader/AutoTrader.sol', 'r') as file:
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

# 모니터링 및 거래 수행
def monitor_and_trade():
    while True:
        current_value = contract.functions.value().call()
        print(f'Current Value: {current_value}')

        if current_value > 500:
            print('Value exceeds 500, purchasing...')
            tx_hash = contract.functions.purchase().transact({
                'from': account,
                'value': w3.toWei(0.01, 'ether')
            })
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f'Purchase completed with transaction hash: {receipt.transactionHash.hex()}')
            break

        time.sleep(1)  # 1초마다 값 확인

# 시뮬레이션: 값을 설정하고 모니터링 시작
contract.functions.setValue(550).transact({'from': account})
monitor_and_trade()
