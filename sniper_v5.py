import asyncio
import ccxt.pro as ccxt
import pandas as pd
#import pandas_ta as ta
import time
import json
from datetime import datetime

# ==========================================================
# ИНТЕГРИРОВАННЫЙ ПУЛЬТ УПРАВЛЕНИЯ (V2.5)
# ==========================================================
#PULSE_GENOME = {
#    "SOL/USDT": {"l_off": 0.0012, "s_off": 0.0012, "min_w": 0.7, "max_w": 1.9, "tp1": 0.0045, "tp2": 0.0110, "sl": -0.0018},
#    "SUI/USDT": {"l_off": 0.0018, "s_off": 0.0018, "min_w": 0.9, "max_w": 2.5, "tp1": 0.0065, "tp2": 0.0160, "sl": -0.0022},
#    "1000PEPE/USDT": {"l_off": 0.0025, "s_off": 0.0025, "min_w": 1.5, "max_w": 3.4, "tp1": 0.0090, "tp2": 0.0250, "sl": -0.0028}
#}

#PULSE_GENOME = {
#    "SOL/USDT:USDT": {"l_off": 0.0012, "s_off": 0.0012, "min_w": 0.7, "max_w": 1.9, "tp1": 0.0045, "tp2": 0.0110, "sl": -0.0018},
#    "SUI/USDT:USDT": {"l_off": 0.0018, "s_off": 0.0018, "min_w": 0.9, "max_w": 2.5, "tp1": 0.0065, "tp2": 0.0160, "sl": -0.0022},
#    "1000PEPE/USDT:USDT": {"l_off": 0.0020, "s_off": 0.0020, "min_w": 0.8, "max_w": 3.4, "tp1": 0.0090, "tp2": 0.0250, "sl": -0.0028}
#}
#    "1000PEPE/USDT:USDT": {"l_off": 0.0025, "s_off": 0.0025, "min_w": 1.5, "max_w": 3.4, "tp1": 0.0090, "tp2": 0.0250, "sl": -0.0028}

# ==========================================================
# ИНТЕГРИРОВАННЫЙ ПУЛЬТ УПРАВЛЕНИЯ (V3.4 - Hexagon)
# ==========================================================
PULSE_GENOME = {
    "SOL/USDT:USDT": {
        "l_off": 0.0030, "s_off": 0.0030, "min_w": 0.8, "max_w": 2.5, 
        "tp1": 0.0050, "tp2": 0.0120, "sl": -0.0035
    },
    "SUI/USDT:USDT": {
        "l_off": 0.0035, "s_off": 0.0035, "min_w": 1.0, "max_w": 3.0, 
        "tp1": 0.0065, "tp2": 0.0180, "sl": -0.0045
    },
    "1000PEPE/USDT:USDT": {
        "l_off": 0.0040, "s_off": 0.0040, "min_w": 1.5, "max_w": 4.5, 
        "tp1": 0.0090, "tp2": 0.0280, "sl": -0.0055
    },
    "FET/USDT:USDT": {
        "l_off": 0.0032, "s_off": 0.0032, "min_w": 0.9, "max_w": 3.2, 
        "tp1": 0.0060, "tp2": 0.0150, "sl": -0.0040
    },
    "NEAR/USDT:USDT": {
        "l_off": 0.0030, "s_off": 0.0030, "min_w": 0.7, "max_w": 2.8, 
        "tp1": 0.0055, "tp2": 0.0130, "sl": -0.0035
    },
    "WIF/USDT:USDT": {
        "l_off": 0.0042, "s_off": 0.0042, "min_w": 1.2, "max_w": 4.0, 
        "tp1": 0.0085, "tp2": 0.0220, "sl": -0.0050
    }
}

MAX_SLOTS = 1
LEVERAGE = 20
RISK_GEAR = 0.85    # Использование 95% доступной маржи на слот
RESERVE_CASH = 0.8  # Резерв на комиссии ($)
SMART_CUT_T = 45    # Секунд до проверки Price-Cut

MAX_SLOTS = 1
LEVERAGE = 20
RISK_GEAR = 0.85    # Использование 95% доступной маржи на слот
RESERVE_CASH = 0.8  # Резерв на комиссии ($)
SMART_CUT_T = 45    # Секунд до проверки Price-Cut

class GlobalMemory:
    def __init__(self):
        self.prices = {}
        self.active_pos = {}
        self.slots_occupied = 0
        self.tp_fixed = {} # Статус фиксации TP1
        self.entry_times = {}
        self.is_running = True
        self.wallet = 0.0
        self.available = 0.0

memory = GlobalMemory()

def log(msg):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{t}] {msg}"
    print(formatted_msg)
    with open("bingx_log.txt", "a", encoding="utf-8") as f:
        f.write(formatted_msg + "\n")

async def init_exchange():
    """Связь с BingX через зашифрованный канал"""
    # Архитектор, вставь свои ключи сюда
    return ccxt.bingx({
        'apiKey': 'JalqlQMGxo0HNxVgkCDcvik47vAUDYkv8ZlChntsXDt4OjHDRTRG5W56F0aKJoK9Z8hNA8ADGvKyOlbhRDOA',
        'secret': 'DeA2h64PM8KtfQZ4wQcUvIPUt3LgjunjYCLJVHqnIL8PtHLgDmef7oJNHxYEy00cO9OswsI4wg4WBwCFa9v0A',
        'enableRateLimit': True,
        'options': {
            'defaultType': 'swap',
            'portfolioMargin': False, # Убираем, если аккаунт обычный
            'broker': 'CCXT'
        }
    })

async def update_balance(exchange):
    """Мониторинг кошелька (раз в 20 сек)"""
    while memory.is_running:
        try:
            bal = await exchange.fetch_balance()
            memory.wallet = float(bal['total'].get('USDT', 0))
            memory.available = float(bal['free'].get('USDT', 0))
        except Exception as e:
            log(f"⚠️ Ошибка кошелька: {e}")
        await asyncio.sleep(20)

async def price_stream(exchange):
    """Индивидуальный захват цен (Поддержка BingX V2)"""
    symbols = list(PULSE_GENOME.keys())
    log(f"📡 Запуск раздельного WS-потока для: {symbols}")

    async def track_symbol(symbol):
        while memory.is_running:
            try:
                ticker = await exchange.watch_ticker(symbol)
                if ticker and 'last' in ticker:
                    val = float(ticker['last'])
                    memory.prices[symbol] = val
                    # Прямой лог для подтверждения связи
#                    log(f"🟢 Поток {symbol}: {val}")
            except Exception as e:
                log(f"⚠️ Ошибка потока {symbol}: {e}")
                await asyncio.sleep(2)

    # Запускаем задачи параллельно
    async def heartbeat():
        await asyncio.sleep(5) # Ждем прогрузки баланса 5 секунд при старте
        while memory.is_running:
            try:
                # Берем текущий баланс для информативности
                bal = memory.available if hasattr(memory, 'available') else "Active"
                log(f"💓 HEARTBEAT: System OK | Bal: ${bal} | Mode: V3.11")
                await asyncio.sleep(600) # 10 минут
            except:
                await asyncio.sleep(10)

    # Добавь heartbeat в список задач
    tasks = [track_symbol(s) for s in symbols]
    tasks.append(heartbeat()) # Добавляем пульс

    await asyncio.gather(*tasks)


async def check_signal(exchange, symbol):
    """Анализ на пробой и поглощение"""
    try:
        dna = PULSE_GENOME[symbol]
        # Берем 30 свечей для точности MA и STD
        ohlcv = await exchange.fetch_ohlcv(symbol, '1m', limit=30)
        df = pd.DataFrame(ohlcv, columns=['t', 'o', 'h', 'l', 'c', 'v'])

        # Индикаторы
        ma = df['c'].rolling(20).mean().iloc[-1]
        std = df['c'].rolling(20).std().iloc[-1]
        upper = ma + (std * 2.1)
        lower = ma - (std * 2.1)
        width = (upper - lower) / ma * 100

        # 1. Фильтр Окна (Squeeze)
        if not (dna['min_w'] <= width <= dna['max_w']): return None

        cur_p = memory.prices.get(symbol, df['c'].iloc[-1])
        prev_o, prev_c = df['o'].iloc[-1], df['c'].iloc[-1]

        # 2. Логика Поглощения (Входим по тренду пробоя)
        # ЛОНГ: Цена выше верхней ленты + оффсет И текущая цена выше открытия красной свечи
#        is_buy = (cur_p >= upper * (1 + dna['l_off'])) and (cur_p > prev_o) and (prev_c > prev_o)
        # ШОРТ: Цена ниже нижней ленты + оффсет И текущая цена ниже открытия зеленой свечи
#        is_sell = (cur_p <= lower * (1 - dna['s_off'])) and (cur_p < prev_o) and (prev_c < prev_o)
        # ЛОНГ: Цена > оффсета И выше открытия ПРЕДЫДУЩЕЙ (неважно какого она была цвета)
        is_buy = (cur_p >= upper * (1 + dna['l_off'])) and (cur_p > prev_o)

        # ШОРТ: Цена < оффсета И ниже открытия ПРЕДЫДУЩЕЙ
        is_sell = (cur_p <= lower * (1 - dna['s_off'])) and (cur_p < prev_o)

        # Защита от "пустых" данных: если объем за минуту нулевой - скипаем
        if df['v'].iloc[-1] <= 0: return None

        if is_buy or is_sell:
            return {'symbol': symbol, 'side': 'buy' if is_buy else 'sell', 'price': cur_p, 'dna': dna, 'open_p': df['o'].iloc[-1]}
    except: pass
    return None

async def execute_entry(exchange, res):
    """Вход по Лимитке + Мгновенный Тейк 1 и Стоп"""
    symbol, side, price, dna, open_p = res['symbol'], res['side'], res['price'], res['dna'], res['open_p']
    try:
#        limit_price = float(exchange.price_to_precision(symbol, (open_p + price) / 2))
        # Было: (open_p + price) / 2 (50% отката)
        # Стало: цена пробоя минус 30% тела свечи (более агрессивный зацеп)
        limit_price = price - (price - open_p) * 0.15 if side == 'buy' else price + (open_p - price) * 0.15


        try: await exchange.set_leverage(LEVERAGE, symbol)
        except: pass

        margin = (memory.available / (MAX_SLOTS - memory.slots_occupied)) * RISK_GEAR
        if margin > RESERVE_CASH: margin -= RESERVE_CASH
        amount = float(exchange.amount_to_precision(symbol, (margin * LEVERAGE) / limit_price))
        if amount <= 0: return

        # Расчет цен
        tp1_price = limit_price * (1 + dna['tp1']) if side == 'buy' else limit_price * (1 - dna['tp1'])
        sl_price = limit_price * (1 + dna['sl']) if side == 'buy' else limit_price * (1 - dna['sl'])

        # ПАРАМЕТРЫ: Тейк 1 на 50% объема + полный Стоп
        params = {
            'stopLoss': float(exchange.price_to_precision(symbol, sl_price)),
            'takeProfit': float(exchange.price_to_precision(symbol, tp1_price)),
            'takeProfitQty': float(exchange.amount_to_precision(symbol, amount * 0.5)), # ТОЛЬКО 50%
            'spot': False
        }

        log(f"🕸️ ЛОВУШКА [V3.9]: {symbol} {side.upper()} | TP1(50%): {round(tp1_price,4)} | SL: {ro und(sl_price,4)}")
        order = await exchange.create_order(symbol, 'limit', side, amount, limit_price, params)

        if order:
            memory.active_pos[symbol] = {
                'side': side, 'price': limit_price, 'vol': amount,
                'dna': dna, 'order_id': order['id']
            }
            memory.entry_times[symbol] = time.time()
            memory.tp_fixed[symbol] = False
            memory.slots_occupied += 1
    except Exception as e:
        log(f"❌ Ошибка лимитки {symbol}: {e}")

async def signal_hunter(exchange):
    """Цикл поиска сигналов"""
    log("🏹 Охотник за импульсами активирован.")
    while memory.is_running:
        if memory.slots_occupied < MAX_SLOTS:
            for symbol in PULSE_GENOME.keys():
                if symbol not in memory.active_pos:
                    signal = await check_signal(exchange, symbol)
                    if signal:
                        await execute_entry(exchange, signal)
                        break # Ждем следующего цикла для балансировки
        await asyncio.sleep(1)

async def monitor_logic(exchange):
    """Ультимативный мониторинг V3.6: Лимитки + Smart-Cut"""
    exit_params = {'spot': False}

    while memory.is_running:
        for symbol, pos in list(memory.active_pos.items()):
            try:
                cur_p = memory.prices.get(symbol)
                if not cur_p: continue

                dna = pos['dna']
                # Считаем PNL от нашей лимитной цены входа
                diff = (cur_p / pos['price'] - 1) if pos['side'] == 'buy' else (pos['price'] / cur_p - 1)
                age = time.time() - memory.entry_times[symbol]

                # ЛОГ ДЛЯ ДЕБАГА
                if int(time.time()) % 10 == 0:
                    log(f"🕵️ Монитор {sym bol}: Profit: {round(diff*100, 3)}% | Age: {int(age)}s")

                # --- СТАДИЯ А: Если лимитка входа еще не исполнилась (ждем 30 сек) ---
                # Если цена улетела далеко (+0.5%) без нас - отменяем охоту
                if age > 30 and diff > 0.005:
                    log(f"🚫 Пропуск {symbol}: Улетела без отката.")
                    await exchange.cancel_all_orders(symbol, exit_params)
                    del memory.active_pos[symbol]
                    memory.slots_occupied -= 1
                    continue

                # --- СТАДИЯ Б: Активная позиция (уже в рынке) ---

                # 1. Smart Price-Cut (Та самая проверка через 45 сек)
                # Выходим, если время вышло, а мы НЕ в профите хотя бы 0.1%
                if age >= SMART_CUT_T and not memory.tp_fixed[symbol] and diff < 0.001:
                    log(f"⏱️ SMART-CUT: {symbol} (Нет инерции)")
                    try:
                        # 1. Расчищаем место (отменяем лимитки)
                        await exchange.cancel_all_orders(symbol, {'spot': False})
                        await asyncio.sleep(0.5)

                        # 2. Узнаем, сколько РЕАЛЬНО успело купиться
                        pos_info = await exchange.fetch_position(symbol, {'spot': False})
                        real_vol = float(pos_info['contracts']) if pos_info and pos_info.get('contracts') else 0

                        if real_vol > 0:
                            side_exit = 'sell' if pos['side'] == 'buy' else 'buy'
                            # Закрываем именно столько, сколько есть на бирже
                            await exchange.create_market_order(symbol, side_exit, real_vol, {'spot': False, 'reduceOnly': True})
                            log(f"✅ Позиция {symbol} успешно очищена: {real_vol} шт.")
                        else:
                            log(f"ℹ️ Лимитка {symbol} была пустой, просто отменена.")

                        # ТОЛЬКО ТЕПЕРЬ СТИРАЕМ ИЗ ПАМЯТИ
                        del memory.active_pos[symbol]
                        memory.slots_occupied -= 1

                    except Exception as e:
                        log(f"🆘 КРИТИЧЕСКИЙ СБОЙ ОЧИСТКИ {symbol}: {e}")
                        log("⚠️ Позиция остается в памяти для повторной попытки!")
                    continue


                # 2. Локальный Тейк №1 (в дополнение к биржевому, для лога и БУ)
                if not memory.tp_fixed[symbol]:
                    pos_info = await exchange.fetch_position(symbol, {'spot': False})
                    current_vol = pos['vol'] # Инициализируем дефолтным значением

                    if pos_info and pos_info.get('contracts') is not None:
                        current_vol = float(pos_info['contracts'])

                        if current_vol < pos['vol'] * 0.7:
                            log(f"🎯 ТЕЙК 1 СРАБОТАЛ: {symbol}. БУ + ТП2.")
                            be_p = pos['price'] * (1 + 0.0005) if pos['side'] == 'buy' else pos['price'] * (1 - 0.0005)
                            tp2_p = pos['price'] * (1 + dna['tp2']) if pos['side'] == 'buy' else pos['price'] * (1 - dna['tp2'])

                            side_exit = 'sell' if pos['side'] == 'buy' else 'buy'
                            await exchange.cancel_all_orders(symbol, {'spot': False})

                            final_params = {
                                'stopLoss': float(exchange.price_to_precision(symbol, be_p)),
                                'spot': False
                            }
                            await exchange.create_order(symbol, 'limit', side_exit, current_vol, tp2_p, final_params)

                            memory.tp_fixed[symbol] = True
                            pos['vol'] = current_vol


                # 3. Ultra-Short SL (Подстраховка кода, если биржа лаганет)
                if diff <= dna['sl']:
                    log(f"🚨 ULTRA-SL TRIGGERED: {symbol}")
                    await exchange.cancel_all_orders(symbol, exit_params)
                    side_exit = 'sell' if pos['side'] == 'buy' else 'buy'
                    await exchange.create_market_order(symbol, side_exit, pos['vol'], exit_params)
                    del memory.active_pos[symbol]
                    memory.slots_occupied -= 1

            except Exception as e:
                log(f"⚠️ Monitor error {symbol}: {e}")

        await asyncio.sleep(0.5)

async def recover_positions(exchange):
    """Синхронизация памяти с реальными позициями на бирже при старте"""
    try:
        log("🔍 Протокол реанимации: Сканирую открытые позиции...")
        # Запрашиваем только фьючерсные позиции
        pos_data = await exchange.fetch_positions(symbols=list(PULSE_GENOME.keys()), params={'spot': False})

        for p in pos_data:
            symbol = p['symbol']
            side = p['side'] # 'long' или 'short'
            contracts = float(p['contracts'])

            if contracts > 0:
                # Мапим сторону под наш формат
                side_internal = 'buy' if side == 'long' else 'sell'
                entry_p = float(p['entryPrice'])

                # Восстанавливаем паспорт позиции
                memory.active_pos[symbol] = {
                    'side': side_internal,
                    'price': entry_p,
                    'vol': contracts,
                    'dna': PULSE_GENOME[symbol],
                    'custom_sl': PULSE_GENOME[symbol]['sl'] # Ставим дефолтный стоп
                }
                memory.tp_fixed[symbol] = False
                memory.entry_times[symbol] = time.time() # Таймер Smart-Cut сбросится (безопасно)
                memory.slots_occupied += 1

                log(f"✅ Позиция {symbol} ({side}) подхвачена! Вход: {entry_p} | Vol: {contracts}")

        if memory.slots_occupied == 0:
            log("📡 Активных позиций на бирже не обнаружено. Охотник чист.")

    except Exception as e:
        log(f"⚠️ Ошибка реанимации: {e}")

async def main():
    exchange = await init_exchange()
    log("🚀 TITAN-BINGX V2.5 [NEURON-IMPULSE] START")

    await recover_positions(exchange)

    tasks = [
        asyncio.create_task(update_balance(exchange)),
        asyncio.create_task(price_stream(exchange)),
        asyncio.create_task(monitor_logic(exchange)),
        asyncio.create_task(signal_hunter(exchange))
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("🛑 Остановка Архитектором.")
