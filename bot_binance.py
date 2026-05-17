
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
    """Аналитик Биткоина с инерцией 90с и бесконечным циклом V19.5"""
    #log("🚥 Аналитик BTC запущен (Защита от дребезга 90с активна)")
    while memory.is_running:
        try:
            # 1. Получаем историю BTC для анализа фазы
            ohlcv = await exchange.fetch_ohlcv('BTC/USDT:USDT', '1m', limit=100)
            df = pd.DataFrame(ohlcv, columns=['t', 'o', 'h', 'l', 'c', 'v'])

            # Расчет изменения: Берем первую свечу [0] и последнюю [-1]
            price_start = df['c'].iloc[0]
            price_now = df['c'].iloc[-1]
            change = (price_now / price_start - 1) * 100

            # 2. Определяем ТЕОРЕТИЧЕСКИЙ режим (calculated_mode)
            if change > 0.8:
                calculated_mode = "BULL"
            elif change < -0.8:
                calculated_mode = "BEAR"
            else:
                calculated_mode = "STABLE"

            # 3. Логика Инерции (используем memory)
            if calculated_mode != memory.mode:
                # Если рынок тянет в новый режим, а мы еще не начали ждать
                if memory.pending_mode != calculated_mode:
                    memory.pending_mode = calculated_mode
                    memory.change_timer = time.time()
                    #log(f"🚥 ПОДГОТОВКА: BTC тянет в {calculated_mode}. Ждем подтверждения 90с...")

                # Если 90 секунд стабильно держится новый режим - переключаем
                time_passed = time.time() - memory.change_timer
                if time_passed >= 90:
                    memory.mode = calculated_mode
                    memory.change_timer = 0
                    memory.current_regime = calculated_mode.lower()

                    # Загружаем соответствующие ДНК файлы
                    load_all_dna()

                    log(f"🏛️ ⚙️ ФАЗА ПОДТВЕРЖДЕНА: >>> {memory.mode} <<< | Trend: {round(change, 3) }%")
            else:
                # Если рынок вернулся к нашему текущему режиму - сбрасываем ожидание
                if memory.pending_mode != memory.mode:
                    #log(f"✅ ВЕТЕР СТИХ: BTC вернулся в норму. Остаемся в {memory.mode}.")
                    memory.pending_mode = memory.mode
                    memory.change_timer = 0

            # Редкий лог статуса (раз в 5 минут)
#            if int(time.time()) % 300 < 20:
                #log(f"🚥 STATUS: BTC Change: {round(change, 3)}% | Current Mode: {memory.mode}")

            await asyncio.sleep(20) # Пауза между проверками 20 секунд

        except Exception as e:
            log(f"⚠️ Ошибка аналитика BTC: {e}")
            await asyncio.sleep(10)

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

                    if clean_sym in memory.all_dna['stable']:
                        active[clean_sym] = p

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

                # СЦЕНАРИЙ 2: Для ЖИВЫХ позиций (SUI, PEPE, DOGE) — ЖЕСТКАЯ ЗАЩИТА БЕЗУБЫТКА
                else:
                    try:
                        # Если по монете уже зафиксирован TP1, венику ЗАПРЕЩЕНО трогать ордера,
                        # чтобы случайно не сбить наш выставленный БУ-стоп!
                        if sym_key in memory.tp_fixed and not memory.tp_fixed[sym_key].get('tp1', False):
                            # Раз в 20 секунд убираем наводку дубликатов
                            if int(time.time()) % 20 == 0:
                                await exchange.fapiPrivateDeleteAlgoOpenOrders({'symbol': binance_market_id})
                                memory.stop_placed[sym_key] = None # Сбрасываем флаг, чтобы monitor_logic выставил ОДИН чистый стоп
                    except Exception:
                        pass
#                    pass
#                    try:
                        # Если Тейк 1 по монете ЕЩЕ НЕ ВЫПОЛНЕН — мы можем безопасно чистить дубликаты стопов.
                        # Но если TP1 выполнен (флаг равен True), венику ЗАПРЕЩЕНО трогать ордера,
                        # чтобы не сбить наш выставленный БУ-стоп!
#                        if sym_key in memory.tp_fixed and not memory.tp_fixed[sym_key]['tp1']:
#                            if int(time.time()) % 60 < 10: # Раз в минуту убираем наводку дублей стартового стопа
#                                await exchange.fapiPrivateDeleteAlgoOpenOrders({'symbol': binance_market_id})
#                                memory.stop_placed[sym_key] = None # Заставляем выставить один чистый стоп
#                    except Exception:
#                        pass

            await asyncio.sleep(10)
        except Exception as e:
            log(f"⚠ Ошибка Position-Tracker: {e}")
            await asyncio.sleep(15)

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

        # 3. Фильтры безопасности (Анти-Шторм + Anti-Wick)
        if not (dna.get('min_w', 0.8) <= width <= dna.get('width', 2.0)): return None
        candle_size = (df['h'].iloc[-1] / df['l'].iloc[-1] - 1)
        if candle_size > 0.008: return None

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
        is_buy = (cur_p >= long_trigger) and (cur_p > prev_open) and (wick_ratio_long > 0.35)
        is_sell = (cur_p <= short_trigger) and (cur_p < prev_open) and (wick_ratio_short > 0.35)

        if not (is_buy or is_sell): return None

        # --- [ТРАНСПЛАНТАЦИЯ ГЕОМЕТРИИ СВЕЧИ V26.0] ---
        # Расчет полноты живой свечи, чтобы отсечь флэт-шум
        high_now = max(df['h'].iloc[-1], cur_p)
        low_now = min(df['l'].iloc[-1], cur_p)
        live_candle_range = high_now - low_now if (high_now - low_now) > 0 else 0.000001

        up_shadow = high_now - cur_p
        dn_shadow = cur_p - low_now
        long_body = cur_p - prev_open
        short_body = prev_open - cur_p

        shadow_limit = 0.30  # Тень не более 30% от всей свечи
        body_limit = 0.60    # Тело не менее 60% от всей свечи

        if is_buy: # Геометрический фильтр для ЛОНГА
            if (up_shadow / live_candle_range) > shadow_limit or (long_body / live_candle_range) < body_limit:
                return None
        elif is_sell: # Геометрический фильтр для ШОРТА
            if (dn_shadow / live_candle_range) > shadow_limit or (short_body / live_candle_range) < body_limit:
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
        await asyncio.sleep(2.5) # Пауза после полного круга

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
#        cur_p = memory.prices.get(symbol)
#        if not cur_p: return
        # БРОНИРОВАННОЕ ЧТЕНИЕ ЦЕНЫ: Ищем оба формата ключа в WebSocket-потоке
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

        dna = memory.dna_fleet.get(symbol)
        if not dna: return

        # Локальная инициализация
        if symbol not in memory.trail_active: memory.trail_active[symbol] = False
        if symbol not in memory.tp_fixed: memory.tp_fixed[symbol] = {'tp1': False, 'tp2': False}

        current_mode = 'stable'
        for m, matrix in memory.all_dna.items():
            if matrix == memory.dna_fleet: current_mode = m; break

        exit_side = 'SELL' if side in ['long', 'buy'] else 'BUY'
        bal_str = f"| Bal: ${round(memory.total_wallet, 2)}"

        # --- ЖЕСТКИЙ ФИКС ОБЪЯВЛЕНИЯ ID РЫНКА ---
        binance_market_id = symbol.replace('/', '').replace(':USDT', '')

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
        # --- [ЭТАЛОННЫЙ МОНОЛИТ ВЫХОДОВ V26.3 — БЕЗУПРЕЧНАЯ СЕПАРАЦИЯ] ---

        # 4. ЛОГИКА ТЕЙК-ПРОФИТА 1 (TP1)
        if not memory.tp_fixed[symbol]['tp1'] and profit >= dna['tp1']:
            close_qty_raw = vol * 0.5

            # Защита Notional $5.20
            if (close_qty_raw * cur_p) < 5.2:
                log(f"⚠ ОБЪЕМ МАЛ ДЛЯ ДРОБЛЕНИЯ {symbol}: Закрываем 100% по рынку для защиты кошелька.")
                await exchange.cancel_all_orders(binance_market_id)
                await exchange.create_market_order(symbol, exit_side, vol, {'reduceOnly': True})
                clean_memory_keys(symbol)
                return # Выход из тика

            action_triggered = False
            try:
                close_qty = exchange.amount_to_precision(symbol, vol * 0.5)
                await exchange.create_market_order(symbol, exit_side, close_qty, {'reduceOnly': True})

                await exchange.cancel_all_orders(binance_market_id)
                bu_price = float(exchange.price_to_precision(symbol, entry_p))
                rem_qty = exchange.amount_to_precision(symbol, vol - float(close_qty))

                await exchange.create_order(symbol, 'STOP_MARKET', exit_side, rem_qty, params={'stopPrice': bu_price, 'reduceOnly': True})

                memory.tp_fixed[symbol]['tp1'] = True
                memory.stop_placed[symbol] = bu_price
                log(f"🎯 TP1 ВЫПОЛНЕН: {symbol} (+{round(profit*100,2)}%) {bal_str}")
                action_triggered = True
            except Exception as e:
                log(f"⚠️ Ошибка TP1 {symbol}: {e}")

            if action_triggered: return # ФИКС: Обрываем тик строго ВНЕ try/except!

        # 5. ЛОГИКА ТЕЙК-ПРОФИТА 2 (TP2)
        if not memory.tp_fixed[symbol]['tp2'] and profit >= dna['tp2']:
            action_triggered = False
            try:
                # Если остаток позиции слишком мал для дробления — кроем 100%
                if (vol * cur_p) < 5.2:
                    log(f"⚠ Остаток мал для трейлинга {symbol}: Закрываем 100% на TP2.")
                    await exchange.cancel_all_orders(binance_market_id)
                    await exchange.create_market_order(symbol, exit_side, vol, {'reduceOnly': True})
                    clean_memory_keys(symbol)
                    return

                memory.tp_fixed[symbol]['tp2'] = True
                memory.trail_active[symbol] = True
                memory.max_pnl[symbol] = profit
                log(f"🔥 TP2 ФИКСИРОВАН: {symbol}. Включен Трейлинг [{current_mode.upper()}] {bal_str}")
                action_triggered = True
            except Exception as e:
                log(f"⚠️ Ошибка TP2 {symbol}: {e}")

            if action_triggered: return # ФИКС: Обрываем тик строго ВНЕ try/except!

        # 6. ВЕДЕНИЕ АДАПТИВНОГО ТРЕЙЛИНГА ПО ШАГАМ
        if memory.trail_active[symbol]:
            trail_step = 0.0045 if current_mode == 'bull' else (0.0015 if current_mode == 'bear' else dna.get('trail', 0.0032))
            if profit > memory.max_pnl[symbol]:
                memory.max_pnl[symbol] = profit

            if profit <= (memory.max_pnl[symbol] - trail_step):
                log(f"🏁 ГИБРИДНЫЙ ТРЕЙЛИНГ: Закрытие {symbol} @ {round(profit*100,2)}% {bal_str}")
                try:
                    await exchange.cancel_all_orders(binance_market_id)
                    await exchange.create_market_order(symbol, exit_side, vol, {'reduceOnly': True})
                    clean_memory_keys(symbol)
                except Exception as e:
                    log(f"⚠️ Ошибка закрытия трейлинга {symbol}: {e}")
                return # Намертво обрываем тик после закрытия сделки
#=========
    except Exception as e: pass

def clean_memory_keys(symbol):
    """Тотальная зачистка флагов монеты при выходе"""
    if symbol in memory.tp_fixed: del memory.tp_fixed[symbol]
    if symbol in memory.trail_active: del memory.trail_active[symbol]
    if symbol in memory.stop_placed: del memory.stop_placed[symbol]
    if symbol in memory.max_pnl: del memory.max_pnl[symbol]
#==============
async def monitoring_cycle(exchange):
    """Цикл слежения за всеми открытыми позициями одновременно [V24.5 Трейл-Синхро]"""
    log("👁️ Мониторинг позиций запущен.")
    while memory.is_running:
        if memory.active_pos:
            tasks = []
            for sym, data in memory.active_pos.items():
                # Гарантируем, что ключ чистый, без двоеточий
                clean_sym = sym.replace(':USDT', '')
                tasks.append(monitor_logic(exchange, clean_sym, data))

            if tasks:
                await asyncio.gather(*tasks)
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
