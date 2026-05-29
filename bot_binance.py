
# --- УПРАВЛЕНИЕ КАПИТАЛОМ ---
MAX_ACTIVE_SLOTS = 1       # Динамика: 1 (при <$150), 2 (при <$500), 3 (при >$500)
RISK_GEAR = 0.95           # Общий множитель объема (0.1 - 1.0)
RESERVE_CASH = 0.5         # Буфер на комиссии (USDT)

# --- ГЛОБАЛЬНЫЕ ФИЛЬТРЫ (Безопасность) ---
GLOBAL_MAX_BANDWIDTH = 2   # Если рынок разорвало в клочья - стоп входы
FUNDING_SHIELD = 0.0003    # Пропуск при ставке > 0.03%
SAFE_LEVERAGE_LIMIT = 20    # Жесткий лимит до июня 2026
# ==========================================


class GlobalMemory:
    def __init__(self):
        self.mode = "STABLE"
        self.pending_mode = "STABLE"
        self.change_timer = 0
        self.last_mode_change = 0  # Время последнего переключения
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
        # --- ИСПРАВЛЕННЫЕ СТРОКИ (ЧЕРЕЗ SELF) ---
        self.stop_placed = {}
        self.max_pnl = {}
        self.tp_fixed = {}
        self.trail_active = {}

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

async def update_market_regime(exchange):
    """Фоновый замер тренда Биткоина, инерции макро-рынка и наполнение истории для BTC Trend Shield [V27.1]"""
    log("💉 Прогрев истории BTC: Загрузка свечей...")
    if not hasattr(memory, 'btc_history'):
        memory.btc_history = []

    while memory.is_running:
        try:
            # ТВОЙ ИСХОДНЫЙ ФЬЮЧЕРСНЫЙ КЛЮЧ: Загружаем 1м свечи для фильтра скорости входа
            btc_ohlcv_1m = await exchange.fetch_ohlcv('BTC/USDT:USDT', '1m', limit=5)
            if btc_ohlcv_1m:
                memory.btc_history.append(float(btc_ohlcv_1m[-1][4])) # Записываем close живой минутки
                memory.btc_history = memory.btc_history[-30:]

            # --- ТВОЯ ПОЛНАЯ ИСХОДНАЯ ЛОГИКА МАКРО-ИНЕРЦИИ И ФАЗ ---
            ohlcv = await exchange.fetch_ohlcv('BTC/USDT:USDT', '4h', limit=60)
            df = pd.DataFrame(ohlcv, columns=['t', 'o', 'h', 'l', 'c', 'v'])

            base_p = df['c'].iloc[-2]
            cur_p = float(memory.prices.get('BTC/USDT:USDT', df['c'].iloc[-1]))

            trend = (cur_p / base_p - 1) * 100
            memory.btc_trend = trend

            # Полное сохранение твоих порогов инерции
            if trend >= 0.75:
                memory.market_mode = 'bull'
                memory.dna_fleet = memory.all_dna['bull'] # Жесткий перенос матрицы
            elif trend <= -0.75:
                memory.market_mode = 'bear'
                memory.dna_fleet = memory.all_dna['bear'] # Жесткий перенос матрицы
            else:
                memory.market_mode = 'stable'
                memory.dna_fleet = memory.all_dna['stable'] # Жесткий перенос матрицы

            #log(f"🏛️ МАКРО-ФАЗА: >>> {memory.market_mode.upper()} <<< | Trend BTC: {round(trend, 3 )}% | Price: {cur_p}")

        except Exception as e:
            log(f"⚠ Ошибка макро-режима BTC: {e}")
        await asyncio.sleep(60)
#===========
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
    """V35.0: Ультра-высокочастотный сбор тиков и стакана"""
    client = await init_exchange()
    log("📡 Запуск WebSocket-потока цен [V35.0 Instant Market]...")
    while memory.is_running:
        try:
            tickers = await client.watch_tickers()
            if not tickers: continue

            for symbol, price_data in tickers.items():

                if 'USDT' in symbol:
                    # Достаем сырые данные из пакета тикера биржи
                    raw_last = price_data.get('last')
                    raw_bid  = price_data.get('bid')
                    raw_ask  = price_data.get('ask')

                    # Если биржа прислала None вместо живой цены — жестко скипаем этот тик
                    if raw_last is None:
                        continue

                    val = float(raw_last)
                    memory.prices[symbol] = val

                    # Безопасно сохраняем стакан: если bid/ask пусты — страхуемся ценой val
                    memory.prices[f"{symbol}_bid"] = float(raw_bid) if raw_bid is not None else val
                    memory.prices[f"{symbol}_ask"] = float(raw_ask) if raw_ask is not None else val
        except Exception as e:
            log(f"⚠️ Ошибка WS-Stream: {e}"); await asyncio.sleep(1)
    await client.close()

async def update_balance(exchange):
    """Фоновое обновление кошелька (раз в 20 секунд) [V24.3]"""
    while memory.is_running:
        try:
            bal = await exchange.fetch_balance()

            # Безопасное извлечение данных из CCXT структуры Binance Futures
            total = float(bal.get('total', {}).get('USDT', 0))
            free = float(bal.get('free', {}).get('USDT', 0))

            # Резервируем часть капитала для безопасности системы
            memory.available_margin = max(0, free - RESERVE_CASH)
            memory.total_wallet = total

            # Логируем МАЯК баланса строго раз в 5 минут, чтобы не спамить
            if not hasattr(memory, 'last_bal_log') or time.time() - memory.last_bal_log > 300:
                memory.last_bal_log = time.time()

        except Exception as e:
            log(f"⚠️ Ошибка Balance-Worker: {e}")
            await asyncio.sleep(5) # Защитная пауза при сбое сети

        await asyncio.sleep(20) # Оптимальная частота опроса кошелька для HFT

async def position_tracker(exchange):
    """Синхронизация позиций с защитой БУ-стопов и жестким клинингом пыли V25.6 [BINANCE Futures]"""
    while memory.is_running:
        try:
            pos_data = await exchange.fetch_positions()

            active = {}
            for p in pos_data:
                vol = abs(float(p.get('contracts', 0)))
                if vol > 0.00001:
                    raw_sym = p['symbol']
                    clean_sym = raw_sym.replace(':USDT', '')
                    if '/' not in clean_sym and 'USDT' in clean_sym:
                        clean_sym = clean_sym.replace('USDT', '/USDT')

                    # --- [ПРОТОКОЛ: АВТО-УТИЛИЗАЦИЯ ПЫЛИ V25.6] ---
                    notional_val = abs(float(p.get('notional', 0)))
                    if notional_val < 0.25: # Увеличили порог пыли до $0.25
                        try:
                            binance_market_id = clean_sym.replace('/', '')
                            # Полностью выжигаем все ордера по этой пыли (включая Algo)
                            await exchange.fapiPrivateDeleteAllOpenOrders({'symbol': binance_market_id})
                            await exchange.fapiPrivateDeleteAlgoOpenOrders({'symbol': binance_market_id})

                            # Пробуем закрыть остаток позиции по рынку
                            exit_side = 'SELL' if p['side'].lower() in ['long', 'buy'] else 'BUY'
                            await exchange.create_market_order(clean_sym, exit_side, vol, {'reduceOnly': True})
                            log(f"🧹 ВЕНИК: Позиция-пыль {clean_sym} успешно выжжена из терминала.")
                        except Exception:
                            pass
                        continue # Намертво стираем из памяти бота, чтобы не занимала слот

#                    if clean_sym in memory.all_dna['stable']:
#                        active[clean_sym] = p

                    # --- ЖЕСТКИЙ ФИКС СИНХРОНИЗАЦИИ КЛЮЧЕЙ V27.6 ---
                    # Проверяем оба формата ключа в ДНК-матрице
                    is_in_dna = (clean_sym in memory.all_dna['stable']) or (f"{clean_sym}:USDT" in memory.all_dna['stable'])

                    if is_in_dna:
                        # Записываем в active исходный raw_sym (с :USDT), чтобы monitor_logic читал верные флаги!
                        active[raw_sym] = p

            # ПРОТОКОЛ ВОССТАНОВЛЕНИЯ RECOVERED
            for symbol, p in active.items():
                if symbol not in memory.tp_fixed:
                    log(f"🔗 RECOVERED BINANCE: {symbol} ({abs(float(p['contracts']))} units) успешно усыновлена!")
                    memory.tp_fixed[symbol] = {'tp1': False, 'tp2': False}
                    memory.trail_active[symbol] = False
                    memory.stop_placed[symbol] = None
                    memory.max_pnl[symbol] = 0.0
                    memory.entry_times[symbol] = time.time()

            # АВТОМАТИЧЕСКАЯ ОЧИСТКА СЛОВАРЕЙ ПРИ ЗАКРЫТИИ СДЕЛКИ
            for sym in list(memory.active_pos.keys()):
                if sym not in active:
                    log(f"🧹 Позиция {sym} закрыта на бирже. Очистка системных флагов.")
                    clean_memory_keys(sym)

            memory.active_pos = active
            memory.slots_occupied = len(active)

            # --- [БРОНИРОВАННЫЙ ТОТАЛЬНЫЙ ВЕНИК ОРДЕРОВ-СИРОТ V25.6] ---
            for sym_key in list(memory.dna_fleet.keys()):
                binance_market_id = sym_key.replace('/', '').replace(':USDT', '')

                # СЦЕНАРИЙ 1: Если позиции НЕТ в рынке (SOL, LINK) — тотальный снос ордеров
                if sym_key not in memory.active_pos:
                    try:
                        await exchange.fapiPrivateDeleteAllOpenOrders({'symbol': binance_market_id})
                        await exchange.fapiPrivateDeleteAlgoOpenOrders({'symbol': binance_market_id})
                    except Exception:
                        pass

            await asyncio.sleep(10)
        except Exception as e:
            log(f"⚠ Ошибка Position-Tracker: {e}")
            await asyncio.sleep(15)

async def check_signal(exchange, symbol):
    """V35.0 Instant Market: Квантовый перехват оффсетов по живой цене тика"""
    try:
        dna = memory.dna_fleet.get(symbol)
        if not dna: return None

        # --- [ВРЕЗКА V29.0: ПРОВЕРКА КУЛДАУНА ЭВАКУАЦИИ (3 ЧАСА)] ---
        if hasattr(memory, 'cooldown_fleet'):
            last_evac_time = memory.cooldown_fleet.get(symbol)
            if last_evac_time:
                time_passed = time.time() - last_evac_time
                if time_passed < 10800:
                    return None
                else:
                    del memory.cooldown_fleet[symbol]

        # Мгновенно извлекаем живую секундную цену из памяти WebSocket
        cur_p = memory.prices.get(symbol, 0.0)
        if cur_p <= 0:
            return None

        # --- [ВРЕЗКА V31.0: ФИЛЬТР СПРЕДА БИТКОИНА (BTC SPREAD SHIELD)] ---
        if hasattr(memory, 'btc_history') and len(memory.btc_history) >= 15:
            btc_window = memory.btc_history[-15:]
            btc_spread = (max(btc_window) / min(btc_window) - 1) * 100
            if btc_spread < 0.06:
                return None

        # --- [ВРЕЗКА V31.5: ФИЛЬТР ПЛОТНОСТИ ТРЕНДА БИТКОИНА (BTC MOMENTUM POWER SHIELD)] ---
        if hasattr(memory, 'btc_history') and len(memory.btc_history) >= 3:
            btc_momentum_window = memory.btc_history[-3:]
            m1_diff = abs(btc_momentum_window[-1] - btc_momentum_window[-2])
            m2_diff = abs(btc_momentum_window[-2] - btc_momentum_window[-3])
            avg_min_move_pct = ((m1_diff + m2_diff) / 2) / btc_momentum_window[-1] * 100
            if avg_min_move_pct < 0.025:
                return None

        # --- [ВРЕЗКА V34.0: ФИЛЬТР ПЛОТНОСТИ СТАКАHА АЛЬТА (ASK-BID SPREAD SHIELD)] ---
        bid_key = f"{symbol}_bid"
        ask_key = f"{symbol}_ask"
        if bid_key in memory.prices and ask_key in memory.prices:
            best_bid = memory.prices[bid_key]
            best_ask = memory.prices[ask_key]
            if best_bid > 0:
                ticker_spread = (best_ask / best_bid - 1) * 100
                if ticker_spread > 0.05:
                    return None

        #1. Данные рынка (limit=30 для точности MA20)
        ohlcv = await exchange.fetch_ohlcv(symbol, '1m', limit=30)

#============
        df = pd.DataFrame(ohlcv, columns=['t', 'o', 'h', 'l', 'c', 'v'])
        cur_p = memory.prices.get(symbol, df['c'].iloc[-1])

        # 2. Боллинджер и Ширина
        ma_period = dna.get('m_per', 20)
        ma_mult = dna.get('m_mult', 2.1)
        #ma = df['c'].rolling(ma_period).mean().iloc[-1]
        #std = df['c'].rolling(ma_period).std().iloc[-1]
        ma = df['c'].rolling(ma_period).mean().shift(1).iloc[-1]
        std = df['c'].rolling(ma_period).std().shift(1).iloc[-1]
        upper = ma + (std * ma_mult)
        lower = ma - (std * ma_mult)
        width = (upper - lower) / ma * 100

        # 3. Фильтры безопасности (Анти-Шторм + Anti-Wick)
        if not (dna.get('min_w', 0.8) <= width <= dna.get('width', 2.0)): return None
        candle_size = (df['h'].iloc[-1] / df['l'].iloc[-1] - 1)
        if candle_size > 0.008: return None
#====
        # --- [ЖЕСТКИЙ ФИКС V31.3: ИСТИННОЕ СКОЛЬЗЯЩЕЕ 4-ЧАСОВОЕ ОКНО ХОДА ЦЕНЫ] ---
        try:
            # Запрашиваем 240 минутных свечей, чтобы получить честные скользящие 4 часа без слепых зон
            ohlcv_4h = await exchange.fetch_ohlcv(symbol, '1m', limit=240)
            if len(ohlcv_4h) >= 30:
                # Вытаскиваем все максимумы и минимумы за этот 4-часовой период
                highs_4h = [float(candle[2]) for candle in ohlcv_4h]
                lows_4h = [float(candle[3]) for candle in ohlcv_4h]

                max_4h = max(highs_4h)
                min_4h = min(lows_4h)

                # Истинный скользящий ход цены за 4 часа
                rolling_range_4h = (max_4h / min_4h - 1) * 100

                # Если ход монеты за последние 4 часа > 4.5% — ЖЕСТКАЯ БЛОКИРОВКА (Монета в мясорубке)
                if rolling_range_4h > 4.5:
                    # log(f"🛡️ 4H Range Shield V31.3: Сигнал {symbol} заблокирован. Скользящий ход:  {round(rolling_range_4h, 2)}% > 4.5%")
                    return None
        except Exception as e:
            pass
#====
        # 4. Параметры предыдущей свечи (Engulfing)
        prev_open = df['o'].iloc[-1]
        prev_close = df['c'].iloc[-1]

        # --- БЛОК V20.0: ФАКТОР ФИТИЛЯ ---
        candle_range = df['h'].iloc[-1] - df['l'].iloc[-1]
        if candle_range == 0: return None # Защита от нулевых свечей

        # Для ЛОНГА: нижняя тень (от минимума до тела)
        lower_wick = min(df['o'].iloc[-1], df['c'].iloc[-1]) - df['l'].iloc[-1]
        wick_ratio_long = lower_wick / candle_range

        # Для ШОРТА: верхняя тень (от максимума до тела)
        upper_wick = df['h'].iloc[-1] - max(df['o'].iloc[-1], df['c'].iloc[-1])
        wick_ratio_short = upper_wick / candle_range

        # РАСЧЕТ ТРИГГЕРОВ ИЗ ДНК МАТРИЦЫ
        long_trigger = lower * (1 - dna['l_off'])
        short_trigger = upper * (1 + dna['s_off'])

        # 5. Первичная логика входа (Оффсет + Поглощение + Фитиль)
        #is_buy = (cur_p >= long_trigger) and (cur_p > prev_open) and (wick_ratio_long > 0.35)
        #is_sell = (cur_p <= short_trigger) and (cur_p < prev_open) and (wick_ratio_short > 0.35)
        # --- [ЖЕСТКИЙ ПЕРЕВОД V35.0 НА МГНОВЕННЫЙ ПЕРЕХВАТ ТИКА] ---
        # Сравниваем живую секундную цену cur_p с оффсетами, не дожидаясь закрытия минуты!

#=== С Логом
        # --- [УЗЕЛ V35.1: ИHТЕЛЛЕКТУАЛЬНЫЙ ДЕБАГ ФИЛЬТРOВ ВХОДА БИНАНСА] ---
        # Базовый триггер: живая цена тика пересекла ДНК-оффсет
        hit_long_offset = (cur_p <= long_trigger) and (wick_ratio_long > 0.35)
        hit_short_offset = (cur_p >= short_trigger) and (wick_ratio_short > 0.35)

        if hit_long_offset or hit_short_offset:
            # 1. Проверяем BTC Spread Shield
            if hasattr(memory, 'btc_history') and len(memory.btc_history) >= 15:
                btc_window = memory.btc_history[-15:]
                btc_spread = (max(btc_window) / min(btc_window) - 1) * 100
                if btc_spread < 0.06:
                    log(f"🔍 [ОТКАЗ {symbol}]: Цена пробила оффсет, но BTC Spread Shield заблокировал вход (Спред BTC: {round(btc_spread, 3)}% < 0.06%)")
                    return None

            # 2. Проверяем BTC Momentum Shield
            if hasattr(memory, 'btc_history') and len(memory.btc_history) >= 3:
                btc_momentum_window = memory.btc_history[-3:]
                m1_diff = abs(btc_momentum_window[-1] - btc_momentum_window[-2])
                m2_diff = abs(btc_momentum_window[-2] - btc_momentum_window[-3])
                avg_min_move_pct = ((m1_diff + m2_diff) / 2) / btc_momentum_window[-1] * 100
                if avg_min_move_pct < 0.025:
                    log(f"🔍 [ОТКАЗ {symbol}]: Пробой оффсета, но BTC Momentum Shield заблокировал вход (Скорость BTC: {round(avg_min_move_pct, 4)}% < 0.025%)")
                    return None

            # 3. Проверяем Ask-Bid Spread Shield альта
            if bid_key in memory.prices and ask_key in memory.prices:
                if best_bid > 0:
                    ticker_spread = (best_ask / best_bid - 1) * 100
                    if ticker_spread > 0.05:
                        log(f"🔍 [ОТКАЗ {symbol}]: Пробой оффсета, но стакан пустой! Ask-Bid Shield спас от проскальзывания (Спред альта: {round(ticker_spread, 3)}% > 0.05%)")
                        return None

            # 4. Проверяем 4H Rolling Range Shield
            if len(ohlcv_4h) >= 30:
                if rolling_range_4h > 4.5:
                    log(f"🔍 [ОТКАЗ {symbol}]: Пробой оффсета, но монета забанена 4H Range Shield (Ход за 4 часа: {round(rolling_range_4h, 2)}% > 4.5%)")
                    return None

            # 5. Проверяем Каскадный нож предыстории (Pre-Candle Shield)
            #if len(df) >= 5:
            #    p_c1 = df.iloc[-2]; p_c2 = df.iloc[-3]; p_c3 = df.iloc[-4]
            #    is_3_green = (p_c1['c'] > p_c1['o']) and (p_c2['c'] > p_c2['o']) and (p_c3['c'] > p_c3['o'])
            #    is_3_red = (p_c1['c'] < p_c1['o']) and (p_c2['c'] < p_c2['o']) and (p_c3['c'] < p_c3['o'])

                    # --- ИСПРАВЛЕНИЕ V23.9: 4-МИНУТНЫЙ КАСКАД ДЛЯ СВОБОДЫ ВХОДОВ ---
            if len(df) >= 6:
                p_c1 = df.iloc[-2]; p_c2 = df.iloc[-3]; p_c3 = df.iloc[-4]; p_c4 = df.iloc[-5]
                is_3_green = (p_c1['c'] > p_c1['o']) and (p_c2['c'] > p_c2['o']) and (p_c3['c'] > p_c3['o']) and (p_c4['c'] > p_c4['o'])
                is_3_red = (p_c1['c'] < p_c1['o']) and (p_c2['c'] < p_c2['o']) and (p_c3['c'] < p_c3['o']) and (p_c4['c'] < p_c4['o'])

                if hit_long_offset and is_3_red:
                    log(f"🔍 [ОТКАЗ {symbol}]: Пробой оффсета, но Каскадный Нож запретил ловить летящий топор (3 красных свечи подряд)")
                    return None
                if hit_short_offset and is_3_green:
                    log(f"🔍 [ОТКАЗ {symbol}]: Пробой оффсета, но Каскадный Нож запретил шортить вертикальную ракету (3 зеленых свечи подряд)")
                    return None

            # Если все фильтры-судьи дали добро — взводим истинные триггеры входа
            is_buy = hit_long_offset
            is_sell = hit_short_offset
        else:
            is_buy = False
            is_sell = False

        if not (is_buy or is_sell):
            return None
#====

        # --- [ВРЕЗКА V29.0: ФИЛЬТР ПРЕДЫСТОРИИ КАСКАДНЫЙ НОЖ (PRE-CANDLE SHIELD)] ---
        if len(df) >= 6:
            p_c1 = df.iloc[-2]; p_c2 = df.iloc[-3]; p_c3 = df.iloc[-4]; p_c4 = df.iloc[-5]
            is_3_green = (p_c1['c'] > p_c1['o']) and (p_c2['c'] > p_c2['o']) and (p_c3['c'] > p_c3['o']) and (p_c4['c'] > p_c4['o'])
            is_3_red = (p_c1['c'] < p_c1['o']) and (p_c2['c'] < p_c2['o']) and (p_c3['c'] < p_c3['o']) and (p_c4['c'] < p_c4['o'])


            if is_buy and is_3_red:
                # Если ловим лонг, но цена валится каскадом 3 минуты вниз без остановки — ОТМЕНА
                # log(f"🛡️ Pre-Candle Shield: Заблокирован вход в ЛОНГ по {symbol}. Обнаружен падаю щий каскад.")
                return None

            if is_sell and is_3_green:
                # Если ловим шорт, но цена летит ракетой 3 минуты вверх без откатов — ОТМЕНА
                # log(f"🛡️ Pre-Candle Shield: Заблокирован вход в ШОРТ по {symbol}. Обнаружен расту щий каскад.")
                return None

#=====
        # --- [ВРЕЗКА V31.0: АДАПТИВНЫЙ ФИЛЬТР ОБЪЕМА (VOLUME SPIKE SHIELD)] ---
        # --- [ВРЕЗКА V27.0: ПОПУТНЫЙ HFT VOLUME SPIKE SHIELD] ---
        try:
            if len(df) >= 7:
                live_volume = float(df['v'].iloc[-1])  # Живой тиковый объем
                mean_volume = float(df['v'].iloc[-6:-1].mean())  # Средний объем за 5м

                # На Бинансе бьем маркетом вдогонку, поэтому заходим СТРОГО на взрывном попутном объеме!
                if live_volume <= mean_volume * 1.05:
                    return None

            # --- [КАСКАДНЫЙ НОЖ V27.0 — ОПТИМИЗАЦИЯ НА 2 СВЕЧИ] ---
            # Уходим от слепоты 4 свечей. Запрещаем вход, только если тренд идет 2 минуты стеной против нас
            if len(df) >= 3:
                c_0 = float(df['c'].iloc[-1])
                c_1 = float(df['c'].iloc[-2])
                c_2 = float(df['c'].iloc[-3])

                if is_buy_candidate and (c_0 < c_1 and c_1 < c_2):
                    return None  # Ловить летящий топор нельзя
                if is_sell_candidate and (c_0 > c_1 and c_1 > c_2):
                    return None  # Встречать грудью вертикальную ракету нельзя
        except Exception as input_filter_err:
            pass
#=====
        # --- [КВАНТОВЫЙ ФИЛЬТР: BTC TREND SHIELD] ---
        # ТВОЙ СИНТАКСИС: Проверяем минутное изменение Биткоина со строгим ключом :USDT
        if hasattr(memory, 'btc_history') and len(memory.btc_history) >= 2:
            btc_now = memory.btc_history[-1]
            btc_prev = memory.btc_history[-2]
            btc_change = btc_now / btc_prev - 1

            if is_buy and btc_change < -0.0004: # Блокируем лонг альта при проливе BTC
                return None
            if is_sell and btc_change > 0.0004: # Блокируем шорт альта при пампе BTC
                return None


        # 6. Funding Shield (Если прошли геометрию)
        try:
            f_data = await exchange.fetch_funding_rate(symbol)
            if abs(float(f_data.get('fundingRate', 0))) > FUNDING_SHIELD:
                log(f"🛡 Funding Shield: {symbol} пропуск (Rate: {f_data.get('fundingRate')})")
                return None
        except:
            pass

        return {
            'symbol': symbol,
            'side': 'buy' if is_buy else 'sell',
            'price': cur_p,
            'dna': dna
        }

    except Exception as e:
        pass
    return None
#============
async def signal_hunter(exchange):
    """Главный цикл поиска входов (Multi-Slot Ready)"""
    log("🏹 Охотник за сигналами активирован.")
    symbols = list(memory.dna_fleet.keys())

    while memory.is_running:

#        if int(time.time()) % 300 == 0:
            # ИСПРАВЛЕНО: берем market_mode из живой коробки передач
            #log(f"🏹 Охотник на чеку. Сканирую {len(memory.dna_fleet)} секторов в режиме {memory.market_mode.upper()}...")
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
        await asyncio.sleep(0.3) # Пауза после полного круга

async def execute_entry(exchange, signal):
    """Асинхронная установка плеча и вход в позицию"""
    symbol = signal['symbol']
    side = signal['side']
    price = signal['price']
    dna = signal['dna']
    # --- ШТУЧНЫЙ ФИКС V24.8: СНОС СУФФИКСА ДЛЯ ВОЗВРАТА ПРИБЫЛИ К $18 940 ---
    symbol = symbol.split(':')[0]

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
        # РЕМОНТ V16.0: Используем глобальный баланс из памяти объекта memory
        avail_bal = float(memory.available) if hasattr(memory, 'available') else 0.0

        # Если баланс в памяти пуст, ставим аварийный лимит от маржи слота
        if avail_bal <= 0:
            avail_bal = margin_for_slot * 1.05

        usdt_volume = margin_for_slot * dna['lev']
        if usdt_volume > avail_bal * dna['lev']:
            usdt_volume = avail_bal * dna['lev'] * 0.98

        amount_base = usdt_volume / price

        # Получаем чистую строковую прецизию без обертки во float
        amount = exchange.amount_to_precision(symbol, amount_base)


        if float(amount) <= 0:
            return
    #    if amount <= 0: return

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
#=============
async def monitor_logic(exchange, symbol, pos):
    try:
        # 1. ЧИСТОЕ ЧТЕНИЕ ЦЕНЫ ИЗ WEBSOCKET (Без лагов и мусора)
        # БРОНИРОВАННОЕ ЧТЕНИЕ ЦЕНЫ: Ищем оба формата ключа в WebSocket-потоке
        # --- ШТУЧНАЯ ВРЕЗКА V24.6: ИНИЦИАЛИЗАЦИЯ ПАРАМЕТРОВ ПОЗИЦИИ ---
        vol = abs(float(pos.get('contracts', pos.get('initialMargin', 0))))
        side = pos.get('side', 'long').lower()
        exit_side = 'SELL' if side in ['long', 'buy'] else 'BUY'
        cur_p = memory.prices.get(symbol)
        if not cur_p:
            alt_symbol = symbol.replace('/', '') # Пробуем формат DOGEUSDT
            cur_p = memory.prices.get(alt_symbol)

        if not cur_p:
            # Если в WebSocket пусто — берем живую цену прямо из инфо-пакета позиции на бирже
            cur_p = float(pos.get('markPrice')) if pos.get('markPrice') else float(pos.get('info', {}).get('markPrice', 0))

        if not cur_p or cur_p <= 0: return # Полная защита от деления на ноль

        # 2. РАСЧЕТ PNL С ЗАЩИТОЙ ОТ ИНВЕРСИИ
        entry_p = float(pos['entryPrice'])
        side = pos['side'].lower()
        profit = (cur_p / entry_p) - 1 if side in ['long', 'buy'] else (entry_p / cur_p) - 1
        vol = abs(float(pos['contracts']))

        # ЖЕСТКИЙ ФИКС NAMEERROR: Объявляем переменную age для модулей раннего выхода!
        if symbol in memory.entry_times:
            age = time.time() - memory.entry_times[symbol]
        else:
            memory.entry_times[symbol] = time.time()
            age = 1

        dna = memory.dna_fleet.get(symbol)
        if not dna:
            # Если позиция без суффикса, принудительно добавляем его для поиска в ДНК
            if ":USDT" not in symbol:
                dna = memory.dna_fleet.get(f"{symbol}:USDT")
        if not dna: return

        # Локальная инициализация
        if symbol not in memory.trail_active: memory.trail_active[symbol] = False
        if symbol not in memory.tp_fixed: memory.tp_fixed[symbol] = {'tp1': False, 'tp2': False}

        current_mode = 'stable'
        for m, matrix in memory.all_dna.items():
            if matrix == memory.dna_fleet: current_mode = m; break

        exit_side = 'SELL' if side in ['long', 'buy'] else 'BUY'
        bal_str = f"| Bal: ${round(memory.total_wallet, 2)}"

        # --- [ЖЕСТКИЙ ФИКС КВАНТОВОГО МОДУЛЯ РАННЕГО ВЫХОДА V27.7] ---
        if profit < 0:
            # ТРИГГЕР 1: Эвакуация по импульсу Биткоина (Строго от 4 элементов в истории!)
            # --- [ВРЕЗКА V24.5: НАПРАВЛЕННАЯ ЭВАКУАЦИЯ BTC НА ПОРОГЕ 0.055%] ---
            # Анализируем 3-минутный вектор Биткоина (срез по 4 точкам истории)
            if hasattr(memory, 'btc_history') and len(memory.btc_history) >= 4:
                btc_now = memory.btc_history[-1]
                btc_then = memory.btc_history[-4]

                if btc_then > 1000 and btc_now > 1000:
                    btc_move_pct = (btc_now / btc_then) - 1

                    # Проверяем, превысил ли Биткоин критическую скорость шторма в 0.055%
                    if abs(btc_move_pct) >= 0.00165:
                        is_pos_long = side.lower() in ['long', 'buy']

                        # ИСТИННЫЙ ВЕКТОРНЫЙ ФИЛЬТР: Эвакуация взводится СТРОГО против нашей маржи
                        is_long_under_attack = is_pos_long and btc_move_pct <= -0.00165    # Лонг, а BTC падает
                        is_short_under_attack = not is_pos_long and btc_move_pct >= 0.00165 # Шорт, а BTC растет

                        if is_long_under_attack or is_short_under_attack:
                            log(f"🚨 [ЭВАКУАЦИЯ BTC V24.5]: Поводырь летит против позиции {symbol} (Скорость BTC: {round(btc_move_pct, 3)}%). Спасаю маржу! Лосс: {round(profit*100, 2)}%")
                            action_triggered_btc = False
                            try:
                                clean_market_id = symbol.replace('/', '').replace(':USDT', '')
                                await exchange.fapiPrivateDeleteAllOpenOrders({'symbol': clean_market_id})
                                await exchange.fapiPrivateDeleteAlgoOpenOrders({'symbol': clean_market_id})
                                await exchange.create_order(symbol, 'market', 'SELL' if is_pos_long else 'BUY', vol, None, {'reduceOnly': True})
                                action_triggered_btc = True
                            except Exception as e:
                                log(f"⚠ Критическая ошибка эвакуации BTC для {symbol}: {e}")

                            # Тотальная принудительная зачистка флагов во всех форматах ключей
                            for k in [symbol, f"{symbol}:USDT", symbol.replace(':USDT', '')]:
                                if k in memory.active_pos: del memory.active_pos[k]
                                if k in memory.tp_fixed: del memory.tp_fixed[k]
                                if k in memory.stop_placed: del memory.stop_placed[k]
                                if k in memory.trail_active: del memory.trail_active[k]
                                if k in memory.max_pnl: del memory.max_pnl[k]

                            if action_triggered_btc:
                                return

#==========
            # ТРИГГЕР 2: Эвакуация по затяжному флэтовому болоту альта (Time-Decay)
            # --- [ВРЕЗКА V24.5: ДИНАМИЧЕСКИЙ ДНК-ТАЙМЕР ЖИЗНИ ЛОТА БИНАНСА] ---
            # Динамически вычисляем индивидуальный лимит удержания (TTL) на базе класса монеты
            is_meme_coin = any(m_n in symbol.upper() for m_n in ['PEPE', 'SHIB', 'WIF', 'POPCAT', 'DOGE', 'MEME'])
            is_anchor_coin = any(a_n in symbol.upper() for a_n in ['DOT', 'POL', 'BNB', 'XRP', 'ADA'])

            if is_meme_coin:
                optimal_decay_ttl = 120    # Мемы: 2 минуты на взрывной микро-импульс
            elif is_anchor_coin:
                optimal_decay_ttl = 420    # Якоря: 7 минут на вязкое раскачивание флэта
            else:
                optimal_decay_ttl = 240    # Тех-Ракеты (NEAR, SOL, FET): 4 минуты оптимального разбега

            # Эвакуируем сделку по таймеру только если время вышло и лосс застрял ниже -0.08%
            #if age > optimal_decay_ttl and profit < -0.0008:
            # --- ШТУЧНЫЙ ФИКС V27.0: БЛОКИРОВКА ТАЙМЕРА ПРИ АКТИВНОМ ПРЕ-ТРЕЙЛИНГЕ ---
            # Если по монете пошел скользящий трейлинг прибыли, таймер утилизации блокируется, давая забрать Тейки!
            if age > optimal_decay_ttl and profit < -0.0008 and not memory.trail_active.get(symbol, False):
                log(f"⏱️ [ДНК-ТАЙМЕР УТИЛИЗАЦИЯ]: {symbol} утилизирован по лимиту класса ({int(age)}с >= {optimal_decay_ttl}с) | Лосс: {round(profit*100, 2)}%")
                action_triggered_decay = False
                try:
                    clean_market_id = symbol.replace('/', '').replace(':USDT', '')
                    await exchange.fapiPrivateDeleteAllOpenOrders({'symbol': clean_market_id})
                    await exchange.fapiPrivateDeleteAlgoOpenOrders({'symbol': clean_market_id})
                    await exchange.create_market_order(symbol, 'SELL' if side in ['long', 'buy'] else 'BUY', vol, {'reduceOnly': True})
                    action_triggered_decay = True
                except Exception as e:
                    log(f"⚠ Критическая ошибка утилизации по таймеру {symbol}: {e}")

                # Тотальная зачистка флагов во всех форматах для разблокировки слота
                for k in [symbol, f"{symbol}:USDT", symbol.replace(':USDT', '')]:
                    if k in memory.active_pos: del memory.active_pos[k]
                    if k in memory.tp_fixed: del memory.tp_fixed[k]
                    if k in memory.stop_placed: del memory.stop_placed[k]
                    if k in memory.trail_active: del memory.trail_active[k]
                    if k in memory.max_pnl: del memory.max_pnl[k]
                if action_triggered_decay:
                    return

#===
            # ТРИГГЕР Б: Синдром Сползания Импульса (Выдох крупного игрока — без изменений)
            if symbol in memory.max_pnl and memory.max_pnl[symbol] >= 0.0025:
                current_decay_pct = (1 - (profit / memory.max_pnl[symbol])) * 100
                if current_decay_pct > 70.0:
                    log(f"🏁 СИНДРОМ СПОЛЗАНИЯ ИМПУЛЬСА: {symbol} закрыт. ММ выдохся (Пик: +{round(memory.max_pnl[symbol]*100,2)}% | Сползло на: {round(current_decay_pct,1)}%)")
                    action_triggered_momentum_dead = False
                    try:
                        clean_market_id = symbol.replace('/', '').replace(':USDT', '')
                        await exchange.fapiPrivateDeleteAllOpenOrders({'symbol': clean_market_id})
                        await exchange.fapiPrivateDeleteAlgoOpenOrders({'symbol': clean_market_id})
                        await exchange.create_market_order(symbol, exit_side, vol, {'reduceOnly': True})
                        action_triggered_momentum_dead = True
                    except Exception as e: log(f"⚠️ Ошибка Синдрома Сползания: {e}")

                    if action_triggered_momentum_dead:
                        for k in [symbol, symbol.replace(':USDT', '')]:
                            if k in memory.active_pos: del memory.active_pos[k]
                            if k in memory.tp_fixed: del memory.tp_fixed[k]
                            if k in memory.stop_placed: del memory.stop_placed[k]
                            if k in memory.trail_active: del memory.trail_active[k]
                            if k in memory.max_pnl: del memory.max_pnl[k]
                        return
#===

            # --- [УЗЕЛ V30.0: АБСОЛЮТНЫЙ DEADTIME LOCK НА 25 МИНУТ] ---
            # Если сделка выжила, но висит в рынке 25 минут (1500с) — выжигаем её при ЛЮБОМ PNL, высвобождая маржу
            if age > 1500:
                log(f"⏱️ АБСОЛЮТНЫЙ DEADTIME LOCK: {symbol} принудительно закрыт по лимиту времени 25 мин (PNL: {round(profit*100, 2)}%)")
                action_triggered_deadtime = False
                try:
                    clean_market_id = symbol.replace('/', '').replace(':USDT', '')
                    await exchange.fapiPrivateDeleteAllOpenOrders({'symbol': clean_market_id})
                    await exchange.fapiPrivateDeleteAlgoOpenOrders({'symbol': clean_market_id})
                    await exchange.create_market_order(symbol, exit_side, vol, {'reduceOnly': True})
                    action_triggered_deadtime = True
                except Exception as e:
                    log(f"⚠️ Критическая ошибка Deadtime-закрытия {symbol}: {e}")

                # Отправляем монету на кулдаун 6 часов как вялую
                if not hasattr(memory, 'cooldown_fleet'):
                    memory.cooldown_fleet = {}
                memory.cooldown_fleet[symbol] = time.time() + 10800
                memory.cooldown_fleet[symbol.replace(':USDT', '')] = time.time() + 10800

                for k in [symbol, symbol.replace(':USDT', '')]:
                    if k in memory.active_pos: del memory.active_pos[k]
                    if k in memory.tp_fixed: del memory.tp_fixed[k]
                    if k in memory.stop_placed: del memory.stop_placed[k]
                    if k in memory.trail_active: del memory.trail_active[k]
                    if k in memory.max_pnl: del memory.max_pnl[k]

                if action_triggered_deadtime: return # Намертво обрываем тик
#==============
        # 3. ВЫСТАВЛЕНИЕ РЕАЛЬНОГО СТОПА НА БИРЖУ СРАЗУ ПРИ ВХОДЕ
        if not memory.stop_placed.get(symbol):
            try:
                sl_price = entry_p * (1 - abs(dna['sl'])) if side in ['long', 'buy'] else entry_p * (1 + abs(dna['sl']))
                sl_price = float(exchange.price_to_precision(symbol, sl_price))

                await exchange.cancel_all_orders(symbol, {'spot': False})
                await exchange.create_order(symbol, 'STOP_MARKET', exit_side, vol, params={'stopPrice': sl_price, 'reduceOnly': True})
                memory.stop_placed[symbol] = sl_price
                log(f"🛡️ СТОП ВЫСТАВЛЕН: {symbol} @ {sl_price} {bal_str}")
            except Exception as e: log(f"🆘 Ошибка стопа {symbol}: {e}")

        # 4. TP1 С ИСПРАВЛЕННЫМ СТРОКОВЫМ ОБЪЕМОМ И ПЕРЕВОДОМ В РЕАЛЬНЫЙ БУ
#==========
        # --- [УЗЕЛ V30.1: ПРЕ-ТРЕЙЛИНГ НА 75% ПУТИ ДО ТЕЙКА 1] ---

        # --- [ВРЕЗКА V27.0: МОНОЛИТ АДАПТИВНОГО ТРЕЙЛИНГА И ТЕЙКОВ БИНАНСА] ---
        pre_trail_trigger = dna['tp1'] * 0.75
        trail_key = f"{symbol}_trail"

        # А. АДАПТИВНЫЙ КОНТУР: Взводим трейлинг на 75% пути до цели
        if not memory.tp_status.get(symbol, {}).get('tp1', False) and profit >= pre_trail_trigger:
            if not memory.trail_active.get(symbol, False):
                memory.trail_active[symbol] = True
                memory.max_pnl[symbol] = profit
                log(f"🚀 [ПРЕ-ТРЕЙЛИНГ ВЗВЕДЕН]: {symbol} прошел 75% пути. Пик зафиксирован. Защита прибыли включена.")

        # Б. КАСКАДНЫЙ ТЕЙК-1: Фиксация 50% объема при долете импульса
        if not memory.tp_status.get(symbol, {}).get('tp1', False) and profit >= dna['tp1']:
            close_qty_raw = vol * 0.5
            if (close_qty_raw * cur_p) < 5.2:
                log(f"⚠️ ОБЪЕМ МАЛ ДЛЯ ДРОБЛЕНИЯ {symbol}: Снос 100% лота по рынку для защиты залога.")
                try:
                    clean_market_id = symbol.replace('/', '').replace(':USDT', '')
                    await exchange.fapiPrivateDeleteAllOpenOrders({'symbol': clean_market_id})
                    await exchange.create_market_order(symbol, exit_side, vol, {'reduceOnly': True})
                except: pass
                clean_memory_keys(symbol)
                if symbol in memory.active_pos: del memory.active_pos[symbol]
                return

           try:
                close_qty = exchange.amount_to_precision(symbol, close_qty_raw)
                await exchange.create_market_order(symbol, exit_side, close_qty, {'reduceOnly': True})

                clean_market_id = symbol.replace('/', '').replace(':USDT', '')
                await exchange.fapiPrivateDeleteAllOpenOrders({'symbol': clean_market_id})

                bu_price = float(exchange.price_to_precision(symbol, entry_p))
                rem_qty = exchange.amount_to_precision(symbol, vol - float(close_qty))
                pos['contracts'] = float(rem_qty)

                # Ставим безубыток (BU) на остаток позиции
                await exchange.create_order(symbol, 'STOP_MARKET', exit_side, rem_qty, params={'stopPrice': bu_price, 'reduceOnly': True})

                memory.tp_status[symbol]['tp1'] = True
                memory.trail_active[symbol] = True
                memory.max_pnl[symbol] = profit
                log(f"🎯 [ТЕЙК-1 BINANCE]: Фиксация 50% по {symbol} (+{round(profit*100, 2)}%). Остаток в безубытке! {bal_str}")
           except Exception as e:
                log(f"⚠ Ошибка исполнения Тейка-1 {symbol}: {e}")
           return

#============
        # 6. ВЕДЕНИЕ АДАПТИВНОГО ТРЕЙЛИНГА ПО ШАГАМ
        # 6. ВЕДЕНИЕ АДАПТИВНОГО ТРЕЙЛИНГА ПО ШАГАМ V27.0
        if memory.trail_active.get(symbol, False):
            is_meme_coin = any(m_n in symbol.upper() for m_n in ['PEPE', 'SHIB', 'WIF', 'POPCAT', 'DOGE', 'MEME'])
            trail_step = 0.0055 if is_meme_coin else 0.0035  # Адаптивный шаг отката

            if profit > memory.max_pnl.get(symbol, 0.0):
                memory.max_pnl[symbol] = profit

            if profit <= (memory.max_pnl[symbol] - trail_step):
                peak_profit = memory.max_pnl[symbol]
                log(f"🏁 [ГИБРИДНЫЙ ТРЕЙЛИНГ КАТАПУЛЬТА V27.0]: Выход из {symbol} | Итог: +{round(profit*100, 2)}% (Пик был: +{round(peak_profit*100, 2)}%) {bal_str}")
                try:
                    clean_market_id = symbol.replace('/', '').replace(':USDT', '')
                    await exchange.fapiPrivateDeleteAllOpenOrders({'symbol': clean_market_id})
                    await exchange.create_market_order(symbol, exit_side, vol, {'reduceOnly': True})

                    # Тотальная зачистка флагов
                    clean_memory_keys(symbol)
                    if symbol in memory.active_pos: del memory.active_pos[symbol]
                    memory.slots_occupied = max(0, memory.slots_occupied - 1)
                except Exception as e:
                    log(f"⚠ Ошибка закрытия трейлинга {symbol}: {e}")
                return
#=========
    except Exception as e: pass

def clean_memory_keys(symbol):
    """Тотальная зачистка флагов монеты при выходе по всем форматам ключей"""
    # Доработка: удаление флагов в различных форматах ключа символа
    for k in [symbol, f"{symbol}:USDT", symbol.replace(':USDT', '')]:
        if k in memory.tp_fixed: del memory.tp_fixed[k]
        if k in memory.trail_active: del memory.trail_active[k]
        if k in memory.stop_placed: del memory.stop_placed[k]
        if k in memory.max_pnl: del memory.max_pnl[k]

async def monitoring_cycle(exchange):
    """Исправленный цикл: передает полный ключ (с :USDT) для точного поиска в памяти."""
    log("👁 Мониторинг позиций запущен.")
    while memory.is_running:
        if memory.active_pos:
            tasks = []
            for sym, data in memory.active_pos.items():
                # FIX: Используем оригинальный 'sym', а не очищенный
                tasks.append(monitor_logic(exchange, sym, data))
            if tasks: await asyncio.gather(*tasks)
        await asyncio.sleep(0.5)

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
            asyncio.create_task(update_market_regime(exchange)), # Активация коробки передач
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
