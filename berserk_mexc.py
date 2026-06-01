# Геометрия полос Боллинджера и Капкана
BB_PERIOD = 20
BB_STD = 2.2
LIMIT_ORDER_TTL = 75           # Время жизни лимитки в стакане (секунды)

# === [УЛЬТИМАТИВНЫЙ ДНК-ПУЛЬТ УПРАВЛЕНИЯ V23.0 МОНОЛИТ] ===
MAX_SLOTS = 3
RISK_GEAR = 0.80
DEBUG_BEACONS = True

# Каноническая матрица индивидуальных параметров под каждый класс активов
DNA_MATRIX = {
    # КЛАСС 1: Высокоскоростные Мемы (Глубокие капканы, жирные тейки, быстрый маркет-вход 25с)
    'PEPE/USDT:USDT':   {'l_off': 0.0055, 's_off': 0.0055, 'tp1': 0.0120, 'tp2': 0.0380, 'tp3': 0.0550, 'sl': 0.018, 'ttl': 25},
    'WIF/USDT:USDT':    {'l_off': 0.0055, 's_off': 0.0055, 'tp1': 0.0120, 'tp2': 0.0350, 'tp3': 0.0500, 'sl': 0.018, 'ttl': 25},
    'SHIB/USDT:USDT':   {'l_off': 0.0050, 's_off': 0.0050, 'tp1': 0.0100, 'tp2': 0.0320, 'tp3': 0.0450, 'sl': 0.015, 'ttl': 25},
    'DOGE/USDT:USDT':   {'l_off': 0.0040, 's_off': 0.0040, 'tp1': 0.0080, 'tp2': 0.0220, 'tp3': 0.0350, 'sl': 0.015, 'ttl': 30},
    'NOT/USDT:USDT':    {'l_off': 0.0055, 's_off': 0.0055, 'tp1': 0.0120, 'tp2': 0.0380, 'tp3': 0.0550, 'sl': 0.018, 'ttl': 25},
    'POPCAT/USDT:USDT': {'l_off': 0.0065, 's_off': 0.0065, 'tp1': 0.0150, 'tp2': 0.0450, 'tp3': 0.0650, 'sl': 0.020, 'ttl': 25},
    'JASMY/USDT:USDT':  {'l_off': 0.0045, 's_off': 0.0045, 'tp1': 0.0090, 'tp2': 0.0280, 'tp3': 0.0400, 'sl': 0.015, 'ttl': 30},

    # КЛАСС 2: Технологичные Ракеты (Оптимальные капканы, средние тейки, маркет-вход 40с)
    'SOL/USDT:USDT': {'l_off': 0.0045, 's_off': 0.0045, 'tp1': 0.0065, 'tp2': 0.0185, 'tp3': 0.0420, 'sl': 0.012, 'ttl': 120},
    'SUI/USDT:USDT': {'l_off': 0.0035, 's_off': 0.0035, 'tp1': 0.0065, 'tp2': 0.0185, 'tp3': 0.0420, 'sl': 0.012, 'ttl': 60},
    'APT/USDT:USDT': {'l_off': 0.0035, 's_off': 0.0035, 'tp1': 0.0065, 'tp2': 0.0185, 'tp3': 0.0420, 'sl': 0.012, 'ttl': 60},
    'NEAR/USDT:USDT':   {'l_off': 0.0025, 's_off': 0.0025, 'tp1': 0.0065, 'tp2': 0.0185, 'tp3': 0.0420, 'sl': 0.012, 'ttl': 40},
    'FET/USDT:USDT':    {'l_off': 0.0025, 's_off': 0.0025, 'tp1': 0.0065, 'tp2': 0.0185, 'tp3': 0.0420, 'sl': 0.012, 'ttl': 40},
    'TIA/USDT:USDT':    {'l_off': 0.0030, 's_off': 0.0030, 'tp1': 0.0070, 'tp2': 0.0200, 'tp3': 0.0450, 'sl': 0.014, 'ttl': 40},
    'RNDR/USDT:USDT':   {'l_off': 0.0025, 's_off': 0.0025, 'tp1': 0.0065, 'tp2': 0.0185, 'tp3': 0.0420, 'sl': 0.012, 'ttl': 40},
    'RENDER/USDT:USDT': {'l_off': 0.0025, 's_off': 0.0025, 'tp1': 0.0065, 'tp2': 0.0185, 'tp3': 0.0420, 'sl': 0.012, 'ttl': 40},

    # КЛАСС 3: Тяжелые Якоря и Дефай (Узкие капканы, консервативные тейки, ожидание лонга до 55с)
    'DOT/USDT:USDT':    {'l_off': 0.0015, 's_off': 0.0015, 'tp1': 0.0040, 'tp2': 0.0120, 'tp3': 0.0250, 'sl': 0.010, 'ttl': 55},
    'C98/USDT:USDT':    {'l_off': 0.0020, 's_off': 0.0020, 'tp1': 0.0050, 'tp2': 0.0150, 'tp3': 0.0300, 'sl': 0.010, 'ttl': 55},
    'BNB/USDT:USDT':    {'l_off': 0.0010, 's_off': 0.0010, 'tp1': 0.0030, 'tp2': 0.0100, 'tp3': 0.0200, 'sl': 0.008, 'ttl': 55},
    'XRP/USDT:USDT':    {'l_off': 0.0012, 's_off': 0.0012, 'tp1': 0.0040, 'tp2': 0.0120, 'tp3': 0.0220, 'sl': 0.009, 'ttl': 55},
    'ADA/USDT:USDT':    {'l_off': 0.0015, 's_off': 0.0015, 'tp1': 0.0040, 'tp2': 0.0120, 'tp3': 0.0240, 'sl': 0.010, 'ttl': 55}
}

def get_coin_dna(symbol):
    """Экстрактор ДНК по полному флотскому ключу"""
    # Если прилетел чистый ключ 'SOL/USDT', принудительно дописываем суффикс
    full_key = symbol if ':USDT' in symbol else f"{symbol}:USDT"
    return DNA_MATRIX.get(full_key, {'l_off': 0.0025, 's_off': 0.0025, 'tp1': 0.0065, 'tp2': 0.0185, 'tp3': 0.0420, 'sl': 0.012, 'ttl': 45})

#def get_coin_dna(symbol):
#    """Канонический экстрактор индивидуальных ДНК-параметров с авто-дефолтами"""
#    clean_name = symbol.split('/')[0].upper()
#    return DNA_MATRIX.get(clean_name, {'l_off': 0.0025, 's_off': 0.0025, 'tp1': 0.0065, 'tp2': 0.0185, 'tp3': 0.0420, 'sl': 0.012, 'ttl': 45})

# Список приоритетных фьючерсных секторов MEXC
#PRIORITY_LIST = [
#    'SOL/USDT:USDT', 'NEAR/USDT:USDT', 'LDO/USDT:USDT', 'OP/USDT:USDT',
#    'APT/USDT:USDT', 'MANA/USDT:USDT', 'POL/USDT:USDT', '1INCH/USDT:USDT'
#]
PRIORITY_LIST = [
    'SOL/USDT:USDT', 'NEAR/USDT:USDT', 'APT/USDT:USDT', 'SUI/USDT:USDT',
    'FET/USDT:USDT', 'TIA/USDT:USDT', 'PEPE/USDT:USDT', 'WIF/USDT:USDT',
    'SHIB/USDT:USDT', 'POL/USDT:USDT'
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
    """
    Синхронный шлюз ордеров V22.2: Абсолютная броня выходов МЕХС.
    Полностью ликвидирует ошибки 7003, 600 и Parameter error.
    """
    try:
        amount_str = exchange.amount_to_precision(symbol, amount)
        qty = float(amount_str)
        if qty <= 0:
            return False

        # Базовая каноническая упаковка параметров Isolated для MEXC
        params = {
            'openType': int(1),       # 1: Изолированная маржа (Isolated)
            'leverage': int(25),      # Жесткое плечо 25х
        }

        # СЦЕНАРИЙ 1: КАНОНИЧЕСКИЙ ДВУХКОНТУРНЫЙ СТОП-МАРКЕТ С ИСПРАВЛЕНИЕМ СИМВОЛОВ (V26.0)
        if is_stop:
            if price is None:
                return False

            exact_trigger_price = float(exchange.price_to_precision(symbol, price))

            # КОНТУР А: Универсальный фьючерсный стоп-маркет CCXT (Выставляет План-Ордер)
            try:
                mexc_algo_params = {
                    'stopPrice': exact_trigger_price,
                    'triggerPrice': exact_trigger_price,
                    'openType': int(1),           # Isolated маржа
                    'triggerType': int(2),         # Активация по цене Last Price
                    'reduceOnly': True
                }

                # Базовый метод CCXT сам превратит "NEAR/USDT:USDT" в нужный внутренний ID биржи!
                order = exchange.create_order(symbol, 'stop_market', side, qty, None, mexc_algo_params)
                return order

            except Exception as mexc_9999_err:
                # КОНТУР Б: Резервный REST-удар триггеров общего стакана при сетевом лаге 9999
                time.sleep(0.2)
                #log(f"⚠️ Алго-шлюз Контура А выдал лаг {mexc_9999_err}. Активирую резервный Контур Б общего стакана!")

                try:
                    # Формируем чистый низкоуровневый REST-пакет, переводя тикер через внутренний маркер CCXT
                    mexc_market_id_raw = exchange.market_id(symbol)
                    mexc_side_raw = int(3) if side.lower() == 'sell' else int(4)
                    mexc_trend_raw = int(1) if side.lower() == 'sell' else int(2)

                    mexc_base_stop_params = {
                        'symbol': mexc_market_id_raw,  # Берем системный ID из ядра CCXT (с нижним подчеркиванием!)
                        'side': mexc_side_raw,
                        'vol': float(qty),
                        'leverage': int(25),
                        'openType': int(1),
                        'orderType': int(5),           # 3: Условный маркет общего движка
                        'price': float(0),             # Рыночное исполнение по триггеру требует 0
                        'triggerType': int(2),
                        'triggerPrice': exact_trigger_price,
                        'trend': mexc_trend_raw
                    }

                    #log(f"🚨 [DEBUG STOP-B REST V26.0]: Sending Direct Pack: {mexc_base_stop_params}")
                    order = exchange.contractPrivatePostOrderCreate(mexc_base_stop_params)
                    return order
                except Exception as fatal_sl_err:
                    #log(f"🆘 КАТАСТРОФА: Оба контура стоп-лосса отвергнуты MEXC для {symbol}: {fatal_sl_err}")
                    return False

        # СЦЕНАРИЙ 2: Пассивный Лимитный Капкан Maker
        elif is_limit:
            if price is None:
                return False
            exact_price = float(exchange.price_to_precision(symbol, price))
            order = exchange.create_order(symbol, 'limit', side, qty, exact_price, params)
            return order

        # СЦЕНАРИЙ 3: Тотальный снос позиции (Тейки, Decay Shield, Сползание)
        else:
            if is_exit:
                params.update({'reduceOnly': True})
                # Бьем чистым фьючерсным маркет-ордером закрытия, обходя капризный close_position
                order = exchange.create_order(symbol, 'market', side, qty, None, params)
                return order
            else:
                # Обычный маркет-вход при налитии капкана
                order = exchange.create_order(symbol, 'market', side, qty, None, params)
                return order

    except Exception as e:
        log(f"⚠ Сбой шлюза ордеров {symbol} ({side.upper()}): {e}")
        return False
#=================
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
            #log(f"⚠️ Ошибка WebSocket потока цен: {ws_err}")
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

        # --- [ФИЛЬТР 2: АДАПТИВНЫЙ VOLUME SPIKE & МУСОРНЫЙ ФИЛЬТР МЕХС V26.0] ---
        # --- [ФИЛЬТР 2: КВАНТОВЫЙ ИHВЕРСНЫЙ VOLUME SHIELD V26.8] ---
        live_volume = float(df_candles[-1][5])  # Живой тиковый объем текущей минуты
        prev_volume = float(df_candles[-2][5])  # Полный объем прошлой минуты
        mean_volume = sum(float(c[5]) for c in df_candles[-6:-1]) / 5

        if mean_volume <= 0:
             return None
        volume_ratio = live_volume / mean_volume

        # Вычисляем истинную математическую дельту угасания тренда
        # Если импульс прет по тренду на нас (live_volume > prev_volume) — мы ОБЯЗАНЫ УЙТИ ИЗ-ПОД УДАРА!
        if is_buy_candidate:
           # Ловим разворот на лоях: капкан ставится только если лавина продаж ИССЯКАЕТ (объем падает)
            if live_volume >= prev_volume:
               # log(f"🛡️ [VOLUME OVERFLOW]: Слив по {symbol} усиливается. Убираю капкан лонга.")
                return None
        elif is_sell_candidate:
            # Ловим разворот на хаях: капкан шорта ставится только если памп ВЫДОХСЯ (объем падает)
            if live_volume >= prev_volume:
                # log(f"🛡️ [VOLUME OVERFLOW]: Памп по {symbol} прет вверх. Убираю капкан шорта.")
                return None

        # Базовая защита от микро-шума стакана
        is_meme = any(m in symbol.upper() for m in ['PEPE', 'SHIB', 'WIF', 'POPCAT', 'DOGE', 'BONK'])
        required_ratio = 1.8 if is_meme else 1.1
        if volume_ratio < required_ratio:
            return None

        # --- [ФИЛЬТР 3: PRE-CANDLE SHIELD — КАСКАДНЫЙ НОЖ ПРЕДЫСТОРИИ] ---
        p_c1 = df_candles[-2]  # Прошлая закрытая минута
        p_c2 = df_candles[-3]  # 2 минуты назад
        p_c3 = df_candles[-4]  # 3 минуты назад

       # is_3_green = (p_c1[4] > p_c1[1]) and (p_c2[4] > p_c2[1]) and (p_c3[4] > p_c3[1])
       # is_3_red   = (p_c1[4] < p_c1[1]) and (p_c2[4] < p_c2[1]) and (p_c3[4] < p_c3[1])
        # --- ЖЕСТКИЙ ШТУЧНЫЙ ФИКС V19.9: КАHОНИЧЕСКИЕ ЦИФРOВЫЕ ИHДЕКСЫ СПИСКА CCXT ---
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
        coin_dna = get_coin_dna(symbol)
        if is_buy_candidate:
            up_shadow = abs(c_high - max(c_open, c_close))
            long_body = abs(c_open - c_close)
            if (up_shadow / live_candle_range) > shadow_limit or (long_body / live_candle_range) < body_limit:
                return None

            # Вычисляем точную ювелирную цену лимитного капкана под нижней полосой
            order_price = lower_band * (1 - coin_dna['l_off'])
            return {'side': 'buy', 'price': order_price, 'upper_band': upper_band, 'lower_band': lower_band}

        elif is_sell_candidate:
            dn_shadow = abs(min(c_open, c_close) - c_low)
            short_body = abs(c_open - c_close)
            if (dn_shadow / live_candle_range) > shadow_limit or (short_body / live_candle_range) < body_limit:
                return None

            # Вычисляем точную ювелирную цену лимитного капкана над верхней полосой
            order_price = upper_band * (1 + coin_dna['s_off'])
            return {'side': 'sell', 'price': order_price, 'upper_band': upper_band, 'lower_band': lower_band}

    except Exception as scan_err:
        log(f"⚠ Ошибка сканирования {symbol}: {scan_err}")
        return None
    return None

async def monitor_logic(exchange):
    """Адаптивное управление выходами V16.9: Фикс лотов SOL, Квантовый Храповик 60с и Синдром Сползания"""
    last_pos_sync = 0
    while memory.is_running:
      try:
        now_time = time.time()

        # ДЕБАГ №1: Проверяем, видит ли вообще функция активные позиции в RAM
#        if int(now_time) % 10 == 0 and memory.active_pos:
#            log(f"🔍 [DEBUG 1]: В памяти RAM active_pos числятся ключи: {list(memory.active_pos.keys())}")

        for symbol, pos in list(memory.active_pos.items()):
            age = now_time - pos['entry_time']

#===========
            exit_side = 'sell' if pos['side'].lower() == 'buy' else 'buy'
#+++++++++++

            # --- ШТУЧНЫЙ ПЕРЕКЛЮЧАТЕЛЬ ДНК V23.0 ---
            coin_dna = get_coin_dna(symbol)
            TP1_PCT = coin_dna['tp1']
            TP2_PCT = coin_dna['tp2']
            TP3_PCT = coin_dna['tp3']
            PRIMARY_SL_PCT = coin_dna['sl']

            # ДЕБАГ №2: Проверяем, какие ключи цен сейчас лежат в WebSocket-таблице memory.prices
#            if int(now_time) % 10 == 0:
#               log(f"🔍 [DEBUG 2]: Сканирую {symbol} | В memory.prices сейчас есть ключи: {list(memory.prices.keys())[:5]}")

            # --- ЖЕСТКИЙ ШТУЧНЫЙ ФИКС V21.1: НЕУЯЗВИМЫЙ REST/WS ГИБРИД ЦЕН ---
            # Проверяем наличие монеты в WebSocket кэше
            cur_p = memory.prices.get(symbol, 0.0)

            # Если WebSocket еще не успел прогреться или монета в хвосте списка (как 1INCH)
            if cur_p <= 0:
                try:
                    # Разгружаем контур: берем точечный секундный тикер напрямую по REST
                    ticker_data = exchange.fetch_ticker(symbol)
                    cur_p = float(ticker_data.get('last', ticker_data.get('close', 0.0)))
                except:
                    cur_p = 0.0

#            if cur_p <= 0:
#                if int(now_time) % 10 == 0:
#                    log(f"⚠️ [DEBUG 3 ОТКЛОНЕНИЕ]: Для {symbol} цена не пробита ни по WS, ни по REST! Пропуск.")
#                continue

            cur_p = float(cur_p)
#==========
#===========


            # Вычисляем PNL
            profit = (cur_p / pos['price'] - 1) if pos['side'].lower() == 'buy' else (pos['price'] / cur_p - 1)
#===========
            # --- [ВРЕЗКА V23.0: EMERGENCY TREND EVACUATION ПРОТИВ BTC] ---
            # --- [ВРЕЗКА V25.5: ВЕКТОРНАЯ АДАПТИВНАЯ ЭВАКУАЦИЯ ПРОТИВ BTC] ---
            # Если Биткоин штормит прямо сейчас (включен MOMENTUM SHIELD)
            if hasattr(memory, 'btc_storm_time') and (now_time - memory.btc_storm_time < 2):
                if hasattr(memory, 'btc_history') and len(memory.btc_history) >= 2:
                    btc_dir_up = memory.btc_history[-1] > memory.btc_history[-2]
                    pos_long = pos['side'].lower() in ['buy', 'long']

                    # --- КВАНТОВЫЙ ВЕКТОРНЫЙ ЩИТ V25.5 ---
                    # Истинный снос срабатывает СТРОГО тогда, когда Биткоин наносит удар в наш залог:
                    is_long_under_attack = pos_long and not btc_dir_up     # Мы в Лонге, а Биткоин падает
                    is_short_under_attack = not pos_long and btc_dir_up    # Мы в Шорте, а Биткоин растет

                    if is_long_under_attack or is_short_under_attack:
                        log(f"🚨 [ЭВАКУАЦИЯ ТРЕНДА V25.5]: Поводырь пробивает залог позиции {symbol}! Экстренный маркет-снос.")
                        try:
                            for lim_sym, lim_info in list(memory.limit_orders.items()):
                                exchange.cancel_order(lim_info['id'], lim_sym)
                            memory.limit_orders.clear()
                            log(f"🧹 [ЭВАКУАТОР]: Лимитки {symbol} удалены. Зафиксированный итог: {r ound(profit*100, 2)}%")
                        except:
                            pass

                        # Немедленный рыночный снос позиции на бирже МЕХС
                        try:
                            params = {'openType': 1, 'leverage': int(25), 'reduceOnly': True}
                            exchange.create_order(symbol, 'market', exit_side, pos['vol'], None, params)
                        except:
                            pass

                        # Принудительное тотальное выжигание RAM во всех форматах ключей
                        for k in [symbol, f"{symbol}:USDT", symbol.replace(':USDT', '')]:
                            if k in memory.active_pos: del memory.active_pos[k]
                            if k in memory.tp1_fixed: del memory.tp1_fixed[k]
                            if k in memory.tp2_fixed: del memory.tp2_fixed[k]
                            if k in memory.stop_placed: del memory.stop_placed[k]
                            if k in memory.max_pnl_observed: del memory.max_pnl_observed[k]

                        memory.slots_occupied = max(0, memory.slots_occupied - 1)
                        continue


            if age > 0:
#=============
#                exit_side = 'sell' if pos['side'] == 'buy' else 'buy'
                mexc_market_id = symbol.replace('/', '').replace(':USDT', '')

                # --- 1. ВЫСТАВЛЕНИЕ ЖЕСТКОГО СЕРВЕРНОГО СТОП-ЛОССА НА МЕХС ---
                if not memory.stop_placed.get(symbol):
                    try:
                        sl_price = pos['price'] * (1 - PRIMARY_SL_PCT) if pos['side'] == 'buy' else pos['price'] * (1 + PRIMARY_SL_PCT)
                        sl_price_precision = float(exchange.price_to_precision(symbol, sl_price))
#                        sl_price_precision = float(exchange.price_to_precision(symbol, sl_price))
                        # Фикс шага цены под жесткие фьючерсные лоты MEXC
                        if sl_price_precision <= 0: sl_price_precision = round(sl_price, 4)

                        exact_vol = exchange.amount_to_precision(symbol, pos['vol'])

                        try: exchange.fapiPrivateDeleteAlgoOpenOrders({'symbol': mexc_market_id})
                        except: pass

                        smart_order(exchange, symbol, exit_side, exact_vol, price=sl_price_precision, is_stop=True)
                        memory.stop_placed[symbol] = sl_price_precision
                        log(f"🛡️ СЕРВЕРНЫЙ СТОП ВЫСТАВЛЕН: {symbol} @ {sl_price_precision}")
                        await asyncio.sleep(0.2)
                    except Exception as e:
                        log(f"🆘 Ошибка автостопа MEXC для {symbol}: {e}")
                        memory.stop_placed[symbol] = pos['price']
#=====
                # --- УЗЕЛ V21.9: ПЕРВИЧНЫЙ СТОП ОТКЛЮЧЕН ДЛЯ РАЗБЛОКИРОВКИ ТЕЙКОВ ---
#                memory.stop_placed[symbol] = True
#=====
                # --- [УЗЕЛ V16.9: КВАНТОВЫЙ ДЕЦЕНТРАЛИЗОВАННЫЙ ВЕНТИЛЬ ВЫХОДОВ НА МЕХС] ---
                if profit > 0:
                    memory.max_pnl_observed[symbol] = max(profit, memory.max_pnl_observed.get(symbol, profit))

                # ТРИГГЕР А: Раннее отсечение сползания альта с учетом проскальзывания на MEXC (60с / -0.08%)
                # --- [ВРЕЗКА V21.4: УЛЬТИМАТИВНЫЙ СИНДРОМ СПОЛЗАНИЯ МЕХС] ---
                # ТРИГГЕР А: Раннее отсечение сползания альта (Decay Shield)
#                if age > 60 and profit < -0.0008:
                # --- ШТУЧНЫЙ ФИКС V25.5: ИНТЕГРАЦИЯ ДНК-ТАЙМИНГОВ УДЕРЖАНИЯ ЛОТА ---
                is_meme_coin = any(m_n in symbol.upper() for m_n in ['PEPE', 'SHIB', 'WIF', 'POPCAT', 'DOGE', 'BONK'])
                is_anchor_coin = any(a_n in symbol.upper() for a_n in ['DOT', 'POL', 'BNB', 'XRP', 'ADA'])

                if is_meme_coin:
                    optimal_decay_ttl = 120    # Мемы: 2 минуты жизни
                elif is_anchor_coin:
                    optimal_decay_ttl = 420    # Якоря: 7 минут жизни
                else:
                    optimal_decay_ttl = 240    # Тех-Ракеты (NEAR, SOL, APT, SUI): 4 минуты оптимального разбега

                if age > optimal_decay_ttl and profit < -0.0008:

                    #log(f"🛡 Decay Shield V16.9: {symbol} утилизирован по времени (Лосс: {round(pro fit*100,2)}%)")
                    # Вычисляем грязную прибыль/убыток в USDT с учетом 25х плеча
                    pnl_usdt = pos['vol'] * pos['price'] * profit
                    log(f"🛡️ [DECAY SHIELD EXIT]: {symbol} утилизирован по времени. | Итог: {round( profit * 100, 2)}% ({round(pnl_usdt, 4)} USDT) | Живой Equity МЕХС: ${round(memory.total_wallet, 2)}")
                    action_triggered_decay = False
#===================
                    # --- ЖЕСТКИЙ МОНОЛИТ V24.2: ДВУХКОНТУРНАЯ ИЗОЛЯЦИЯ DECAY SHIELD ---
                    try:
                        try: exchange.fapiPrivateDeleteAlgoOpenOrders({'symbol': mexc_market_id})
                        except: pass

                        # Шлем приказ сноса на биржу
                        params = {'openType': 1, 'leverage': int(25), 'reduceOnly': True}
                        exchange.create_order(symbol, 'market', exit_side, pos['vol'], None, params)
                    except Exception as e:
                        # Логируем только реальные сбои, игнорируя повторный спам закрытых ордеров
                        # --- ШТУЧНЫЙ ФИКС V26.9: ГЛУШЕНИЕ ЭХА ПOВТOРНЫХ СHOСOВ МЕХС ---
                        err_str = str(e).lower()
                        if "2009" not in err_str and "nonexistent" not in err_str and "closed" not in err_str:
                            log(f"⚠️ Ошибка утилизации типа А для {symbol}: {e}")
                    finally:
                        # === КОНТУР АБСОЛЮТНОЙ ГАРАНТИИ: ВЫПОЛНЯЕТСЯ ВСЕГДА ===
                        # Выжигаем монету из памяти RAM в любом случае, ликвидируя петлю зацикливания!
                        for k in [symbol, f"{symbol}:USDT", symbol.replace(':USDT', '')]:
                            if k in memory.active_pos: del memory.active_pos[k]
                            if k in memory.tp1_fixed: del memory.tp1_fixed[k]
                            if k in memory.tp2_fixed: del memory.tp2_fixed[k]
                            if k in memory.stop_placed: del memory.stop_placed[k]
                            if k in memory.max_pnl_observed: del memory.max_pnl_observed[k]

                        memory.slots_occupied = max(0, memory.slots_occupied - 1)
                        log(f"🧹 [DECAY FINALLY CLEAN]: {symbol} гарантированно удален из RAM. Слот  свободен.")
                    continue
#===================
                # ТРИГГЕР Б: Синдром Сползания Импульса (Выдох ММ на хаях)
                if symbol in memory.max_pnl_observed and memory.max_pnl_observed[symbol] >= 0.0025:
                    current_decay_pct = (1 - (profit / memory.max_pnl_observed[symbol])) * 100
                    if current_decay_pct > 70.0:
                        pnl_usdt = pos['vol'] * pos['price'] * profit
                        log(f"🏁 [СПОЛЗАНИЕ ФИКСАЦИЯ]: {symbol} закрыт по маркету! Пик тренда: +{round(memory.max_pnl_observed[symbol]*100, 2)}% | Фиксация на выходе: +{round(profit*100, 2)}% | Заработано: {round(pnl_usdt, 4)} USDT | Equity: ${round(total_equity, 2)}")

                        #log(f"🏁 СИНДРОМ СПОЛЗАНИЯ ИМПУЛЬСА: {symbol} закрыт на МЕХС. ММ выдохся (Пик: +{round(memory.max_pnl_observed[symbol]*100, 2)}%)")
                        action_triggered_momentum_dead = False
                        try:
                            try: exchange.fapiPrivateDeleteAlgoOpenOrders({'symbol': mexc_market_id})
                            except: pass

                            # Выход прямым маркетом с изолированными параметрами
                            params = {'openType': 1, 'leverage': int(25), 'reduceOnly': True}
                            exchange.create_order(symbol, 'market', exit_side, pos['vol'], None, params)
                            action_triggered_momentum_dead = True
                        except Exception as e:
                            log(f"⚠ Ошибка Синдрома Сползания типа Б: {e}")

                        if action_triggered_momentum_dead:
                            for k in [symbol, symbol.replace(':USDT', '')]:
                                if k in memory.active_pos: del memory.active_pos[k]
                                if k in memory.tp1_fixed: del memory.tp1_fixed[k]
                                if k in memory.tp2_fixed: del memory.tp2_fixed[k]
                                if k in memory.stop_placed: del memory.stop_placed[k]
                                if k in memory.step_be: del memory.step_be[k]
                                if k in memory.max_pnl_observed: del memory.max_pnl_observed[k]
                            memory.slots_occupied = max(0, memory.slots_occupied - 1)
                            continue

#=============

                # --- 3. ШТАТНАЯ ФИКСАЦИЯ ТЕЙКА 1 (С ЖЕСТКИМ ФИКСОМ ОКРУГЛЕНИЯ МАЛЫХ ЛОТОВ SOL) ---
#                log(f"🎯 [ДЕБАГ симбол  {symbol}]: Перед условием! мемори= {memory.tp1_fixed.get(symbol)} профит={profit} >= TP1 {TP1_PCT}  ")

                if not memory.tp1_fixed.get(symbol) and profit >= TP1_PCT:
#                    log(f"🎯 [ДЕБАГ ТЕЙК-1 {symbol}]: Зашел внутрь условия! Пытаюсь закрыть объем...")
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
                            #smart_order(exchange, symbol, exit_side, close_qty, is_exit=True, price=None)

                            for k in [symbol, symbol.replace(':USDT', '')]:
                                if k in memory.active_pos: del memory.active_pos[k]
                                if k in memory.tp1_fixed: del memory.tp1_fixed[k]
                                if k in memory.tp2_fixed: del memory.tp2_fixed[k]
                                if k in memory.stop_placed: del memory.stop_placed[k]
                                if k in memory.max_pnl_observed: del memory.max_pnl_observed[k]
                            memory.slots_occupied = max(0, memory.slots_occupied - 1)
                            return

                        # Если лот позволяет дробить — фиксируем базовые 30%
#===============
                        # --- ЖЕСТКИЙ ШТУЧНЫЙ ФИКС V21.6: УДАРНЫЙ КOHТУР ЧАСТИЧHОГО ЗАКРЫТИЯ ---
                        # 1. Сбрасываем 30% объема чистым фьючерсным маркет-ордером закрытия
                        pos['vol'] = float(exchange.amount_to_precision(symbol, pos['vol'] - close_qty))

                        try:
                            params = {'openType': 1, 'leverage': int(25), 'reduceOnly': True}
                            exchange.create_order(symbol, 'market', exit_side, close_qty, None, params)
                            memory.tp1_fixed[symbol] = True
                            log(f"🎯 ТЕЙК-1 УСПЕШHО ВЫПОЛHЕH: {symbol} частично зафиксирован (+{round(TP1_PCT*100, 2)}%)")
                        except Exception as e_m1:
                            log(f"🆘 Ошибка отправки Тейка-1 на МЕХС: {e_m1}")
                            memory.tp1_fixed[symbol] = True
                        await asyncio.sleep(0.2)
                        # 2. Рассчитываем и выставляем безубыточный стоп-лосс на остаток позиции
                        # --- [ВРЕЗКА V28.2: ИСПРАВЛЕННЫЙ ХРАПОВИК С ТЕЛЕМЕТРИЕЙ БАЛАНСА] ---
                        try:
                            # На МЕХС метод возвращает список синхронно, await перед ним вызовет TypeError!
                            exchange.cancel_all_orders(symbol, {'spot': False})

                            # Рассчитываем прецизионную цену БУ ровно на уровень нашего входа
                            bu_price = float(exchange.price_to_precision(symbol, pos['price']))

                            # Выставляем новый безубыточный СТОП-МАРКЕТ на МЕХС на оставшиеся 50% объема лота
                            await exchange.create_order(
                                symbol, 'STOP_MARKET', exit_side, rem_vol,
                                params={'stopPrice': bu_price, 'reduceOnly': True}
                            )
                            memory.stop_placed[symbol] = bu_price
                            log(f"🛡️ [ХРАПОВИК МЕХС АКТИВИРОВАН]: Остаток {symbol} защищен в БУ @ { bu_price} | Живой Equity МЕХС: ${round(memory.total_wallet, 2)}")
                        except Exception as bu_err:
                            log(f"⚠️ Сбой авто-переноса в БУ на МЕХС для {symbol}: {bu_err}")
#============
                    except Exception as e:
                        log(f"🆘 Ошибка исполнения Тейка 1 {symbol}: {e}")

                # --- 4. ЛОГИКА ТЕЙК-ПРОФИТА 2 (ФИКС V21.3) ---
                if memory.tp1_fixed.get(symbol) and not memory.tp2_fixed.get(symbol) and profit >= TP2_PCT:
                    try:
                        # 0.57 — это правильный канонический коэффициент от остатка, чтобы сбросить ровно 40% от начального объема
                        close_qty = float(exchange.amount_to_precision(symbol, pos['vol'] * 0.57))
                        if close_qty > 0:
                            # Изменяем объем в памяти RAM перед следующим шагом к Тейку-3
                            pos['vol'] = float(exchange.amount_to_precision(symbol, pos['vol'] - close_qty))

                            # Отправляем ордер с жесткими флагами Isolated и leverage
                            params = {'openType': 1, 'leverage': int(25), 'reduceOnly': True}
                            exchange.create_order(symbol, 'market', exit_side, close_qty, None, params)

                            memory.tp2_fixed[symbol] = True
                            log(f"🏆 ТЕЙК-2 ВЫПОЛНЕН: {symbol} зафиксировано 40% объема (+{round(TP2_PCT*100, 2)}%)")
                    except Exception as e:
                        log(f"🆘 Ошибка Тейка 2 {symbol}: {e}")
#=====
                # --- 5. ЛОГИКА ТЕЙК-ПРОФИТА 3 ---

                # --- 5. ЛОГИКА ТЕЙК-ПРОФИТА 3 (МЕГА-ФИНАЛ 100% ВЫХОД) ---
                if memory.tp2_fixed.get(symbol) and profit >= TP3_PCT:
                    log(f"👑 ТЕЙК-3 МЕГА-ФИНАЛ: {symbol} достиг финальной цели (+{round(TP3_PCT*100, 2)}%)")
                    action_triggered_tp3 = False
                    exit_side = 'sell' if pos['side'].lower() == 'buy' else 'buy'
                    close_qty = pos['vol']

                    if close_qty > 0:
                        try:
                            # Удаляем системные сетки
                            try: exchange.fapiPrivateDeleteAlgoOpenOrders({'symbol': mexc_market_id})
                            except: pass

                            # Финишируем прямым маркет-ордером с жестким плечом 25
                            params = {'openType': 1, 'leverage': int(25), 'reduceOnly': True}
                            exchange.create_order(symbol, 'market', exit_side, close_qty, None, params)
                        except Exception as e_m4:
                            log(f"⚠ Ошибка Тейка-3 на МЕХС: {e_m4}")

                    # Полная зачистка RAM-памяти лота
                    for k in [symbol, symbol.replace(':USDT', '')]:
                        if k in memory.active_pos: del memory.active_pos[k]
                        if k in memory.tp1_fixed: del memory.tp1_fixed[k]
                        if k in memory.tp2_fixed: del memory.tp2_fixed[k]
                        if k in memory.stop_placed: del memory.stop_placed[k]
                        if k in memory.max_pnl_observed: del memory.max_pnl_observed[k]

                    memory.slots_occupied = max(0, memory.slots_occupied - 1)
                    continue
#==========
#==========
                    if action_triggered_tp3: return
        # Разгрузка процессора
        await asyncio.sleep(2)
      except Exception as e:
          await asyncio.sleep(1)
        #await asyncio.sleep(0.1)

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
                        coin_dna = get_coin_dna(symbol)
                        memory.active_pos[target_key] = {
                            'side': side,
                            'vol': vol,
                            'price': entry_price,
                            'entry_time': time.time(), # Стартуем таймер Храповика с текущей секунды
                            'dna': {'l_off': coin_dna['l_off'], 's_off': coin_dna['s_off']} # Временный кэш оффсета
                        }
#====
                        # --- ШТУЧНЫЙ ФИКС V21.4: АВТО-ПРОГРЕВ ФЛАГОВ ПРИ ПОДХВАТЕ ---
                        # Запрашиваем цену из WebSocket, чтобы понять где мы находимся
                        rec_p = memory.prices.get(target_key, 0.0)
                        if rec_p > 0:
                            rec_profit = (rec_p / entry_price - 1) if side == 'buy' else (entry_price / rec_p - 1)

                            # Если позиция уже пролетела Тейк-1 (+0.65%)
                            if rec_profit >= TP1_PCT:
                                memory.tp1_fixed[target_key] = True
                                log(f"🛡️ [ПРОГРЕВ RAM]: Сектор {target_key} уже выше Тейка-1 (PNL:  {round(rec_profit*100,2)}%). Блокирую повторный спам Тейка-1.")

                            # If позиция пролетела даже Тейк-2 (+1.85%)
                            if rec_profit >= TP2_PCT:
                                memory.tp2_fixed[target_key] = True
#====
                        memory.slots_occupied += 1
    except Exception as recover_err:
        log(f"⚠️ Критическая ошибка авто-усыновления MEXC: {recover_err}")
    # -------------------------------------------------------------------------
#========
#=====
    log(f"🏛️ 🏹 Охота лимитными капканами Berserk V16.9 активирована. Патрулирую стаканы...")

    # Инициализируем таймер фонового опроса позиций
    # --- [ВРЕЗКА V20.3: ОЧИЩЕННЫЙ ГЕНЕРАЛЬНЫЙ ЦИКЛ СНАЙПЕРА] ---
    last_pos_sync = 0

    while memory.is_running:
        try:
            now = time.time()

            # А. ТРЕКЕР УСЫНОВЛЕНИЯ ПОЗИЦИЙ СТРОГО РАЗ В 10 СЕКУНД
            if now - last_pos_sync >= 10:
                try:

                    # --- ШТУЧНЫЙ ФИКС V26.5: ЖИВОЙ ЕЖЕСЕКУНДНЫЙ СЪЕМ EQUITY МЕХС ---
                    try:
                        bal_refresh = exchange.fetch_balance({'type': 'swap'})
                        if isinstance(bal_refresh, dict) and 'USDT' in bal_refresh:
                            memory.total_wallet = float(bal_refresh['USDT'].get('total', memory.total_wallet))
                            memory.available = float(bal_refresh['USDT'].get('free', memory.available))
                    except:
                        pass
                    raw_positions = exchange.fetch_positions(None, {'type': 'swap'})
                    current_mexc_active = []

                    for p in raw_positions:
                        vol_raw = p.get('contracts', p.get('positionAmt', p.get('size', p.get('marginSize', 0.0))))
                        vol = abs(float(vol_raw)) if vol_raw is not None else 0.0

                        if vol > 0.00001:
                            raw_sym = p.get('symbol', p.get('pair', ''))
                            clean_sym = raw_sym.replace('_', '/').replace(':USDT', '')
                            fleet_key = f"{clean_sym}:USDT"
                            target_key = fleet_key if fleet_key in PRIORITY_LIST else clean_sym

                            if target_key in PRIORITY_LIST:
                                current_mexc_active.append(target_key)

                                if target_key not in memory.active_pos:
                                    side_raw = str(p.get('side', p.get('positionSide', p.get('direction', 'long')))).lower()
                                    side = 'buy' if ('long' in side_raw or 'buy' in side_raw or 'open_long' in side_raw) else 'sell'
                                    entry_price = float(p.get('entryPrice', p.get('price', p.get('avgEntryPrice', 0.0))))

                                    log(f"🔗🔗 ЖИВОЙ ПЕРЕХВАТ MEXC V20.3: Усыновляем контракт {target_key} ({vol} лотов).")
                                    memory.active_pos[target_key] = {
                                        'side': side, 'vol': vol, 'price': entry_price, 'entry_time': time.time(),
                                        'dna': {'l_off': 0.002, 's_off': 0.002}
                                    }

                    # --- ШТУЧНЫЙ ФИКС V26.0: СИНХРОНИЗАЦИЯ КЛЮЧЕЙ И ТЕЛЕМЕТРИЯ EQUITY МЕХС ---
                    for sym in list(memory.active_pos.keys()):
                        if sym not in current_mexc_active:
                            try:
                                pos_data = memory.active_pos[sym]
                                log(f"🏁 [ФИКСАЦИЯ МЕХС]: Позиция {sym} закрыта. Принудительный клининг. | Живой Equity МЕХС: ${round(memory.total_wallet, 2)}")
                            except:
                                log(f"🏁 [ФИКСАЦИЯ МЕХС]: Позиция {sym} закрыта. Принудительный клининг. | Живой Equity МЕХС: ${round(memory.total_wallet, 2)}")

                            # Каскадное выжигание всех типов ключей
                            for k in [sym, f"{sym}:USDT", sym.replace(':USDT', '')]:
                                if k in memory.active_pos: del memory.active_pos[k]
                                if k in memory.tp1_fixed: del memory.tp1_fixed[k]
                                if k in memory.tp2_fixed: del memory.tp2_fixed[k]
                                if k in memory.stop_placed: del memory.stop_placed[k]
                                if k in memory.max_pnl_observed: del memory.max_pnl_observed[k]

                    memory.slots_occupied = len(current_mexc_active)
                    last_pos_sync = now
#                except:
#                    pass
                except Exception as main_loop_err:
                    # --- ШТУЧНЫЙ ФИКС V26.9: ГЛУШЕНИЕ ОШИБОК БАЛАНСА И СИРОТ В ХВОСТЕ ЦИКЛА ---
                    err_str = str(main_loop_err).lower()
                    if "2009" not in err_str and "2005" not in err_str and "nonexistent" not in err_str:
                        log(f"⚠️ Системный сбой трекера позиций: {main_loop_err}")

            # Б. REST-ПОЛУЧЕНИЕ ЦЕНЫ BTC ДЛЯ ИСТОРИИ СТРОГО РАЗ В 60 СЕКУНД (Защита от дублей)
            if now - memory.last_btc_push >= 60:
                try:
                    btc_ticker = exchange.fetch_ticker('BTC/USDT:USDT')
                    btc_price = float(btc_ticker.get('last', btc_ticker.get('close', 0.0)))
                    if btc_price > 0:
                        if not hasattr(memory, 'btc_history'):
                            memory.btc_history = []
                        memory.btc_history.append(btc_price)
                        memory.btc_history = memory.btc_history[-15:] # Храним 15 минут
                        memory.last_btc_push = now
                except Exception as btc_err:
                    log(f"⚠ Ошибка REST-запроса Поводыря: {btc_err}")
                    memory.last_btc_push = now

            # В. КВАНТОВЫЙ REST MOMENTUM SHIELD (Обсчет реальной трендовой скорости)
            if hasattr(memory, 'btc_history') and len(memory.btc_history) >= 3:
                btc_window = memory.btc_history[-3:]
                m1_diff = abs(btc_window[-1] - btc_window[-2])
                m2_diff = abs(btc_window[-2] - btc_window[-3])
                avg_btc_move_pct = ((m1_diff + m2_diff) / 2) / btc_window[-1] * 100
#+++++++++++++++
                # --- [ФИКС V23.1: БЛОКИРОВКА ЦИКЛА ПРИ ШТОРМЕ] ---
                if avg_btc_move_pct > 0.12:
                    memory.btc_storm_time = now
                    if not hasattr(memory, 'last_momentum_log'): memory.last_momentum_log = 0
                    if now - memory.last_momentum_log >= 60:
                        #log(f"🛡 [MOMENTUM SHIELD ACTIVATE]: REST-скорость BTC опасна ({round(avg_b tc_move_pct, 4)}% > 0.045%). Включаю 90с таймер остывания.")
                        memory.last_momentum_log = now

                # Жестко обрываем итерацию и уходим на новый круг, если 90 секунд еще не прошло
#                if hasattr(memory, 'btc_storm_time') and (now - memory.btc_storm_time < 90):
#                    await asyncio.sleep(0.5)
#                    continue  # Входы заблокированы наглухо!

# ------------------------------------------------------------------

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
                       # qty = amount_usdt / signal['price']
                        # --- ШТУЧНЫЙ ФИКС V20.5: ПЕРЕВОД USDT В КАНOНИЧЕСКИЕ КОНТРАКТЫ MEXC ---
                        try:
                            market_data = exchange.market(symbol)
                            contract_size = float(market_data.get('contractSize', 1.0))
                        except:
                            contract_size = 1.0

                        # Стоимость одного контракта в USDT = цена монеты * размер контракта
                        contract_value_usdt = signal['price'] * contract_size
                        qty = amount_usdt / contract_value_usdt



                        # Выставляем пассивный лимитный капкан Maker
                        order = smart_order(exchange, symbol, signal['side'], qty, is_limit=True, price=signal['price'])
                        if order and isinstance(order, dict):
                            order_id = order.get('id')
                            memory.limit_orders[symbol] = {
                                'id': order_id, 'timestamp': time.time(), 'price': signal['price'],
                                'side': signal['side'], 'qty': qty, 'dna': signal
                            }

                            log(f"🚀 ВЗВЕДЕН ЛИМИТНЫЙ КАПКАН Maker (ISOLATED): {symbol} {signal['side'].upper()} @ {signal['price']}")
#========
            # === [УЗЕЛ V26.9: ВЕКТОРНЫЙ КВАНТОВЫЙ ВЕНИК & МАРКЕТ-УСКОРИТЕЛЬ МЕХС] ===
            for sym_key in list(memory.limit_orders.keys()):
                order_data = memory.limit_orders[sym_key]
                order_age = now - order_data['timestamp']

                coin_dna = get_coin_dna(sym_key)
                optimal_ttl = coin_dna.get('ttl', 40)

                if order_age >= optimal_ttl:
                    try:
                        # А. Математический фильтр: считываем живые 1m свечи по REST-тикеру
                        try:
                            clean_rest_symbol = sym_key.split(':')[0]
                            ohlcv_check = exchange.fetch_ohlcv(clean_rest_symbol, '1m', limit=3)
                            if len(ohlcv_check) >= 2:
                                v_now = float(ohlcv_check[-1][5])
                                v_prev = float(ohlcv_check[-2][5])
                                volume_growing = v_now > v_prev
                            else:
                                volume_growing = True
                        except:
                            volume_growing = True

                        # Б. Прямой Maker-демонтаж зависшего ордера из стакана
                        try:
                            exchange.cancel_order(order_data['id'], sym_key)
                        except Exception as direct_cancel_err:
                            err_msg = str(direct_cancel_err).lower()
                            if "not found" in err_msg or "filled" in err_msg:
                                volume_growing = True

                        # Принудительно очищаем таблицу лимиток в RAM
                        if sym_key in memory.limit_orders:
                            del memory.limit_orders[sym_key]

                        # В. ИСТИННЫЙ ВЕКТОРНЫЙ ОПРЕДЕЛИТЕЛЬ (Защита от прорыва против маржи)
                        is_order_buy = order_data['side'].lower() in ['buy', 'long']

                        # Сверяем направление живого сквиза цены относительно нашего капкана
                        cur_m_price = memory.prices.get(sym_key, 0.0)
                        if cur_m_price > 0:
                            price_going_up = cur_m_price > order_data['price']
                        else:
                            price_going_up = is_order_buy # Резервный флаг, если сокет завис

                        # Фильтруем вектор: вход вдогонку разрешен ТОЛЬКО если импульс идет ПОПУТНО нашей сделке!
                        # Если мы хотели BUY, а цена улетела ВВЕРХ без нас -> это истинный пробой тренда, бьем вдогонку.
                        # Если мы хотели BUY, а цена рушится ВНИЗ на объемах против нас -> маркет-вход блокируется наглухо!
                        is_trend_support = (is_order_buy and price_going_up) or (not is_order_buy and not price_going_up)

                        # Г. ИСПОЛНИТЕЛЬНЫЙ КОНТУР V28.0 (КВАНТОВАЯ РОТАЦИЯ МАРЖИ И ВХОД НА ВСЕ ДЕПО)
                        if volume_growing and is_trend_support:
                            log(f"🚀 [МАРКЕТ-ВХОД ВДОГОНКУ V28.0]: Капкан по {sym_key} не налился. Выжигаю чужие лимитки для входа на 100% депо!")
                            try:
                                # Намертво стираем абсолютно все остальные неналитые лимитные капканы на аккаунте
                                for any_sym in list(memory.limit_orders.keys()):
                                    try:
                                        exchange.cancel_order(memory.limit_orders[any_sym]['id'], any_sym)
                                        del memory.limit_orders[any_sym]
                                    except: pass

                                await asyncio.sleep(0.2) # Пауза 200мс для обновления кэша баланса МЕХС

                                # Считываем тотально освобожденный баланс кошелька
                                bal_refresh = await exchange.fetch_balance({'type': 'swap'})
                                if isinstance(bal_refresh, dict) and 'USDT' in bal_refresh:
                                    memory.available = float(bal_refresh['USDT'].get('free', memory.available))

                                # Пересчитываем максимальный объем USDT от всего свободного капитала
                                amount_usdt = memory.available * RISK_GEAR * 25
                                contract_value_usdt = order_data['price'] * contract_size
                                new_qty = amount_usdt / contract_value_usdt

                                # Страховой демпфер под неделимый шаг лотов МЕХС для SOL/SUI/APT/TIA/NEAR
                                if any(token in sym_key.upper() for token in ['SOL', 'SUI', 'APT', 'NEAR', 'TIA']):
                                    new_qty = new_qty / 10.0

                                # Округляем до разрешенного биржей количества контрактов
                                new_qty = float(exchange.amount_to_precision(sym_key, new_qty))
                                if new_qty <= 0: continue

                                exit_side_chase = order_data['side']
                                params_chase = {'openType': int(1), 'leverage': int(25)}

                                # Ударяем по рынку вдогонку на всю доступную котлету
                                market_order = exchange.create_order(sym_key, 'market', exit_side_chase, new_qty, None, params_chase)

                                if market_order:
                                    # Записываем сделку в оперативную память с прецизионной точностью нового объема
                                    memory.active_pos[sym_key] = {
                                        'side': order_data['side'],
                                        'vol': new_qty,
                                        'price': float(market_order.get('price', order_data['price'])),
                                        'entry_time': time.time(),
                                        'dna': order_data['dna']
                                    }
                                    memory.slots_occupied = len(memory.active_pos)
                            except Exception as market_chaser_err:
                                log(f"⚠️ Сбой маркет-входа вдогонку для {sym_key}: {market_chaser_err}")

                        else:
                            log(f"🧹 [ВЕНИК V26.9]: Капкан по {sym_key} стерт. Объем затух или сквиз  идет против нас. Маркет-вход ЗАБЛОКИРОВАН.")

                    except Exception as cancel_err:
                        err_msg = str(cancel_err).lower()
                        if "cannot be cancelled" in err_msg or "filled" in err_msg or "not found" in err_msg:
                            log(f"🔥 ПЕРЕХВАТ СКВИЗА V26.9: Ордер по {sym_key} успел исполниться в долю секунды отмены! Усыновляем позицию.")
                            if sym_key not in memory.active_pos:
                                memory.active_pos[sym_key] = {
                                    'side': order_data['side'],
                                    'vol': order_data['qty'],
                                    'price': order_data['price'],
                                    'entry_time': time.time(),
                                    'dna': order_data['dna']
                                }
                                memory.slots_occupied = len(memory.active_pos)
                            if sym_key in memory.limit_orders:
                                del memory.limit_orders[sym_key]

#========
        except Exception as main_err:
            await asyncio.sleep(1)
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    try: asyncio.run(main_logic())
    except KeyboardInterrupt: log("🛑 Снайпер Берсерк принудительно остановлен.")
