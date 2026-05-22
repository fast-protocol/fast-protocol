
MAX_SLOTS = 2               # Максимум параллельных позиций
RISK_GEAR = 0.50            # Множитель маржи слота (0.1 - 1.0)
PRIMARY_SL_PCT = 0.012      # Жесткий серверный Стоп-Лосс (-1.2%)

# --- ЦЕЛИ TRIPLE-GEAR V16.2 ---
TP1_PCT = 0.0065            # Тейк 1 (+0.65%) - Закрытие 30% объема
TP2_PCT = 0.0185            # Тейк 2 (+1.85%) - Закрытие 40% объема
TP3_PCT = 0.0420            # Тейк 3 (+4.20%) - Закрытие остатка 30%

# Геометрия полос Боллинджера и Капкана
BB_PERIOD = 20
BB_STD = 2.2
ENTRY_TRIGGER_OFFSET = 0.0018  # Сигнальный вылет (0.18%)
ENTRY_ORDER_OFFSET = 0.0020    # Снайперский отступ лимитного капкана (0.20% от полосы)
LIMIT_ORDER_TTL = 75           # Время жизни лимитки в стакане (секунды)

# Список приоритетных фьючерсных секторов MEXC
PRIORITY_LIST = [
    'SOL/USDT:USDT', 'NEAR/USDT:USDT', 'LDO/USDT:USDT', 'OP/USDT:USDT',
    'APT/USDT:USDT', 'MANA/USDT:USDT', 'POL/USDT:USDT', '1INCH/USDT:USDT'
]

class GlobalMemory:
    def __init__(self):
        self.is_running = True
        self.available = 0.0
        self.total_wallet = 0.0
        self.slots_occupied = 0

        # Потоки цен и истории Поводыря
        self.prices = {}
        self.btc_history = []
        self.last_btc_push = 0

        # Снайперские кэш-таблицы состояний (Защита от KeyError)
        self.active_pos = {}
        self.stop_placed = {}
        self.tp1_fixed = {}
        self.tp2_fixed = {}
        self.step_be = {}
        self.max_pnl_observed = {}
        self.limit_orders = {} # Трекер выставленных капканов: {symbol: {id, time, price, side, qty}}

memory = GlobalMemory()

def log(msg):
    """Каноническое двойное логирование: Экран + Файл"""
    t = datetime.now().strftime('%H:%M:%S')
    # Дублируем запись в файл
    try:
        with open("berserk_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{t}] {msg}\n")
    except:
        pass
    print(f"[{t}] 🏛️ {msg}", flush=True)

async def init_exchange():
    """Синхронная инициализация эталонного CCXT-движка MEXC V17.0"""
    exchange = ccxt.mexc({
        'apiKey': API_KEY,
        'secret': SECRET_KEY,
        'options': {'defaultType': 'swap', 'positionMode': False},
        'enableRateLimit': True
    })
    try:
        bal = exchange.fetch_balance({'type': 'swap'})
        if isinstance(bal, dict) and 'USDT' in bal:
            memory.available = float(bal['USDT'].get('free', 0.0))
            memory.total_wallet = float(bal['USDT'].get('total', 0.0))
    except Exception as e:
        log(f"⚠️ Ошибка считывания стартового баланса: {e}")
        memory.available = 0.0

    log(f"ЛИМИТНЫЙ СНАЙПЕР BERSERK V17.0 ОНЛАЙН. Маржа: ${round(memory.available, 2)}")
    return exchange

# --- [ВОЗВРАЩЕНИЕ ИСТИННОГО МOНOЛИТА smart_order V17.0 БЕЗ AWAIT] ---
def smart_order(exchange, symbol, side, amount, is_limit=False, price=None, is_exit=False, is_stop=False):
    """Синхронный стриминг ордеров с принудительной изоляцией маржи openType=1"""
    try:
        amount_str = exchange.amount_to_precision(symbol, amount)
        qty = float(amount_str)
        if qty <= 0:
            return False

        # Каноническая упакoвка параметров по правилам старой рабочей версии
        params = {
            'openType': 1,      # 1: Strict Isolated Маржа!
            'leverage': int(25) # Жесткое требование биржи для ISO-режима
        }
        if is_exit or is_stop:
            params['reduceOnly'] = True

        # СЦЕНАРИЙ 1: Жесткий серверный СТОП-МАРКЕТ
        if is_stop:
            if price is None: return False
            params['stopPrice'] = float(exchange.price_to_precision(symbol, price))
            order = exchange.create_order(symbol, 'market', side, qty, None, params)
            return order

        # СЦЕНАРИЙ 2: Пассивный Лимитный Капкан Maker
        elif is_limit:
            if price is None: return False
            exact_price = float(exchange.price_to_precision(symbol, price))
            order = exchange.create_order(symbol, 'limit', side, qty, exact_price, params)
            return order

        # СЦЕНАРИЙ 3: Агрессивный Taker (Выход / Тейк)
        else:
            order = exchange.create_order(symbol, 'market', side, qty, None, params)
            return order

    except Exception as e:
        log(f"⚠️ Сбой шлюза ордеров {symbol} ({side.upper()}): {e}")
        return False

async def price_stream(exchange_pro):
    """Высокочастотный WebSocket-стриминг цен + Посекундный трекер Поводыря BTC"""
    log(f"📡 Запуск квантового WebSocket-потока цен для {len(PRIORITY_LIST)} активов...")

    # Инициализируем стартовые отметки цен, чтобы избежать KeyError
    for sym in PRIORITY_LIST:
        memory.prices[sym] = 0.0

    while memory.is_running:
        try:
            # Читаем живые тикеры в реальном времени через ccxt.pro
            tickers = await exchange_pro.watch_tickers(PRIORITY_LIST)
            now = time.time()

            for symbol, t_data in tickers.items():
                if symbol in memory.prices:
                    val = float(t_data.get('last', t_data.get('close', 0.0)))
                    if val > 0:
                        memory.prices[symbol] = val

                    # СИНХРОНИЗАЦИЯ ПОВОДЫРЯ: Ловим Биткоин для наполнения 15-минутной истории
                    if "BTC/USDT" in symbol:
                        # Записываем чистую цену закрытия строго раз в 60 секунд (без тикового каша-шума)
                        if now - memory.last_btc_push >= 60:
                            memory.btc_history.append(val)
                            if len(memory.btc_history) > 100:
                                memory.btc_history.pop(0)
                            memory.last_btc_push = now

        except Exception as ws_err:
            log(f"⚠️ Ошибка WebSocket потока цен: {ws_err}")
            await asyncio.sleep(1)

async def check_signal(exchange, symbol):
    """Снайперский сканер V16.2 с фильтрами Синдиката, Каскадных ножей и Адаптивного Объема"""
    try:
        cur_p = memory.prices.get(symbol, 0.0)
        if cur_p <= 0:
            return None

        # --- [ФИЛЬТР 1: BTC SPREAD SHIELD — 15М СПРЕД ПОВОДЫРЯ] ---
        if len(memory.btc_history) >= 15:
            btc_window = memory.btc_history[-15:]
            btc_spread = (max(btc_window) / min(btc_window) - 1) * 100
            if btc_spread < 0.06:
                return None  # Биткоин в мертвом флэте — капли не тратим

        # --- [ВРЕЗКА V16.5: ФИЛЬТР ПЛОТНОСТИ ТРЕНДА БИТКОИНА (BTC MOMENTUM SHIELD)] ---
        if len(memory.btc_history) >= 3:
            btc_momentum_window = memory.btc_history[-3:]
            m1_diff = abs(btc_momentum_window[-1] - btc_momentum_window[-2])
            m2_diff = abs(btc_momentum_window[-2] - btc_momentum_window[-3])
            avg_min_move_pct = ((m1_diff + m2_diff) / 2) / btc_momentum_window[-1] * 100

            # Если Биткоин вяло ползет со скоростью менее 0.025% в минуту — блокируем взвод капкана
            if avg_min_move_pct < 0.025:
                return None

        # --- [ЖЕСТКИЙ ФИКС V16.8: СИНХРОННЫЙ СБОР СКОЛЬЗЯЩЕГО 4H ОКНА НА МЕХС] ---
        try:
            # Очищаем символ от фьючерсного хвоста для REST-метода MEXC (из 'SOL/USDT:USDT' делаем 'SOL/USDT')
            clean_rest_symbol = symbol.split(':')[0]

            # Запрашиваем 48 пятиминутных свечей (48 * 5 мин = 240 мин = ровно 4 часа скользящего трека)
            ohlcv_4h = exchange.fetch_ohlcv(clean_rest_symbol, '5m', limit=48)
            if len(ohlcv_4h) >= 10:
                # В массиве OHLCV CCXT: индекс 2 — это High, индекс 3 — это Low
                highs_4h = [float(candle[2]) for candle in ohlcv_4h]
                lows_4h = [float(candle[3]) for candle in ohlcv_4h]

                max_4h = max(highs_4h)
                min_4h = min(lows_4h)

                rolling_range_4h = (max_4h / min_4h - 1) * 100
                if rolling_range_4h > 4.5:
                    return None # Монета перегрета — пропускаем сигнал
        except Exception as e:
            log(f"⚠️ Ошибка 4H фильтра: {e}")
            pass

        # Запрашиваем историю минутных свечей альта через REST шлюз MEXC
        df_candles = exchange.fetch_ohlcv(symbol, '1m', limit=25)
        if len(df_candles) < BB_PERIOD + 5:
            return None

        # Расчет Боллинджера по канонической формуле
        closes = [float(c[4]) for c in df_candles[-BB_PERIOD-1:-1]] # Строго по закрытым свечам
        ma20 = sum(closes) / BB_PERIOD
        variance = sum((x - ma20) ** 2 for x in closes) / BB_PERIOD
        std = variance ** 0.5
        upper_band = ma20 + (std * BB_STD)
        lower_band = ma20 - (std * BB_STD)

        # Флаги первичного вылета за границы Боллинджера
        is_sell_candidate = cur_p >= upper_band
        is_buy_candidate = cur_p <= lower_band

        if not (is_sell_candidate or is_buy_candidate):
            return None

        # --- [ФИЛЬТР 2: ADAPTIVE VOLUME SHIELD — АДАПТИВНЫЙ ФИЛЬТР ОБЪЕМА] ---
        live_volume = float(df_candles[-1][5])  # Объем текущей живой минутки
        mean_volume = sum(float(c[5]) for c in df_candles[-6:-1]) / 5  # Средний за прошлые 5 минут

        if mean_volume <= 0:
            return None

        volume_ratio = live_volume / mean_volume
        is_meme = any(m in symbol.upper() for m in ['PEPE', 'SHIB', 'WIF', 'POPCAT', 'DOGE', 'BONK'])
        required_ratio = 1.8 if is_meme else 1.1

        if volume_ratio < required_ratio:
            return None  # Пустой шумовой прокол стакана без плотности ордеров

        # --- [ФИЛЬТР 3: PRE-CANDLE SHIELD — КАСКАДНЫЙ НОЖ ПРЕДЫСТОРИИ] ---
        p_c1 = df_candles[-2]  # Прошлая закрытая минута
        p_c2 = df_candles[-3]  # 2 минуты назад
        p_c3 = df_candles[-4]  # 3 минуты назад

        is_3_green = (p_c1[4] > p_c1[1]) and (p_c2[4] > p_c2[1]) and (p_c3[4] > p_c3[1])
        is_3_red   = (p_c1[4] < p_c1[1]) and (p_c2[4] < p_c2[1]) and (p_c3[4] < p_c3[1])

        if is_buy_candidate and is_3_red:
            return None  # Падающий каскадный нож продавца — ловить лимиткой запрещено
        if is_sell_candidate and is_3_green:
            return None  # Растущая вертикальная ракета покупателя — шортить капканом запрещено

        # --- [ФИЛЬТР 4: ГЕОМЕТРИЯ СВЕЧИ (ТВОЯ СЕРВЕРНАЯ СТРУКТУРА MARUBOZU)] ---
        c_open, c_high, c_low, c_close = float(df_candles[-1][1]), float(df_candles[-1][2]), float(df_candles[-1][3]), float(df_candles[-1][4])
        live_candle_range = abs(c_high - c_low)
        if live_candle_range <= 0:
            return None

        # Жесткие лимиты теней Marubozu из твоей оригинальной версии V16.0
        shadow_limit = 0.40
        body_limit = 0.50

        if is_buy_candidate:
            up_shadow = abs(c_high - max(c_open, c_close))
            long_body = abs(c_open - c_close)
            if (up_shadow / live_candle_range) > shadow_limit or (long_body / live_candle_range) < body_limit:
                return None

            # Вычисляем точную ювелирную цену лимитного капкана под нижней полосой
            order_price = lower_band * (1 - ENTRY_ORDER_OFFSET)
            return {'side': 'buy', 'price': order_price, 'upper_band': upper_band, 'lower_band': lower_band}

        elif is_sell_candidate:
            dn_shadow = abs(min(c_open, c_close) - c_low)
            short_body = abs(c_open - c_close)
            if (dn_shadow / live_candle_range) > shadow_limit or (short_body / live_candle_range) < body_limit:
                return None

            # Вычисляем точную ювелирную цену лимитного капкана над верхней полосой
            order_price = upper_band * (1 + ENTRY_ORDER_OFFSET)
            return {'side': 'sell', 'price': order_price, 'upper_band': upper_band, 'lower_band': lower_band}

    except Exception as scan_err:
        log(f"⚠ Ошибка сканирования {symbol}: {scan_err}")
        return None
    return None

async def monitor_logic(exchange):
    """Адаптивное управление выходами V16.9: Фикс лотов SOL, Квантовый Храповик 60с и Синдром Сползания"""
    last_pos_sync = 0
    while memory.is_running:
        # --- ЖЕСТКИЙ ФИКС ОБЪЯВЛЕНИЯ ПЕРЕМЕННОЙ V17.1.1 ---
        now_time = time.time()

        # --- [ВРЕЗКА V17.1: ЖИВОЙ ФОНОВЫЙ ТРЕКЕР УСЫНОВЛЕНИЯ ПОЗИЦИЙ MEXC] ---
        if now_time - last_pos_sync >= 5: # Опрашиваем биржу раз в 5 секунд прямо во время торгов!
            try:
                raw_positions = exchange.fetch_positions(None, {'type': 'swap'})
                current_mexc_active = []

                for p in raw_positions:
                    vol = abs(float(p.get('contracts', p.get('positionAmt', 0.0))))
                    if vol > 0.00001:
                        raw_sym = p.get('symbol', p.get('pair', ''))
                        clean_sym = raw_sym.replace('_', '/').replace(':USDT', '')
                        if '/' not in clean_sym and 'USDT' in clean_sym:
                            clean_sym = clean_sym.replace('USDT', '/USDT')
                        fleet_key = f"{clean_sym}:USDT"

                        if fleet_key in PRIORITY_LIST or clean_sym in PRIORITY_LIST:
                            target_key = fleet_key if fleet_key in PRIORITY_LIST else clean_sym
                            current_mexc_active.append(target_key)

                            # Если позиция открылась на бирже, а в памяти её нет — мгновенно усыновляем!
                            if target_key not in memory.active_pos:
                                side_raw = p.get('side', p.get('positionSide', 'LONG')).lower()
                                side = 'buy' if 'long' in side_raw or 'buy' in side_raw else 'sell'
                                entry_price = float(p.get('entryPrice', p.get('price', 0.0)))

                                log(f"🔗 ЖИВОЙ ПЕРЕХВАТ MEXC: Обнаружена открытая сделка по {target_key} ({vol} лотов). Берем под контроль выходов!")
                                memory.active_pos[target_key] = {
                                    'side': side, 'vol': vol, 'price': entry_price, 'entry_time': time.time(),
                                    'dna': {'l_off': ENTRY_ORDER_OFFSET, 's_off': ENTRY_ORDER_OFFSET}
                                }
                                memory.slots_occupied = len(current_mexc_active)

                # Очищаем системные флаги из памяти для закрытых на бирже позиций
                for sym in list(memory.active_pos.keys()):
                    if sym not in current_mexc_active:
                        log(f"🧹 Позиция {sym} закрыта на MEXC. Вычищаем оперативную память.")
                        if sym in memory.active_pos: del memory.active_pos[sym]
                        if sym in memory.tp1_fixed: del memory.tp1_fixed[sym]
                        if sym in memory.tp2_fixed: del memory.tp2_fixed[sym]
                        if sym in memory.stop_placed: del memory.stop_placed[sym]
                        if sym in memory.max_pnl_observed: del memory.max_pnl_observed[sym]

                memory.slots_occupied = len(current_mexc_active)
                last_pos_sync = now_time
            except:
                pass
        # ---------------------------------------------------------------------



        for symbol, pos in list(memory.active_pos.items()):
            try:
                cur_p = memory.prices.get(symbol, 0.0)
                if cur_p <= 0: continue

                # Расчет чистого PNL и времени жизни позиции
                profit = (cur_p / pos['price'] - 1) if pos['side'] == 'buy' else (pos['price'] / cur_p - 1)
                age = time.time() - pos['entry_time']
                exit_side = 'sell' if pos['side'] == 'buy' else 'buy'
                mexc_market_id = symbol.replace('/', '').replace(':USDT', '')

                # --- 1. ВЫСТАВЛЕНИЕ ЖЕСТКОГО СЕРВЕРНОГО СТОП-ЛОССА НА МЕХС ---
                if not memory.stop_placed.get(symbol):
                    try:
                        sl_price = pos['price'] * (1 - PRIMARY_SL_PCT) if pos['side'] == 'buy' else pos['price'] * (1 + PRIMARY_SL_PCT)
                        sl_price_precision = float(exchange.price_to_precision(symbol, sl_price))
                        exact_vol = exchange.amount_to_precision(symbol, pos['vol'])

                        try: exchange.fapiPrivateDeleteAlgoOpenOrders({'symbol': mexc_market_id})
                        except: pass

                        smart_order(exchange, symbol, exit_side, exact_vol, price=sl_price_precision, is_stop=True)
                        memory.stop_placed[symbol] = sl_price_precision
                        log(f"🛡️ СЕРВЕРНЫЙ СТОП ВЫСТАВЛЕН: {symbol} @  {sl_price_precision}")
                    except Exception as e:
                        log(f"🆘 Ошибка автостопа MEXC для {symbol}: {e}")
                        memory.stop_placed[symbol] = pos['price']

                # --- [УЗЕЛ V16.9: КВАНТОВЫЙ ДЕЦЕНТРАЛИЗОВАННЫЙ ВЕНТИЛЬ ВЫХОДОВ НА МЕХС] ---
                if profit > 0:
                    memory.max_pnl_observed[symbol] = max(profit, memory.max_pnl_observed.get(symbol, profit))

                # ТРИГГЕР А: Раннее отсечение сползания альта с учетом проскальзывания на MEXC (60с / -0.08%)
                if age > 60 and profit < -0.0008:
                    log(f"🛡️ Decay Shield V16.9: {symbol} срезан на 60с (Лосс: {round(profit*100, 2 )}%)")
                    action_triggered_decay = False
                    try:
                        try: exchange.fapiPrivateDeleteAlgoOpenOrders({'symbol': mexc_market_id})
                        except: pass
                        smart_order(exchange, symbol, exit_side, pos['vol'], is_exit=True)
                        action_triggered_decay = True
                    except Exception as e: log(f"⚠️ Ошибка утилизации: {e}")

                    if action_triggered_decay:
                        for k in [symbol, symbol.replace(':USDT', '')]:
                            if k in memory.active_pos: del memory.active_pos[k]
                            if k in memory.tp1_fixed: del memory.tp1_fixed[k]
                            if k in memory.tp2_fixed: del memory.tp2_fixed[k]
                            if k in memory.stop_placed: del memory.stop_placed[k]
                            if k in memory.step_be: del memory.step_be[k]
                            if k in memory.max_pnl_observed: del memory.max_pnl_observed[k]
                        memory.slots_occupied = max(0, memory.slots_occupied - 1)
                        return

                # ТРИГГЕР Б: Синдром Сползания Импульса (Выдох крупного игрока на МЕХС)
                if symbol in memory.max_pnl_observed and memory.max_pnl_observed[symbol] >= 0.0025:
                    current_decay_pct = (1 - (profit / memory.max_pnl_observed[symbol])) * 100
                    if current_decay_pct > 70.0:
                        log(f"🏁 СИНДРОМ СПОЛЗАНИЯ ИМПУЛЬСА: {symbol} закрыт на МЕХС. ММ выдохся (Пик: +{round(memory.max_pnl_observed[symbol]*100,2)}%)")
                        action_triggered_momentum_dead = False
                        try:
                            try: exchange.fapiPrivateDeleteAlgoOpenOrders({'symbol': mexc_market_id})
                            except: pass
                            smart_order(exchange, symbol, exit_side, pos['vol'], is_exit=True)
                            action_triggered_momentum_dead = True
                        except Exception as e: log(f"⚠️ Ошибка Синдрома Сползания: {e}")

                        if action_triggered_momentum_dead:
                            for k in [symbol, symbol.replace(':USDT', '')]:
                                if k in memory.active_pos: del memory.active_pos[k]
                                if k in memory.tp1_fixed: del memory.tp1_fixed[k]
                                if k in memory.tp2_fixed: del memory.tp2_fixed[k]
                                if k in memory.stop_placed: del memory.stop_placed[k]
                                if k in memory.step_be: del memory.step_be[k]
                                if k in memory.max_pnl_observed: del memory.max_pnl_observed[k]
                            memory.slots_occupied = max(0, memory.slots_occupied - 1)
                            return

                # --- 3. ШТАТНАЯ ФИКСАЦИЯ ТЕЙКА 1 (С ЖЕСТКИМ ФИКСОМ ОКРУГЛЕНИЯ МАЛЫХ ЛОТОВ SOL) ---
                if not memory.tp1_fixed.get(symbol) and profit >= TP1_PCT:
                    try:
                        raw_close_qty = pos['vol'] * 0.30
                        close_qty_str = exchange.amount_to_precision(symbol, raw_close_qty)
                        close_qty = float(close_qty_str)

                        # ЗАЩИТА ОТ ОКРУГЛЕНИЯ В НOЛЬ (Для лотов SOL/LDO)
                        if close_qty <= 0 or close_qty >= pos['vol']:
                            log(f"⚠ ЛОТ {symbol} СЛИШКОМ МАЛ ДЛЯ ДРОБЛЕНИЯ ({pos['vol']}): Фиксируем 100% объема в Тейк 1 по рынку!")
                            try: exchange.fapiPrivateDeleteAlgoOpenOrders({'symbol': mexc_market_id})
                            except: pass
                            smart_order(exchange, symbol, exit_side, pos['vol'], is_exit=True)

                            for k in [symbol, symbol.replace(':USDT', '')]:
                                if k in memory.active_pos: del memory.active_pos[k]
                                if k in memory.tp1_fixed: del memory.tp1_fixed[k]
                                if k in memory.tp2_fixed: del memory.tp2_fixed[k]
                                if k in memory.stop_placed: del memory.stop_placed[k]
                                if k in memory.max_pnl_observed: del memory.max_pnl_observed[k]
                            memory.slots_occupied = max(0, memory.slots_occupied - 1)
                            return

                        # Если лот позволяет дробить — фиксируем базовые 30%
                        smart_order(exchange, symbol, exit_side, close_qty, is_exit=True)
                        memory.tp1_fixed[symbol] = True
                        pos['vol'] = float(exchange.amount_to_precision(symbol, pos['vol'] - close_qty))
                        log(f"🎯 ТЕЙК-1 ВЫПОЛНЕН: {symbol} зафиксировано 30% объема (+{round(TP1_PCT*100,2)}%)")

                        #try: exchange.fapiPrivateDeleteAlgoOpenOrders({'symbol': mexc_market_id})
                        #except: pass
                        try:
                            exchange.cancel_all_orders(symbol, {'params': {'type': 5}}) # Удаляет только триггерные стопы
                        except:
                            pass
                        #bu_price = pos['price'] * (1 + 0.0015) if pos['side'] == 'buy' else pos['price'] * (1 - 0.0015)
                        bu_price = pos['price'] * (1 - 0.0005) if pos['side'] == 'buy' else pos['price'] * (1 + 0.0005)
                        bu_price_precision = float(exchange.price_to_precision(symbol, bu_price))

                        exact_remainder_vol = float(exchange.amount_to_precision(symbol, pos['vol']))
                        smart_order(exchange, symbol, exit_side, exact_remainder_vol, price=bu_price_precision, is_stop=True)
                        memory.stop_placed[symbol] = bu_price_precision
                    except Exception as e:
                        log(f"🆘 Ошибка исполнения Тейка 1 {symbol}: {e}")

                # --- 4. ЛОГИКА ТЕЙК-ПРОФИТА 2 ---
                if memory.tp1_fixed.get(symbol) and not memory.tp2_fixed.get(symbol) and profit >= TP2_PCT:
                    try:
                        close_qty = float(exchange.amount_to_precision(symbol, pos['vol'] * 0.57))
                        if close_qty > 0:
                            smart_order(exchange, symbol, exit_side, close_qty, is_exit=True)
                            memory.tp2_fixed[symbol] = True
                            pos['vol'] = float(exchange.amount_to_precision(symbol, pos['vol'] - close_qty))
                            log(f"🏆 ТЕЙК-2 ВЫПОЛНЕН: {symbol} зафиксировано 40% объема (+{round(TP2_PCT*100,2)}%)")
                    except Exception as e: log(f"🆘 Ошибка Тейка 2 {symbol}: {e}")

                # --- 5. ЛОГИКА ТЕЙК-ПРОФИТА 3 ---
                if memory.tp2_fixed.get(symbol) and profit >= TP3_PCT:
                    log(f"👑 ТЕЙК-3 МЕГА-ФИНАЛ: {symbol} полностью закрыт (+{round(TP3_PCT*100,2)}%)")
                    action_triggered_tp3 = False
                    try:
                        try: exchange.fapiPrivateDeleteAlgoOpenOrders({'symbol': mexc_market_id})
                        except: pass
                        smart_order(exchange, symbol, exit_side, pos['vol'], is_exit=True)
                        action_triggered_tp3 = True
                    except Exception as e: log(f"⚠ Ошибка Тейка 3 для {symbol}: {e}")

                    if symbol in memory.active_pos: del memory.active_pos[symbol]
                    if symbol in memory.tp1_fixed: del memory.tp1_fixed[symbol]
                    if symbol in memory.tp2_fixed: del memory.tp2_fixed[symbol]
                    if symbol in memory.stop_placed: del memory.stop_placed[symbol]
                    if symbol in memory.max_pnl_observed: del memory.max_pnl_observed[symbol]
                    memory.slots_occupied = max(0, memory.slots_occupied - 1)
                    if action_triggered_tp3: return

            except Exception as loop_err: pass
        await asyncio.sleep(0.1)

async def main_logic():
    """Генеральный оркестратор Берсерка V16.9: Фикс балансов, CROSS-защита и REST-пушер"""
    exchange = await init_exchange()
    exchange_pro = ccxtpro.mexc({'apiKey': API_KEY, 'secret': SECRET_KEY, 'options': {'defaultType': 'swap'}})

    # Запускаем параллельные квантовые потоки цен и ведения позиций
    asyncio.create_task(price_stream(exchange_pro))
    asyncio.create_task(monitor_logic(exchange))

    log("🏹 Охота лимитными капканами Berserk V16.9 активирована. Патрулирую стаканы...")

    memory.last_btc_push = 0
    last_balance_update = 0


    # --- [ВРЕЗКА V16.9.6: БРОНИРОВАННЫЙ ШЛЮЗ АВТО-УСЫНОВЛЕНИЯ ПОЗИЦИЙ MEXC] ---
    try:
        log("🔗 Сканирование аккаунта на наличие открытых позиций...")
        # Запрашиваем все текущие фьючерсные удержания на аккаунте
        raw_positions = exchange.fetch_positions(None, {'type': 'swap'})

        for p in raw_positions:
            # Извлекаем чистый объем (notional/contracts) по правилам CCXT MEXC
            vol = abs(float(p.get('contracts', p.get('positionAmt', 0.0))))

            if vol > 0.00001:
                raw_sym = p.get('symbol', p.get('pair', ''))

                # Приводим к единому формату пульта (из OP_USDT или OP/USDT делаем OP/USDT:USDT)
                clean_sym = raw_sym.replace('_', '/').replace(':USDT', '')
                if '/' not in clean_sym and 'USDT' in clean_sym:
                    clean_sym = clean_sym.replace('USDT', '/USDT')
                fleet_key = f"{clean_sym}:USDT"

                if fleet_key in PRIORITY_LIST or clean_sym in PRIORITY_LIST:
                    target_key = fleet_key if fleet_key in PRIORITY_LIST else clean_sym

                    # Определяем сторону
                    side_raw = p.get('side', p.get('positionSide', 'LONG')).lower()
                    side = 'buy' if 'long' in side_raw or 'buy' in side_raw else 'sell'
                    entry_price = float(p.get('entryPrice', p.get('price', 0.0)))

                    if target_key not in memory.active_pos:
                        log(f"🔗 RECOVERED MEXC: Позиция {target_key} ({vol} лотов) успешно усыновлена флотоводцем!")
                        memory.active_pos[target_key] = {
                            'side': side,
                            'vol': vol,
                            'price': entry_price,
                            'entry_time': time.time(), # Стартуем таймер Храповика с текущей секунды
                            'dna': {'l_off': ENTRY_ORDER_OFFSET, 's_off': ENTRY_ORDER_OFFSET} # Временный кэш оффсета
                        }
                        memory.slots_occupied += 1
    except Exception as recover_err:
        log(f"⚠️ Критическая ошибка авто-усыновления MEXC: {recover_err}")
    # -------------------------------------------------------------------------

    while memory.is_running:
        try:
            now = time.time()

            # 1. АВТОНОМНЫЙ REST-ПУШЕР БИТКОИНА ДЛЯ MEXC
            if now - memory.last_btc_push >= 60:
                try:
                    btc_ticker = exchange.fetch_ticker('BTC/USDT:USDT')
                    btc_price = float(btc_ticker.get('last', btc_ticker.get('close', 0.0)))
                    if btc_price > 0:
                        memory.btc_history.append(btc_price)
                        if len(memory.btc_history) > 30: memory.btc_history.pop(0)
                        log(f"🛰️ ПОВОДЫРЬ СИНХРОНИЗ ИРОВАН (REST): BTC @ ${btc_price} | История: {len(memory.btc_history)}м")
                        memory.last_btc_push = now
                except Exception as btc_err:
                    log(f"⚠️ Ошибка REST-запроса Поводыря: {btc_err}")

            # 2. ФОНОВОЕ ОБНОВЛЕНИЕ БАЛАНСА (ЗАЩИТА ОТ ОБНУЛЕНИЯ И CODE 2005)
            if now - last_balance_update >= 15:
                try:
                    bal = exchange.fetch_balance({'type': 'swap'})
                    if isinstance(bal, dict) and 'USDT' in bal:
                        memory.available = float(bal['USDT'].get('free', 0.0))
                        last_balance_update = now
                except:
                    pass

            # 3. СКАНЕР СИГНАЛОВ И ВЫСТАВЛЕНИЕ КАПКАНОВ
            if memory.slots_occupied < MAX_SLOTS:
                for symbol in PRIORITY_LIST:
                    if symbol in memory.active_pos or symbol in memory.limit_orders:
                        continue

                    signal = await check_signal(exchange, symbol)
                    if signal and memory.slots_occupied < MAX_SLOTS:

                        # Расчет объема снайперского лота
                        amount_usdt = memory.available * RISK_GEAR * 25
                        qty = amount_usdt / signal['price']

                        # Выставляем пассивный лимитный капкан Maker
                        order = smart_order(exchange, symbol, signal['side'], qty, is_limit=True, price=signal['price'])
                        if order and isinstance(order, dict):
                            order_id = order.get('id')
                            memory.limit_orders[symbol] = {
                                'id': order_id, 'time': time.time(), 'price': signal['price'],
                                'side': signal['side'], 'qty': qty, 'dna': signal
                            }
                            log(f"🚀 ВЗВЕДЕН ЛИМИТНЫЙ КАПКАН Maker (ISOLATED): {symbol} {signal['side'].upper()} @ {signal['price']}")

            # --- [ВЕНИК АВТОСНОСА НЕИСПОЛНЕННЫХ ЛИМИТОК ПО TTL = 75с] ---
            for symbol in list(memory.limit_orders.keys()):
                order_data = memory.limit_orders[symbol]
                try:
                    open_orders = await exchange.fetch_open_orders(symbol)
                    is_still_open = any(o['id'] == order_data['id'] for o in open_orders)

                    if not is_still_open:
                        log(f"🔥 КАПКАН СРАБОТАЛ! {symbol} налит шпилькой по цене {order_data['price']}.")
                        memory.active_pos[symbol] = {
                            'side': order_data['side'], 'vol': order_data['qty'], 'price': order_data['price'],
                            'entry_time': time.time(), 'dna': order_data['dna']
                        }
                        memory.slots_occupied += 1
                        del memory.limit_orders[symbol]
                        continue
                except: pass

                if now - order_data['time'] > LIMIT_ORDER_TTL:
                    log(f"🧹 ВЕНИК ЛИМИТОК: Капкан по {symbol} утилизирован по времени TTL ({LIMIT_O RDER_TTL}с).")
                    try:
                        mexc_market_id = symbol.replace('/', '').replace(':USDT', '')
                        await exchange.fapiPrivateCancelOrder({'symbol': mexc_market_id, 'orderId': order_data['id']})
                    except: pass
                    if symbol in memory.limit_orders: del memory.limit_orders[symbol]

        except Exception as main_err:
            await asyncio.sleep(1)
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    try: asyncio.run(main_logic())
    except KeyboardInterrupt: log("🛑 Снайпер Берсерк принудительно остановлен.")
