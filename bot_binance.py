import asyncio
import ccxt.pro as ccxt
import pandas as pd
import time
import json
import math
from datetime import datetime

# ==========================================
# --- ПУЛЬТ УПРАВЛЕНИЯ TITAN-BINANCE V1.0 ---
# ==========================================
API_KEY = ""
SECRET_KEY = ""

# --- УПРАВЛЕНИЕ КАПИТАЛОМ ---
MAX_ACTIVE_SLOTS = 1       # Динамика: 1 (при <$150), 2 (при <$500), 3 (при >$500)
RISK_GEAR = 0.85           # Общий множитель объема (0.1 - 1.0)
RESERVE_CASH = 2.0         # Буфер на комиссии (USDT)

# --- ГЛОБАЛЬНЫЕ ФИЛЬТРЫ (Безопасность) ---
GLOBAL_MAX_BANDWIDTH = 2   # Если рынок разорвало в клочья - стоп входы
FUNDING_SHIELD = 0.0003    # Пропуск при ставке > 0.03%
SAFE_LEVERAGE_LIMIT = 20    # Жесткий лимит до июня 2026
# ==========================================

class GlobalMemory:
    def __init__(self):
        self.prices = {}
        self.active_pos = {}
        self.dna_fleet = {}    # Сюда будет грузиться активный режим
        self.all_dna = {'bull': {}, 'stable': {}, 'bear': {}} # Хранилище всех геномов
        self.current_regime = 'stable' # По умолчанию
        self.is_running = True
        self.slots_occupied = 0
        self.tp_status = {}
        self.step_be = {}
        self.entry_times = {}
        self.btc_history = []
        self.available_margin = 0.0
        self.total_wallet = 0.0
        self.be_levels = {}
        self.last_btc_push = 0 
memory = GlobalMemory()

def load_all_dna():
    """Загрузка всех трех файлов в память при старте"""
    try:
        for mode in ['bull', 'stable', 'bear']:
            with open(f'dna_{mode}.json', 'r') as f:
                memory.all_dna[mode] = json.load(f)
        # Устанавливаем стартовую матрицу
        memory.dna_fleet = memory.all_dna['stable']
        log(f"🧬 Тройная Матрица загружена. Режим по умолчанию: STABLE")
    except Exception as e:
        log(f"❌ ОШИБКА ЗАГРУЗКИ JSON: {e}")

async def warm_up_btc_history(exchange):
    """Мгновенное наполнение истории BTC свечами за прошлый час"""
    memory.btc_history = [] # Очищаем массив полностью перед загрузкой свечей
    try:
        log("💉 Прогрев истории BTC: Загрузка свечей...")
        # Берем последние 60 минутных свечей
        ohlcv = await exchange.fetch_ohlcv('BTC/USDT:USDT', '1m', limit=60)
        
        # Индекс [4] — это цена закрытия (Close). Это критично.
        memory.btc_history = [float(candle[4]) for candle in ohlcv]
        
        if memory.btc_history:
            memory.last_btc_push = time.time()
            
            # МГНОВЕННЫЙ РАСЧЕТ РЕЖИМА ПРИ СТАРТЕ
            btc_start = memory.btc_history[0]
            btc_now = memory.btc_history[-1]
            change = (btc_now / btc_start) - 1
            
            new_regime = 'stable'
            if change > 0.008:   new_regime = 'bull'
            elif change < -0.008: new_regime = 'bear'
            
            memory.current_regime = new_regime
            memory.dna_fleet = memory.all_dna[new_regime]
            
            log(f"✅ История BTC прогрета: {len(memory.btc_history)} записей. База: {btc_start}")
            log(f"⚙️ Стартовый режим: >>> {new_regime.upper()} <<< (Trend: {round(change*100, 2)}%)")
            
    except Exception as e:
        log(f"⚠️ Не удалось прогреть историю: {e}")

async def update_market_regime():
    log("🚥 Коробка передач: Анализ запущен.")
    while memory.is_running:
        try:
            hist_len = len(memory.btc_history)
            if hist_len >= 60:
                # Берем точку 10 минут назад (индекс -60)
                # Это гарантирует, что мы смотрим именно на 10-минутный отрезок
                btc_start = memory.btc_history[-60] 
                btc_now = memory.prices.get('BTC/USDT:USDT', memory.btc_history[-1])

                if btc_start > 10000:
                    btc_change = (btc_now / btc_start) - 1
                else:
                    btc_change = 0

                # ОДИН расчет для всего
                change_pct = round(btc_change * 100, 3)

                # 1. Дебаг-лог (каждые 10 сек)
                if int(time.time()) % 10 == 0:
                    log(f"🚥 DEBUG: BTC Hist: {hist_len}/100 | Change: {change_pct}% | Mode: {memory.current_regime.upper()}")

                # 2. Логика переключения
                new_regime = 'stable'
                if btc_change > 0.008:   new_regime = 'bull'
                elif btc_change < -0.008: new_regime = 'bear'

                if new_regime != memory.current_regime:
                    memory.current_regime = new_regime
                    memory.dna_fleet = memory.all_dna[new_regime]
                    log(f"⚙️ ПЕРЕКЛЮЧЕНИЕ: >>> {new_regime.upper()} <<< | Change: {change_pct}%")
            else:
                if int(time.time()) % 30 == 0:
                    log(f"⏳ Коробка копит данные: {hist_len}/60...")

        except Exception as e:
            log(f"⚠️ Ошибка Коробки: {e}")

        await asyncio.sleep(5)

def log(msg):
    t = datetime.now().strftime('%H:%M:%S')
    print(f"[{t}] 🏛️ {msg}")
    with open("binance_log.txt", "a") as f: f.write(f"[{t}] {msg}\n")

# Загрузка Матрицы
def load_dna():
    try:
        with open('dna_binance.json', 'r') as f:
            memory.dna_fleet = json.load(f)
        log(f"🧬 Матрица V16.0 загружена: {len(memory.dna_fleet)} монет в обойме.")
    except Exception as e:
        log(f"❌ ОШИБКА JSON: {e}")

async def init_exchange():
    """Инициализация асинхронного подключения"""
    exchange = ccxt.binance({
        'apiKey': API_KEY,
        'secret': SECRET_KEY,
        'options': {'defaultType': 'future'},
        'enableRateLimit': True,
    })
    return exchange

async def price_stream():
    client = await init_exchange()
    log("📡 Запуск WebSocket-потока цен...")
    while memory.is_running:
        try:
            tickers = await client.watch_tickers()
            if not tickers: continue

            now = time.time()
            btc_captured = False

            for symbol, price_data in tickers.items():
                # 1. Сохраняем все цены USDT
                if 'USDT' in symbol:
                    val = float(price_data['last'])
                    memory.prices[symbol] = val
                    
                    # 2. Ловим Биткоина (любой формат: BTC/USDT, BTC/USDT:USDT, BTCUSDT)
                    if not btc_captured and 'BTC' in symbol and 'USDT' in symbol:
                        if (now - memory.last_btc_push) >= 10:
                            memory.btc_history.append(val)
                            if len(memory.btc_history) > 100: memory.btc_history.pop(0)
                            memory.last_btc_push = now
                            btc_captured = True
#                            log(f"✅ BTC Hist Update: {len(memory.btc_history)}/60") # Раскомментируй для проверки

        except Exception as e:
            log(f"⚠️ Ошибка WS-Stream: {e}")
            await asyncio.sleep(1)
    await client.close()

async def update_balance(exchange):
    """Фоновое обновление кошелька (раз в 10 секунд)"""
    while memory.is_running:
        try:
            bal = await exchange.fetch_balance()
            # Добавь этот принудительный лог для проверки
 #           log(f"DEBUG: Получены данные баланса") 
            total = float(bal.get('total', {}).get('USDT', 0))
            free = float(bal.get('free', {}).get('USDT', 0))

            # Резервируем часть для безопасности
            memory.available_margin = max(0, free - RESERVE_CASH)
            memory.total_wallet = total
            # Если хочешь видеть баланс чаще, убери комментарий ниже
#            log(f"💰 БАЛАНС: ${round(total, 2)} | Доступно: ${round(memory.available_margin, 2)}")
            
            # Логируем МАЯК только если баланс изменился или раз в 5 минут
            if not hasattr(memory, 'last_bal_log') or time.time() - memory.last_bal_log > 300:
#                log(f"💰 МАЯК: Balance ${round(total, 2)} | Available: ${round(memory.available_margin, 2)}")
                memory.last_bal_log = time.time()

        except Exception as e:
            log(f"⚠️ Ошибка Balance-Worker: {e}")
        await asyncio.sleep(10)

async def position_tracker(exchange):
    """Синхронизация открытых позиций в реальном времени"""
    while memory.is_running:
        try:
            pos_data = await exchange.fetch_positions()
            # Фильтруем только те, где объем > 0
            active = {p['symbol']: p for p in pos_data if float(p.get('contracts', 0)) > 0}
            memory.active_pos = active
            memory.slots_occupied = len(active)
        except Exception as e:
            log(f"⚠️ Ошибка Position-Tracker: {e}")
        await asyncio.sleep(2)

async def check_signal(exchange, symbol):
    try:
        dna = memory.dna_fleet.get(symbol)
        if not dna: return None

        # 1. Данные рынка (limit=30 для точности MA20)
        ohlcv = await exchange.fetch_ohlcv(symbol, '1m', limit=30)
        df = pd.DataFrame(ohlcv, columns=['t', 'o', 'h', 'l', 'c', 'v'])
        cur_p = memory.prices.get(symbol, df['c'].iloc[-1])

        # 2. Боллинджер и Ширина
        ma_period = dna.get('m_per', 20)
        ma_mult = dna.get('m_mult', 2.1)
        ma = df['c'].rolling(ma_period).mean().iloc[-1]
        std = df['c'].rolling(ma_period).std().iloc[-1]
        upper = ma + (std * ma_mult)
        lower = ma - (std * ma_mult)
        width = (upper - lower) / ma * 100

        # 3. Фильтры безопасности (Анти-Шторм + Анти-Шип)
        if not (dna.get('min_w', 0.8) <= width <= dna.get('width', 2.0)): return None
        
        candle_size = (df['h'].iloc[-1] / df['l'].iloc[-1] - 1)
        if candle_size > 0.008: return None 

        # 4. Параметры предыдущей свечи (Engulfing)
        prev_open = df['o'].iloc[-1]
        prev_close = df['c'].iloc[-1]
        is_prev_red = prev_close < prev_open
        is_prev_green = prev_close > prev_open

        # 5. Логика входа (Оффсет + Поглощение)
        # ЛОНГ: зашел в зону l_off И текущая цена пробила вверх тело красной свечи
        is_buy = (cur_p <= lower * (1 - dna['l_off'])) and (cur_p > prev_open) and is_prev_red
        
        # ШОРТ: зашел в зону s_off И текущая цена пробила вниз тело зеленой свечи
        is_sell = (cur_p >= upper * (1 + dna['s_off'])) and (cur_p < prev_open) and is_prev_green

        if is_buy or is_sell:
            # Funding Shield
            f_data = await exchange.fetch_funding_rate(symbol)
            if abs(float(f_data.get('fundingRate', 0))) > FUNDING_SHIELD: return None

            return {
                'symbol': symbol,
                'side': 'buy' if is_buy else 'sell',
                'price': cur_p,
                'dna': dna
            }
    except: pass
    return None

async def signal_hunter(exchange):
    """Главный цикл поиска входов (Multi-Slot Ready)"""
    log("🏹 Охотник за сигналами активирован.")
    symbols = list(memory.dna_fleet.keys())

    while memory.is_running:

        if int(time.time()) % 300 == 0:
           log(f"🏹 Охотник на чеку. Сканирую {len(memory.dna_fleet)} секторов в режиме {memory.current_regime.upper()}...")
        # Если все слоты заняты - ждем и не тратим API вес
        if memory.slots_occupied >= MAX_ACTIVE_SLOTS:
            await asyncio.sleep(2)
            continue

        # Проверяем монеты пачками по 5 штук (чтобы не спамить Binance)
        for i in range(0, len(symbols), 5):
            batch = symbols[i:i+5]
            tasks = [check_signal(exchange, s) for s in batch]
            results = await asyncio.gather(*tasks)

            for res in results:
                if res and memory.slots_occupied < MAX_ACTIVE_SLOTS:
                    # Проверяем, не выходили ли мы только что из этой монеты
                    if res['symbol'] in memory.active_pos: continue

                    # Сигнал подтвержден -> Идем на вход
                    await execute_entry(exchange, res)

            await asyncio.sleep(0.1) # Микро-пауза между пачками
        await asyncio.sleep(0.5) # Пауза после полного круга

async def execute_entry(exchange, signal):
    """Асинхронная установка плеча и вход в позицию"""
    symbol = signal['symbol']
    side = signal['side']
    price = signal['price']
    dna = signal['dna']

    try:
        off_val = dna['l_off'] if side == 'buy' else dna['s_off']
        log(f"🎯 СИГНАЛ: {symbol} {side.upper()} | Offset: {off_val} | Price: {price} | Mode: {memory.current_regime.upper()}")
        #log(f"🎯 СИГНАЛ: {symbol} {side.upper()} | Offset: {dna['offset']} | Price: {price}")

        # 1. Подготовка "почвы" (Leverage & Margin Mode)
        # На Binance это критично делать перед каждым входом
        try:
            await exchange.set_margin_mode('ISOLATED', symbol)
        except: pass # Если уже стоит ISOLATED - биржа выдаст ошибку, скипаем

        try:
#            await exchange.set_leverage(int(dna['lev']), symbol)
            await exchange.set_leverage(SAFE_LEVERAGE_LIMIT, symbol)
        except Exception as e:
            log(f"⚠️ Ошибка плеча {symbol}: {e}")

        # 2. Расчет объема (С учетом активных слотов)
        # Делим доступную маржу на количество свободных слотов
        slots_left = MAX_ACTIVE_SLOTS - memory.slots_occupied
        if slots_left <= 0: slots_left = 1

        # Выделяем долю USDT на этот слот
        margin_for_slot = (memory.available_margin / slots_left) * RISK_GEAR

        # Проверка на минимальный лот Binance (~5-10 USDT номинала)
        if margin_for_slot < 5.0:
            log(f"⚠️ Мало маржи для {symbol} (${round(margin_for_slot, 2)}). Пропуск.")
            return

        # Считаем количество контрактов
        amount_base = (margin_for_slot * dna['lev']) / price
        amount = float(exchange.amount_to_precision(symbol, amount_base))

        if amount <= 0: return

        # 3. Выставление ордера (MARKET для мгновенного захвата тени)
#        log(f"🚀 ВХОД {symbol}: {side.upper()} | Vol: {amount} | Margin: ${round(margin_for_slot, 2)}")
        log(f"🚀 ВХОД {symbol} {side.upper()} | Vol: {amount} | Bal: ${round(memory.total_wallet, 2)}")

        order = await exchange.create_market_order(symbol, side, amount)

        if order:
            # ОБЯЗАТЕЛЬНО РАСКОММЕНТИРУЙ ЭТО:
            # Мгновенно сообщаем мониторингу о новой позиции, не дожидаясь трекера
            memory.active_pos[symbol] = {
                'symbol': symbol,
                'side': side,
                'entryPrice': price,
                'contracts': amount
            }
            # 4. Инициализация "Живой Памяти" для этой сделки
            memory.entry_times[symbol] = time.time()
            memory.be_levels[symbol] = dna['sl'] # Начальный стоп
            memory.tp_status[symbol] = {'tp1': False, 'tp2': False}

            # Храповик: инициализируем стартовую ступень
            memory.step_be[symbol] = dna['sl']

            log(f"✅ Позиция {symbol} открыта успешно.")
            # Даем Position Tracker время обновить memory.slots_occupied
            await asyncio.sleep(1)

    except Exception as e:
        log(f"❌ ОШИБКА ВХОДА {symbol}: {e}")

async def safe_close_all_orders(exchange, symbol):
    """Экстренная очистка всех ордеров по монете"""
    try:
        await exchange.cancel_all_orders(symbol)
    except:
        pass

async def monitor_logic(exchange, symbol, pos):
    """Индивидуальный присмотр за каждой позицией (V16.0)"""
    try:
        dna = memory.dna_fleet.get(symbol)
        if not dna: return

        # 1. Текущие параметры сделки
        cur_p = memory.prices.get(symbol)
        if not cur_p: return

        side = pos['side'].lower()
        entry = float(pos['entryPrice'])
        size = abs(float(pos['contracts'])) # Текущий остаток

        # Расчет чистого профита
        profit = (cur_p / entry - 1) if side == 'long' or side == 'buy' else (entry / cur_p - 1)
        elapsed = time.time() - memory.entry_times.get(symbol, time.time())

        # 2. ДИНАМИЧЕСКИЙ ХРАПОВИК (Ступенчатый БУ)
        if symbol not in memory.step_be: memory.step_be[symbol] = dna['sl']

        # Ступень 1: Подтяжка к +0.4%
        if profit >= dna['step1_p'] and memory.step_be[symbol] < dna['step1_be']:
            memory.step_be[symbol] = dna['step1_be']
            log(f"🛡️ ХРАПОВИК {symbol}: Ступень 1 активирована (+{round(dna['step1_be']*100, 2)}%)" )

        # Ступень 2: Подтяжка к +1.0%
        if profit >= dna['step2_p'] and memory.step_be[symbol] < dna['step2_be']:
            memory.step_be[symbol] = dna['step2_be']
            log(f"🛡️ ХРАПОВИК {symbol}: Ступень 2 активирована (+{round(dna['step2_be']*100, 2)}%)" )

        # 3. КАСКАДНАЯ ФИКСАЦИЯ (Тройной удар)
        exit_side = 'sell' if side == 'long' or side == 'buy' else 'buy'
        status = memory.tp_status.get(symbol, {'tp1': False, 'tp2': False})

        # ТЕЙК №1 (30% от первоначального объема)
        if not status['tp1'] and profit >= dna['tp1']:
            # Расчет qty_fix через precision Binance
            qty_fix = float(exchange.amount_to_precision(symbol, size * dna['share1']))
            if qty_fix > 0:
                # Убираем флаг reduceOnly, если он вызывает отказ,
                # или даем микро-паузу перед запросом
                await asyncio.sleep(0.1)
                #await exchange.create_market_order(symbol, exit_side, qty_fix, params={'reduceOnly': True})
                await exchange.create_order(symbol, 'limit', exit_side, qty_fix, cur_p, params={'reduceOnly': True})
                log(f"🎯 ТЕЙК №1 {symbol} | Prof: {round(profit*100,2)}% | Bal: ${round(memory.total_wallet, 2)}")
#               log(f"🎯 ТЕЙК №1 {symbol}: Фиксация {int(dna['share1']*100)}% по цене {cur_p}")
 #               await exchange.create_market_order(symbol, exit_side, qty_fix, params={'reduceOnly': True})
                status['tp1'] = True
                memory.tp_status[symbol] = status

        # ТЕЙК №2 (40% от первоначального -> ~57% от остатка)
        if status['tp1'] and not status['tp2'] and profit >= dna['tp2']:
            qty_fix = float(exchange.amount_to_precision(symbol, size * 0.57))
            if qty_fix > 0:
                try:
                    await asyncio.sleep(0.1)
                   # await exchange.create_market_order(symbol, exit_side, qty_fix, params={'reduceOnly': True})
                    await exchange.create_order(symbol, 'limit', exit_side, qty_fix, cur_p, params={'reduceOnly': True})
                    log(f"🎯 ТЕЙК №2 {symbol} | Prof: {round(profit*100,2)}% | Bal: ${round(memory.total_wallet, 2)}")
                    status['tp2'] = True
                    memory.tp_status[symbol] = status
                except Exception as e:
                    if "2022" in str(e): await asyncio.sleep(0.5)
#-------
#                log(f"🎯 ТЕЙК №2 {symbol}: Фиксация 40% по цене {cur_p}")
#                await exchange.create_market_order(symbol, exit_side, qty_fix, params={'reduceOnly': True})
#                status['tp2'] = True
#                memory.tp_status[symbol] = status

        # 4. УСЛОВИЯ ПОЛНОГО ВЫХОДА (TP3, SL, Surgeon, QC)
        is_tp3 = profit >= dna['tp3']
        is_sl = profit <= memory.step_be[symbol]
        is_surgeon = not status['tp1'] and elapsed > dna['surg_t']*60 and profit < dna['surg_p']

        # Quick-Cut (если монета в спи# Quick-Cut берем из индивидуальных параметров JSON (qc_t и qc_p)
        qc_time_limit = dna.get('qc_t', 110) # Защита get, если ключ пропадет
        qc_profit_limit = dna.get('qc_p', -0.0055)

        is_qc = elapsed > qc_time_limit and profit < qc_profit_limit

        if is_tp3 or is_sl or is_surgeon or is_qc:
            reason = "🎯 TP3" if is_tp3 else "🛡️ SL/BE" if is_sl else "⚔️ SURGEON" if is_surgeon else "✂️ QC"
#            log(f"🚨 ВЫХОД {reason}: {symbol} | Profit: {round(profit*100, 2)}%")
            # ПЫТАЕМСЯ ЗАКРЫТЬ ПОКА НЕ ЗАКРОЕМ (Цикл против ошибки -2022)
            for attempt in range(3):
                try:
                    await exchange.create_market_order(symbol, exit_side, size, params={'reduceOnly': True})
                    log(f"🚨 ВЫХОД {reason}: {symbol} | Profit: {round(profit*100, 2)}% | Bal: ${round(memory.total_wallet, 2)}")
                    break
                except Exception as e:
                    log(f"⏳ Retry exit {symbol} (Error -2022)...")
                    await asyncio.sleep(1)

            # Закрываем ВЕСЬ остаток по рынку (Market) для 100% надежности
#            await exchange.create_market_order(symbol, exit_side, size, params={'reduceOnly': True})
            await safe_close_all_orders(exchange, symbol)

            # Очистка памяти для этого символа
            if symbol in memory.tp_status: del memory.tp_status[symbol]
            if symbol in memory.be_levels: del memory.be_levels[symbol]
            if symbol in memory.step_be: del memory.step_be[symbol]

    except Exception as e:
        log(f"⚠️ Ошибка мониторинга {symbol}: {e}")

async def monitoring_cycle(exchange):
    """Цикл слежения за всеми открытыми позициями одновременно"""
    log("👁️ Мониторинг позиций запущен.")
    while memory.is_running:
        if memory.active_pos:
            # Создаем задачи мониторинга для каждой активной позиции
            tasks = [monitor_logic(exchange, sym, data) for sym, data in memory.active_pos.items()]
            await asyncio.gather(*tasks)
        await asyncio.sleep(0.5) # Частота проверки - 2 раза в секунду

async def run_titan_v1():
    """Главный дирижер системы Titan-Binance"""
    log("🚀 Инициализация TITAN-BINANCE V1.0 [WS-STREAM]...")

    # 1. Загрузка ДНК
    load_all_dna()

    # 2. Подключение к бирже
    exchange = await init_exchange()
    # --- НОВАЯ СТРОКА ---
    await warm_up_btc_history(exchange) 
    # --------------------
    
    try:
        log("🛰️ Подключение к квантовым потокам данных...")

        # 3. Запуск параллельных фоновых задач
        tasks = [
            asyncio.create_task(price_stream()),        # Поток цен
            asyncio.create_task(update_balance(exchange)), # Поток баланса
            asyncio.create_task(update_market_regime()), # Активация коробки передач
            asyncio.create_task(position_tracker(exchange)), # Поток позиций
            asyncio.create_task(signal_hunter(exchange)),    # Охотник
            asyncio.create_task(monitoring_cycle(exchange))  # Мониторинг
        ]

        log("✅ СИСТЕМА АКТИВИРОВАНА. Режим: Мульти-слот V16.0")

        # 4. Поддержание работы всех задач
        await asyncio.gather(*tasks)

    except Exception as e:
        log(f"🆘 КРИТИЧЕСКИЙ СБОЙ СИСТЕМЫ: {e}")
    finally:
        memory.is_running = False
        await exchange.close()
        log("🔌 Система штатно отключена.")

# ==========================================
# ТОЧКА ВХОДА (Запуск Python скрипта)
# ==========================================
if __name__ == "__main__":
    try:
        asyncio.run(run_titan_v1())
    except KeyboardInterrupt:
        log("🛑 Ручная остановка Архитектором.")
