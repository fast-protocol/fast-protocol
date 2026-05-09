import math
import ccxt, time, pandas as pd
from datetime import datetime
# Класс защиты словарей (ОБЯЗАТЕЛЬНО ДОБАВЬ ЭТО)
class SafeDict(dict):
    def __getitem__(self, key):
        if key not in self: self[key] = False
        return super().__getitem__(key)

# --- НАСТРОЙКИ V5.5.1 STRIKE-DUO --- MEXC ---
API_KEY, SECRET_KEY = 'mx0vgl83gPpoR8dcim', '89d6e17b1041478aa1f8fffadaf6490e'

# --- ПУЛЬТ MEXC V12.6 [IRON-RECOVERY] ---
#PRIORITY_LIST = [
#    'APT/USDT:USDT', 'WLD/USDT:USDT', 'ORDI/USDT:USDT',
#    'OP/USDT:USDT', 'LDO/USDT:USDT', 'ARKM/USDT:USDT', 'LPT/USDT:USDT'
#]
# --- ПУЛЬТ MEXC V15.0 [GOLDEN-RATIO] ---
PRIORITY_LIST = [
    'SOL/USDT:USDT', 'NEAR/USDT:USDT', 'LDO/USDT:USDT', 'OP/USDT:USDT',
    'APT/USDT:USDT', 'MANA/USDT:USDT', 'POL/USDT:USDT', '1INCH/USDT:USDT'
]

# --- РИСК И ПЛЕЧО ---
LEVERAGE, RISK_PERCENT = 25, 0.85
BUFFER_CASH = 0.0
MAX_BANDWIDTH = 2.2      # Фильтр паники (в процентах)

# --- УМНЫЙ ПУЛЬТ УПРАВЛЕНИЯ ---
BASE_RISK = 0.85         # Базовый риск (переключатель скоростей)

# --- ЦЕЛИ (TAKE PROFIT) ---
# --- ЦЕЛИ V16.0 [TRIPLE-GEAR] ---
TP1_PCT = 0.0065         # Тейк 1 (+0.65%) - Фикс 30%
TP2_PCT = 0.0185         # Тейк 2 (+1.85%) - Фикс 40%
TP3_PCT = 0.0420         # Тейк 3 (+4.20%) - Фикс остаток 30%

TP1_SHARE = 0.30         # Доля первого тейка
TP2_SHARE = 0.40         # Доля второго тейка

# --- НОВЫЙ ФИЛЬТР (ENTRY_OFFSET) ---
#ENTRY_OFFSET = 0.0011    # 0.08% зазор безопасности
ENTRY_TRIGGER_OFFSET = 0.0018  # Когда "просыпаемся"
ENTRY_ORDER_OFFSET = 0.0020  # Где реально ставим капкан

# --- ЗАЩИТА (STOP LOSS) ---
PRIMARY_SL_PCT = 0.012   # Основной стоп (-1.2%)
SOFT_BE_PCT = -0.003     # Мягкий безубыток (-0.3%)
LOCK_THRESHOLD = 0.0055  # Порог включения замка (+0.5%)
LOCK_PROFIT = 0.0015     # Уровень замка (+0.15%)

# --- КОНВЕЙЕР И ТАЙМИНГИ ---
SURGEON_TIME = 1200       # Хирург (10 минут)
SURGEON_PROFIT = 0.0045  # Порог Хирурга (+0.28%)
TIME_LIMIT = 8400        # Тайм-аут (140 минут)
MAX_CANDLE_SIZE = 0.0075 # Анти-Шип (0.75%)

# --- ПРЕДОХРАНИТЕЛЬ (QUICK CUT) ---
# Теперь применяем ко всем активным монетам, так как они все волатильны
DANGER_COINS = ['SOL', 'NEAR', 'LDO', 'OP', 'APT', 'MANA', 'POL', '1INCH'] 
QC_TIME = 110           # 2 минуты
QC_LIMIT = -0.0052       # -0.4%   
# ==========================================   
MAX_BATCH = 1000000 #1500000
LIMIT_ORDER_TTL = 75  # Время жизни капкана в секундах
#--------
# Порог проверки исполнения тейка (Формула)
# Если фиксируем 50%, то проверка сработает, когда останется меньше 75% позиции
# Это дает запас 25% на проскальзывание и частичное исполнение
#TAKE_CHECK_THRESHOLD = 1.0 - (TP1_SHARE / 2)
#LIMIT_ORDER_TTL = 75  # Время жизни капкана в секундах
order_creation_time = SafeDict() # Новый словарь для тайминга ордеров
#===========================================
# Добавь новый словарь к остальным
entry_times = SafeDict()
lock_activated = SafeDict() # Для замка профита
# К твоим словарям добавь:
take_placed = SafeDict() 
partial_fixed = SafeDict() # Чтобы MEXC тоже стал многозадачным!
just_closed = SafeDict()   # Фикс петли
tp1_fixed = SafeDict()
tp2_fixed = SafeDict()
step_be = SafeDict()     # Уровень ступенчатого БУ
#--------

exchange = ccxt.mexc({
    'apiKey': API_KEY,
    'secret': SECRET_KEY,
    'options': {'defaultType': 'swap', 'positionMode': False},
    'enableRateLimit': True
})

last_stop_time, full_exit_triggered, current_idx = 0, False, 0

def log(msg):
    t = datetime.now().strftime('%H:%M:%S')
    with open("berserk_log.txt", "a") as f: f.write(f"[{t}] {msg}\n")
    print(f"[{t}] 🏛️ {msg}")

def smart_order(symbol, side, amount, is_limit=False, price=None, is_exit=False):
    """Ультра-стриминг с Liquidity Guard + Fix 2005"""
    success = True # <-- ДОБАВЬ ЭТУ СТРОКУ (Инициализация)
    if not is_exit and (amount / MAX_BATCH) > 80:
        log(f"⚠️ Низкая ликвидность {symbol}, пропуск."); return False
    remaining = amount
    while remaining > 0:
        batch = int(min(remaining, MAX_BATCH))
        try:
            # ЖЕСТКАЯ ПРОВЕРКА ДЛЯ ВЫХОДА ПО МАРКЕТУ (FIX 2005)
            # МЫ ЯВНО ГОВОРИМ БИРЖЕ: ЭТОТ ОРДЕР ДОЛЖЕН БЫТЬ ISOLATED
            params = {
                'openType': 1,           # 1: Isolated
                'leverage': int(LEVERAGE) # ТРЕБОВАНИЕ БИРЖИ ДЛЯ ISO
            }
            if is_exit: params['reduceOnly'] = True

            if is_limit and price is not None:
                exchange.create_order(symbol, 'limit', side, batch, price, params)
                mode = "Limit"
            else:
                exchange.create_order(symbol, 'market', side, batch, None, params)
                mode = "Market"
            log(f"📦 Стрим {symbol} ({mode}): {side} {batch} [ISO-MODE]")

            # ЭТИ СТРОКИ ОСТАВЛЯЕМ (ОНИ ВАЖНЫ!)
            remaining -= batch
            time.sleep(1.0)
        except Exception as e:
            # ТВОЯ АВАРИЙНАЯ ЛОГИКА (СОХРАНЯЕМ):
            if "7008" in str(e) and is_exit:
                p = price if price else float(exchange.fetch_ticker(symbol).get('last', 0))
                exchange.create_order(symbol, 'limit', side, int(remaining), p, {'reduceOnly': True})
                log(f"⚠️ Аварийная лимитка {symbol} по {p}"); break
            if "2051" in str(e):
                log(f"📉 Ликвидность {symbol} слишком мала (Limit Exceeded). Пропускаю монету.")
                return False # Выходим из функции немедленно и тихо
            log(f"❌ Order Error: {e}"); success = False; return False
    return {'status': 'success'} if success else False

def run_titan_stable():
    global last_stop_time, full_exit_triggered, current_idx
    log("🚀MEXC V12.6 [IRON-RECOVERY] - СТАРТ. True Partial + 1.5M Stream.")
    # --- ПРЕДПОЛЕТНАЯ ПОДГОТОВКА (Startup Setup) ---
    log("🔧 Настройка параметров плеча и маржи для флота...")
    for sym in PRIORITY_LIST:
        try:
        # Используем прямой метод request к эндпоинту из твоей документации
            params = {
                'symbol': sym,
                'leverage': int(LEVERAGE),
                'openType': 1 # 1: Isolated
            }
            # Путь берем из доков: /api/v1/private/position/change_leverage
            response = exchange.private_post_position_change_leverage(params)
            # Если снова будет NameError, используем exchange.request:
        except:
            try:
                # Ультимативный вариант через request
                exchange.request('position/change_leverage', 'private', 'POST', {
                    'symbol': sym, 'leverage': int(LEVERAGE), 'openType': 1
                })
            except: pass
    log("✅ Флот готов к бою.")
    bal = exchange.fetch_balance()
    total_bal = float(bal.get('total', {}).get('USDT', 0))
    # --- ДОБАВЬ ЭТУ СТРОКУ ЗДЕСЬ ---
    log(f"📡 МАЯК: MEXC в сети | Баланс: ${round(total_bal, 2)} | Оффсет: {ENTRY_ORDER_OFFSET}")
    # -----------------------------------------------
    while True:
        try:
#=====
            # Сначала получаем статус
            # БЛОКИРУЕМ ТОЛЬКО ЕСЛИ ВИСИТ ОРДЕР НА ВХОД


            bal = exchange.fetch_balance()
            total_bal = float(bal.get('total', {}).get('USDT', 0))
            # --- ДОБАВЬ ЭТУ СТРОКУ ЗДЕСЬ ---
            #log(f"📡 МАЯК: MEXC в сети | Баланс: ${round(total_bal, 2)} | Оффсет: {ENTRY_ORDER_OFFSET}")
            # -------------------------------
            # --- ПЕРЕКЛЮЧАТЕЛЬ СКОРОСТЕЙ (Adaptive Risk) ---
            # Если баланс выше $35 - включаем Форсаж 0.70
            # Если ниже $25 - включаем Защиту 0.40
            if total_bal > 50:
                RISK_PERCENT = 0.85
            elif total_bal < 20:
                RISK_PERCENT = 0.40
            else:
                RISK_PERCENT = BASE_RISK # Стандарт 0.55
            # -----------------------------------------------
            pos_all = exchange.fetch_positions()
            active_positions = [p for p in pos_all if float(p.get('contracts', 0)) > 0]
#=====
            if active_positions:
              for active in active_positions: # ТЕПЕРЬ ОБРАБАТЫВАЕМ ВСЕ!
                symbol, side = active['symbol'], active['side'].lower()
                size, entry_raw = float(active['contracts']), active.get('entryPrice')
                # 2. ПОЛУЧЕНИЕ ЦЕНЫ (Единственный и безопасный запрос)
                try:
                    ticker = exchange.fetch_ticker(symbol)
                except:
                    ticker = None # Защита от вылета при сетевой ошибке

                # ФИКС: Проверяем, что биржа прислала данные, а не True/False/None
                if not isinstance(ticker, dict):
                    log(f"⚠️ Биржа вернула пустой тикер для {symbol}, ждем...")
                    time.sleep(1); continue 


                price = float(ticker.get('last', 0))
                m_raw = ticker.get('markPrice')
                mark_p = float(m_raw) if m_raw is not None else price
                # ... дальше твой расчет профита ...
                if entry_raw is None or float(entry_raw) == 0 or price == 0:
                    time.sleep(5); pass #continue

#====
                entry = float(entry_raw)
                profit = (price/entry-1) if side in ['long', 'buy'] else (entry/price-1)
                m_profit = (mark_p/entry-1) if side in ['long', 'buy'] else (entry/mark_p-1)

                # --- УМНЫЙ ЧИСТИЛЬЩИК V5.9.4.4 [FINAL] ---
                position_value = (size * price) / LEVERAGE
                if full_exit_triggered and position_value < 1.0:
                    log(f"🧹 Удаление пыли {symbol}: Vol {size} (${round(position_value, 2)}).")
                    try: exchange.cancel_all_orders(symbol)
                    except: pass
                    smart_order(symbol, 'sell' if side in ['long', 'buy'] else 'buy', size, False, None, True)
                    full_exit_triggered = False; partial_fixed[symbol]  = False;  pass #continue # Вернули continue для скорости

#====
                # --- 1. РАСЧЕТ ТАЙМЕРОВ (V16.0) ---
                pos_ts = active.get('timestamp', 0)
                elapsed = (time.time() * 1000 - pos_ts) / 1000 if pos_ts > 0 else (time.time() - entry_times.get(symbol, time.time()))

                # --- 2. ЛОГИКА V16.0 [КАСКАДНЫЙ ТЕЙК + ХРАПОВИК] ---
                # Шаг 1. Ступенчатый БУ (Храповик)
                # Инициализируем уровень БУ для монеты, если его нет
                if symbol not in step_be: step_be[symbol] = -PRIMARY_SL_PCT

                if profit >= 0.0120 and step_be[symbol] < 0.0040:
                    step_be[symbol] = 0.0040
                    log(f"🛡️ Храповик {symbol}: БУ поднят до +0.4%")
                if profit >= 0.0200 and step_be[symbol] < 0.0100:
                    step_be[symbol] = 0.0100
                    log(f"🛡️ Храповик {symbol}: БУ поднят до +1.0%")

                # Шаг 2. Каскадная фиксация
                side_exit = 'sell' if side in ['long', 'buy'] else 'buy'
                
                # ТЕЙК №1 (30% от текущего объема)
                if not tp1_fixed.get(symbol, False) and profit >= TP1_PCT:
                    qty = float(exchange.amount_to_precision(symbol, size * TP1_SHARE))
                    if qty > 0 and smart_order(symbol, side_exit, qty, True, price, is_exit=True):
                        tp1_fixed[symbol] = True
                        log(f"🎯 ТЕЙК №1 (+{round(profit*100,2)}%) взят по {symbol}")
                        step_be[symbol] = 0.0015

                # ТЕЙК №2 (40% от первоначального объема -> это ~57% от остатка)
                if tp1_fixed.get(symbol, False) and not tp2_fixed.get(symbol, False) and profit >= TP2_PCT:
                    # Считаем 40% от базы через текущий размер
                    qty = float(exchange.amount_to_precision(symbol, size * 0.57)) 
                    if qty > 0 and smart_order(symbol, side_exit, qty, True, price, is_exit=True):
                        tp2_fixed[symbol] = True
                        log(f"🎯 ТЕЙК №2 (+{round(profit*100,2)}%) взят по {symbol}")

                # Определяем итоговый уровень выхода
                current_be = step_be[symbol]
#================================
                # 3. ТРИГГЕРЫ ХИРУРГА И ТАЙМ-АУТА
                # Универсальная логика:
                is_qc = any(x in symbol for x in DANGER_COINS) and elapsed > QC_TIME and profit < QC_LIMIT
#============
                # 1. Берем статус фиксации из нового словаря V16.0
                is_p_fixed = tp1_fixed.get(symbol, False)

                # 2. УМНЫЙ ХИРУРГ (Отключается после фиксации первой прибыли)
                if is_p_fixed:
                    is_surgeon = False
                else:
                    is_surgeon = elapsed > SURGEON_TIME and profit < SURGEON_PROFIT
#============
                is_time_out = elapsed > TIME_LIMIT                 # Режем через 150 мин

                log(f"📡 {symbol} | Prof: {round(profit*100, 2)}% | BE: {round(current_be*100,2)}% | Time: {int(elapsed/60)}m | Vol: {int(size)} | Баланс: ${round(total_bal, 2)} ")

                # 4. УСЛОВИЕ ВЫХОДА (V7.2.0 [ARCHITECT])
                # Добавили is_qc в список условий!
#====
                is_sl_full = profit <= -PRIMARY_SL_PCT
                
                # Если это КВИК-КАТ или жесткий СТОП-ЛОСС — выходим только МАРКЕТОМ (спасаем депо)
                if is_qc or is_sl_full:
                    use_limit_exit = False 
                else:
                    # Для Хирурга, Тейка 2, Тайм-аута или Замка — используем ЛИМИТКУ (экономим деньги)
                    use_limit_exit = True
#====

                if profit >= TP3_PCT or profit <= current_be or m_profit <= -PRIMARY_SL_PCT or is_surgeon or is_qc or is_time_out:
                    try:
                        if profit >= TP3_PCT: res = "🎯 BERSERK-TP3"
                        elif is_qc: res = f"✂️ QUICK-CUT ({symbol})" # Добавили причину
                        elif is_surgeon: res = f"⚔️ SURGEON ({round(SURGEON_PROFIT*100,2)}%)"
                        elif is_time_out: res = "⏱️ TIME-EXIT"
                        elif lock_activated[symbol]: res = "🛡️ PROFIT-LOCK (+0.15%)"
                        else: res = "🛡️ SL/BE"

                        log(f"🚨 {res} ВЫХОД: {symbol} | Profit: {round(profit*100, 2)}%")

                        # ВАЖНО: Защищаем выход от ошибок API при отмене
                        try: 
                            exchange.cancel_all_orders(symbol)
                        except: 
                            pass # Если ордеров уже нет или биржа чихнула - идем дальше на выход

#                       exchange.cancel_all_orders(symbol)
                        side_exit = 'sell' if side in ['long', 'buy'] else 'buy'

                        # Используем твой стриминг для выхода!

                        # В блоке мониторинга, перед smart_order добавь:
                        ticker = exchange.fetch_ticker(symbol)
                        cur_p = float(ticker['last']) # Гарантируем наличие цены

                        # ИСПОЛЬЗУЕМ MARKET ДЛЯ ГАРАНТИРОВАННОГО ВЫХОДА
                        # На малых балансах в режиме RECOVERY надежность важнее 0.02% комиссии
                        #smart_order(symbol, side_exit, size, is_limit=False, price=None, is_exit=True)
                        smart_order(symbol, side_exit, size, is_limit=use_limit_exit, price=cur_p, is_exit=True)

                        # АТОМАРНАЯ ОЧИСТКА ПАМЯТИ
                        just_closed[symbol] = time.time()
                        partial_fixed[symbol] = False
                        take_placed[symbol] = False
                        lock_activated[symbol] = False
                        tp1_fixed[symbol] = False
                        tp2_fixed[symbol] = False
                        step_be[symbol] = -PRIMARY_SL_PCT
                        last_stop_time = time.time()
                        time.sleep(2) 
                    except Exception as e:
                        log(f"❌ Ошибка выхода: {e}")
                        # Сбрасываем флаги, чтобы попробовать закрыться снова на следующем круге
                        partial_fixed[symbol] = False # Очищаем словарь для этой монеты
                        take_placed[symbol] = False # СБРАСЫВАЕМ ПРИ ВЫХОДЕ
                        full_exit_triggered = False
                        tp1_fixed[symbol] = False
                        tp2_fixed[symbol] = False
                        step_be[symbol] = -PRIMARY_SL_PCT
                        time.sleep(5)
                        pass #continue

              time.sleep(2);
              continue

            if time.time() - last_stop_time < 300:
                time.sleep(2);
                continue
#====
            # Если мы уже в сделке, не нужно лихорадочно опрашивать весь список
            # Просто ждем 5 секунд и идем сразу в мониторинг (ниже)
            if len(active_positions) > 0:
                time.sleep(5) 
                # Мы не делаем continue, чтобы бот ОБЯЗАТЕЛЬНО дошел до мониторинга ниже!
            else:
                # А если позиции нет — работаем на полной скорости
                pass
#====
            symbol = PRIORITY_LIST[current_idx]
            # --- УМНАЯ ЧИСТКА V8.8.5 [HYBRID-WAIT] ---
            is_in_position = any(p['symbol'] == symbol for p in active_positions)

            if not is_in_position:
                # Проверяем, как давно стоит этот капкан
                now = time.time()
                order_age = now - order_creation_time.get(symbol, 0)

                if order_age > LIMIT_ORDER_TTL:
                    try:
                        exchange.cancel_all_orders(symbol)
                        order_creation_time[symbol] = 0 # Сбрасываем после отмены
                    except: pass
            else:
                # Если мы уже в позе - сбрасываем таймер ордера на вход
                order_creation_time[symbol] = 0
            # ---------------------------------------------

            # --- УНИВЕРСАЛЬНЫЙ FUNDING SHIELD (Bybit / BingX / MEXC) ---
            try:
                f_data = exchange.fetch_funding_rate(symbol)
                # Извлекаем ставку (универсальный способ для CCXT)
                rate = float(f_data.get('fundingRate', f_data.get('rate', 0)))

                # ЛОГИРОВАНИЕ (Теперь ты видишь реальную картину в %)
                # Если rate = 0.0001, в логе будет 0.01%
                #log(f"📊 Funding {symbol}: {round(rate * 100, 4)}%")

                # ПРОВЕРКА ПОРОГА (0.0003 = 0.03%)
                if abs(rate) > 0.0003:
#                    log(f"🚫 Пропуск {symbol}: Высокий фандинг ({round(rate * 100, 2)}%)")
                    current_idx = (current_idx + 1) % len(PRIORITY_LIST)
                    continue
            except Exception as e:
                # Если биржа лагает на фандинге - просто идем дальше, не падаем
                pass 
#==
            df = pd.DataFrame(exchange.fetch_ohlcv(symbol, '1m', limit=50), columns=['t','o','h','l','c','v'])
            # ATR Filter
            if (df['h'].iloc[-1]/df['l'].iloc[-1]-1) > 0.015:
                current_idx = (current_idx+1)%len(PRIORITY_LIST); continue

            ma20, std = df['c'].rolling(20).mean().iloc[-1], df['c'].rolling(20).std().iloc[-1]
            cur_p = df['c'].iloc[-1]

            # Сигнал Боллинджера
            # --- 1. РАСЧЕТ ГРАНИЦ С ОТСТУПОМ (ENTRY_OFFSET) ---

              # --- РАСЧЕТ ГРАНИЦ И ШИРИНЫ ---
            upper_band = ma20 + (std * 2.2)
            lower_band = ma20 - (std * 2.2)
            
            # НОВАЯ СТРОКА: Считаем текущую ширину в %
            current_bandwidth = (upper_band - lower_band) / ma20 * 100
            # Мы заходим только если цена вылетела ЗА полосу еще на 0.08%
            is_sell_trigger = cur_p >= upper_band * (1 + ENTRY_TRIGGER_OFFSET)
            is_buy_trigger = cur_p <= lower_band * (1 - ENTRY_TRIGGER_OFFSET)

             # Сигнал Боллинджера с подтверждением отступа
             # ВАЖНО: Добавляем проверку ширины
            if (is_sell_trigger or is_buy_trigger):
                
                # Если рынок слишком "раздут" - пропускаем
                if current_bandwidth > MAX_BANDWIDTH:
                    log(f"🚫 Пропуск {symbol}: Ширина {round(current_bandwidth, 2)}% (Паника)")
                    current_idx = (current_idx + 1) % len(PRIORITY_LIST); continue
                
                # Если прошли фильтр - действуем
                side = 'sell' if is_sell_trigger else 'buy'

                # Фильтр Анти-Шип
                candle_size = (df['h'].iloc[-1] / df['l'].iloc[-1] - 1)
                if candle_size > MAX_CANDLE_SIZE:
                    log(f"🚫 Пропуск {symbol}: Шип {round(candle_size*100,2)}%")
                    current_idx = (current_idx + 1) % len(PRIORITY_LIST); continue

                # Расчет объема (используем динамический RISK_PERCENT)
                usable_bal = total_bal - 0.5
                raw_amt = (usable_bal * RISK_PERCENT * LEVERAGE) / cur_p
                # Умножаем на 10, так как MEXC дробит контракты ORDI/LPT в 10 раз
                if 'ORDI' in symbol or 'LPT' in symbol:
                    raw_amt = raw_amt * 10 

                order_p = upper_band * (1 + ENTRY_ORDER_OFFSET) if is_sell_trigger else lower_band * (1 - ENTRY_ORDER_OFFSET)
                # ИСПОЛЬЗУЕМ КЛАССИЧЕСКИЙ ОКРУГЛИТЕЛЬ (как был раньше)
                # Иногда amount_to_precision на MEXC глючит с мелкими монетами
                #amt = float(math.floor(raw_amt))
                # Вместо math.floor используем округление через precision биржи
                amt_str = exchange.amount_to_precision(symbol, raw_amt)
                amt = float(amt_str)
                if amt < 1 and '1000' not in symbol: amt = 1.0 # Минималка для дорогих монет

                # Входим, только если сумма ОК и у нас НЕТ других открытых позиций
                if amt >= 1 and len(active_positions) == 0:
                    log(f"🎯 ЛОВУШКА {symbol}...")
                    log(f"🎯 ЛОВУШКА {symbol} {side.upper()} (Trig: {ENTRY_TRIGGER_OFFSET*100}% | Order: {ENTRY_ORDER_OFFSET*100}%)")
                    # ОТПРАВЛЯЕМ order_p
                    res = smart_order(symbol, side, amt, True, order_p, is_exit=False)
                    if res: # Теперь res - это словарь или True, проверка пройдет
                    #if smart_order(symbol, side, amt, True, order_p, is_exit=False):
                        order_creation_time[symbol] = time.time() # ФИКСИРУЕМ ВРЕМЯ ПОСТАНОВКИ
                        partial_fixed[symbol]  = False
                        entry_times[symbol] = time.time()
                        lock_activated[symbol] = False
                        tp1_fixed[symbol] = False
                        tp2_fixed[symbol] = False
                        step_be[symbol] = -PRIMARY_SL_PCT
                else:
                    log(f"⚠️ Пропуск {symbol}: Баланс слишком мал для входа.")

            current_idx = (current_idx + 1) % len(PRIORITY_LIST); time.sleep(1.1) #оптимальный тайминг, был 5
        except Exception as e:
            if "510" in str(e): log("⏳ Rate limit! Пауза 30с..."); time.sleep(30)
            else: log(f"⚠️ Error  {e}"); time.sleep(15)

run_titan_stable()
