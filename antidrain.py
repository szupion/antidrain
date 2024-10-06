# -*- coding: utf-8 -*-
from web3 import Web3
import time
import json

# Загружаем конфигурацию
with open('config.json', 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

# Настройки RPC для различных сетей
NETWORKS = {
    'ethereum': {
        'rpc': "",
        'chain_id': 1,
        'native_token_symbol': 'ETH'
    },
    'optimism': {
        'rpc': "",
        'chain_id': 10,
        'native_token_symbol': 'ETH'
    },
    'arbitrum': {
        'rpc': "",
        'chain_id': 42161,
        'native_token_symbol': 'ETH'
    },
    'linea': {
        'rpc': "https://rpc.linea.build",
        'chain_id': 59144,
        'native_token_symbol': 'ETH'
    },
    'polygon': {
        'rpc': "",
        'chain_id': 137,
        'native_token_symbol': 'MATIC'
    },
    'bsc': {
        'rpc': "",
        'chain_id': 56,
        'native_token_symbol': 'BNB'
    },
    'zetachain': {
        'rpc': "",
        'chain_id': 7000,
        'native_token_symbol': 'ZETA'
    },
    'base': {
        'rpc': "",
        'chain_id': 8453,
        'native_token_symbol': 'ETH'
    },
    'avalanche': {
        'rpc': "",
        'chain_id': 43114,
        'native_token_symbol': 'AVAX'
    },
    'zora': {
        'rpc': "",
        'chain_id': 7777777,
        'native_token_symbol': 'ETH'
    },
    'scroll': {
        'rpc': "",
        'chain_id': 534352,
        'native_token_symbol': 'ETH'
    },
    'zksync': {
        'rpc': "",
        'chain_id': 324,
        'native_token_symbol': 'ETH'
    },
    'opbnb': {
        'rpc': "https://binance.llamarpc.com",
        'chain_id': 204,
        'native_token_symbol': 'BNB'
    }
}

# Настройки
PRIVATE_KEY = ""
DESTINATION_ADDRESS = ""

# Получаем Web3-инстанс для каждой сети
def get_web3_instance(network):
    rpc_url = NETWORKS[network]['rpc']
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    
    if not web3.is_connected():
        print(f"Не удалось подключиться к сети {network}.")
        return None
    
    return web3

# Функция для получения баланса нативного токена
def get_native_balance(web3, address):
    balance = web3.eth.get_balance(address)
    return web3.from_wei(balance, 'ether')

# Функция для расчёта газа и отправки нативных токенов
def send_native_tokens(web3, network):
    account = web3.eth.account.from_key(PRIVATE_KEY)
    address = account.address
    balance_wei = web3.eth.get_balance(address)
    
    # Получение текущей цены газа
    gas_price = web3.eth.gas_price if CONFIG['gas'][network] is None else Web3.to_wei(CONFIG['gas'][network], 'gwei')
    gas_limit = 21000  # Минимальный лимит газа для простой транзакции

    # Вычисляем общую стоимость транзакции (gas_fee)
    gas_fee = gas_price * gas_limit  # Общая комиссия за транзакцию
    
    # Проверяем, достаточно ли средств для отправки хотя бы минимальной суммы
    if balance_wei > gas_fee:
        # Рассчитываем максимально возможную сумму для отправки с учетом комиссии
        send_amount_wei = balance_wei - gas_fee  # Отправляем всё, что остаётся после вычета комиссии
        
        # Формируем транзакцию
        tx = {
            'to': DESTINATION_ADDRESS,
            'value': send_amount_wei,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': web3.eth.get_transaction_count(address),
            'chainId': NETWORKS[network]['chain_id']
        }

        # Подписываем и отправляем транзакцию
        signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)  # Обратите внимание на правильный атрибут
        
        print(f"{NETWORKS[network]['native_token_symbol']} отправлено, сумма: {web3.from_wei(send_amount_wei, 'ether')} {NETWORKS[network]['native_token_symbol']}, hash: {tx_hash.hex()}")
    else:
        print(f"Недостаточно средств для отправки на {network}. Текущий баланс: {web3.from_wei(balance_wei, 'ether')} {NETWORKS[network]['native_token_symbol']} (нужно хотя бы {web3.from_wei(gas_fee, 'ether')} {NETWORKS[network]['native_token_symbol']} для покрытия комиссии)")

# Основная функция дренинга
def drain_wallet():
    account = Web3.to_checksum_address(Web3(Web3.HTTPProvider(NETWORKS['ethereum']['rpc'])).eth.account.from_key(PRIVATE_KEY).address)
    
    while True:
        for network in CONFIG['enabled_networks']:
            web3 = get_web3_instance(network)
            if web3 is None:  # Пропускаем, если не удалось подключиться
                continue
            
            balance = get_native_balance(web3, account)
            print(f"Баланс на {network}: {balance} {NETWORKS[network]['native_token_symbol']}")
            
            # Если есть баланс, пытаемся отправить средства
            if balance > 0:
                try:
                    send_native_tokens(web3, network)
                except Exception as e:
                    print(f"Ошибка при отправке на {network}: {e}")
            else:
                print(f"На {network} баланс нулевой.")
        
        time.sleep(60)  # Проверяем баланс каждые 60 секунд

# Запускаем дренер
drain_wallet()
