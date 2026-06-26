import ccxt
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
#           إعدادات البوت v4
# ==========================================
LEVERAGE            = 30      # الرافعة المالية
BASE_USDT           = 1.0     # حجم الصفقة (USDT)
MAX_OPEN_POSITIONS  = 5       # أقصى صفقات مفتوحة
MAX_DAILY_LOSS_PCT  = 8.0     # حد الخسارة اليومية %
MAX_HOLD_HOURS      = 4       # أقصى مدة للصفقة بالساعات

# وضع الترند (ADX > 25)
TREND_TP_PCT   = 0.010   # 1.0% TP
TREND_SL_PCT   = 0.005   # 0.5% SL  → نسبة 2:1

# وضع القناة (ADX < 20)
RANGE_TP_PCT   = 0.008   # 0.8% TP
RANGE_SL_PCT   = 0.004   # 0.4% SL  → نسبة 2:1

# حدود ADX لتحديد نوع السوق
ADX_TREND_MIN  = 25      # فوقه = سوق ترندي
ADX_RANGE_MAX  = 20      # تحته = سوق جانبي

TIMEFRAME       = '5m'
TREND_TIMEFRAME = '1h'

# ==========================================
#           200 عملة مختارة
# ==========================================
SYMBOLS = [
    # الكبار
    "BTC/USDT","ETH/USDT","BNB/USDT","SOL/USDT","XRP/USDT",
    "DOGE/USDT","ADA/USDT","AVAX/USDT","LINK/USDT","DOT/USDT",
    "LTC/USDT","BCH/USDT","UNI/USDT","ATOM/USDT","TRX/USDT",
    "ETC/USDT","XLM/USDT","APT/USDT","ARB/USDT","OP/USDT",
    # DeFi
    "AAVE/USDT","SNX/USDT","CRV/USDT","COMP/USDT","MKR/USDT",
    "YFI/USDT","SUSHI/USDT","1INCH/USDT","BAL/USDT","UMA/USDT",
    "DYDX/USDT","PERP/USDT","GMX/USDT","GNS/USDT","RDNT/USDT",
    "PENDLE/USDT","VELA/USDT","LDO/USDT","RPL/USDT","FXS/USDT",
    # Layer 1 & 2
    "NEAR/USDT","ICP/USDT","FIL/USDT","HBAR/USDT","VET/USDT",
    "ALGO/USDT","EGLD/USDT","FTM/USDT","ONE/USDT","KAVA/USDT",
    "THETA/USDT","ROSE/USDT","CFX/USDT","STX/USDT","IMX/USDT",
    "SUI/USDT","SEI/USDT","TIA/USDT","INJ/USDT","BLUR/USDT",
    "POL/USDT","QNT/USDT","ZEN/USDT","EOS/USDT","WAVES/USDT",
    "NEO/USDT","IOTA/USDT","ZEC/USDT","DASH/USDT","XMR/USDT",
    # Meme & Gaming
    "SAND/USDT","MANA/USDT","AXS/USDT","GALA/USDT","ENJ/USDT",
    "CHZ/USDT","MAGIC/USDT","IMX/USDT","GODS/USDT","ALICE/USDT",
    "1000PEPE/USDT","FLOKI/USDT","MEME/USDT","WIF/USDT","BONK/USDT",
    "SHIB/USDT","PEOPLE/USDT","LUNC/USDT","REEF/USDT","WIN/USDT",
    # Oracle & Data
    "BAND/USDT","GRT/USDT","API3/USDT","TRB/USDT","PYTH/USDT",
    # Exchange tokens
    "OKB/USDT","CRO/USDT","KCS/USDT","HT/USDT","CAKE/USDT",
    # Infrastructure
    "ANKR/USDT","NKN/USDT","STORJ/USDT","HOT/USDT","BAT/USDT",
    "ZIL/USDT","REN/USDT","KNC/USDT","LRC/USDT","ZRX/USDT",
    "CVC/USDT","MTL/USDT","IOST/USDT","OGN/USDT","SKL/USDT",
    "CTSI/USDT","DUSK/USDT","ALPHA/USDT","XVS/USDT","SFP/USDT",
    # New & Trending
    "JTO/USDT","JUP/USDT","ORDI/USDT","RNDR/USDT","BEAMX/USDT",
    "DYM/USDT","STRK/USDT","MANTA/USDT","ALT/USDT","PIXEL/USDT",
    "PORTAL/USDT","MYRO/USDT","BOME/USDT","SLERF/USDT","W/USDT",
    "TNSR/USDT","SAGA/USDT","REZ/USDT","BB/USDT","NOT/USDT",
    "IO/USDT","ZK/USDT","LISTA/USDT","ZRO/USDT","BLAST/USDT",
    "DOGS/USDT","CATI/USDT","HMSTR/USDT","EIGEN/USDT","SCR/USDT",
    "NEIRO/USDT","TURBO/USDT","ACT/USDT","PNUT/USDT","GRASS/USDT",
    "KAIA/USDT","MOVE/USDT","ME/USDT","USUAL/USDT","ACE/USDT",
    # Mid Cap
    "RUNE/USDT","TWT/USDT","BAKE/USDT","ONE/USDT","XEM/USDT",
    "STMX/USDT","SUPER/USDT","TLM/USDT","LINA/USDT","SLP/USDT",
    "SPELL/USDT","ICE/USDT","HIGH/USDT","LOKA/USDT","BETA/USDT",
    "COCOS/USDT","FARM/USDT","PORTO/USDT","SANTOS/USDT","CITY/USDT",
    "LEVER/USDT","GTC/USDT","RAD/USDT","OM/USDT","HOOK/USDT",
    "MAGIC/USDT","HFT/USDT","HIFI/USDT","ID/USDT","ARK/USDT",
    "AGLD/USDT","IDEX/USDT","CHESS/USDT","BURGER/USDT","RARE/USDT",
    "WAXP/USDT","PHA/USDT","BICO/USDT","DEGO/USDT","ATA/USDT",
    "JASMY/USDT","ORN/USDT","POLS/USDT","FORTH/USDT","AUCTION/USDT",
    "POND/USDT","WOO/USDT","FLOW/USDT","CELR/USDT","CELO/USDT",
    # Additional solid projects
    "OCEAN/USDT","FET/USDT","AGIX/USDT","NMR/USDT","ORAI/USDT",
    "SSV/USDT","ETHFI/USDT","AEVO/USDT","OMNI/USDT","REI/USDT",
    "METIS/USDT","BOBA/USDT","OMG/USDT","PROM/USDT","GLM/USDT",
    "CKB/USDT","TROY/USDT","DOCK/USDT","VIDT/USDT","ARPA/USDT",
]

# ==========================================
#           مفاتيح API
# ==========================================
API_KEY    = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
if not API_KEY or not API_SECRET:
    raise ValueError("⚠️ يرجى تعيين API_KEY و API_SECRET في ملف .env")

# ==========================================
#           الاتصال بـ Binance Futures
# ==========================================
exchange = ccxt.binanceusdm({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
    'options': {
        'adjustForTimeDifference': True,
        'recvWindow': 10000,
        'defaultType': 'future',
    },
})
exchange.load_markets()
print("✅ تم تحميل بيانات الأسواق.")

# ==========================================
#           متغيرات الحالة
# ==========================================
positions       = {}   # {symbol: {...}}
initial_balance = None
daily_loss      = 0.0
last_reset_date = datetime.now().date()
trade_log       = []
btc_cache       = {'ts': None, 'trend': None}   # كاش BTC لتقليل الطلبات


# ==========================================
#           دوال مساعدة
# ==========================================

def filter_available_symbols():
    markets   = exchange.markets
    available = [s for s in SYMBOLS if s in markets]
    # إزالة التكرار مع الحفاظ على الترتيب
    seen = set()
    unique = []
    for s in available:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    print(f"✅ أزواج متاحة في Futures: {len(unique)}/{len(SYMBOLS)}")
    return unique


def fetch_ohlcv(symbol, timeframe, limit=150):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    for c in ['open','high','low','close','volume']:
        df[c] = df[c].astype(float)
    return df


def calculate_indicators(df):
    """
    مؤشرات شاملة:
    - EMA 9/21/50 للترند
    - RSI 14
    - MACD 12/26/9
    - ATR 14 للتذبذب
    - ADX 14 لتحديد نوع السوق
    - Bollinger Bands 20 للقناة السعرية
    - حجم مقارنة بالمتوسط
    """
    df = df.copy()
    df['ema9']  = ta.ema(df['close'], length=9)
    df['ema21'] = ta.ema(df['close'], length=21)
    df['ema50'] = ta.ema(df['close'], length=50)
    df['rsi']   = ta.rsi(df['close'], length=14)
    df['atr']   = ta.atr(df['high'], df['low'], df['close'], length=14)

    # ADX
    adx_df = ta.adx(df['high'], df['low'], df['close'], length=14)
    if adx_df is not None and 'ADX_14' in adx_df.columns:
        df['adx']   = adx_df['ADX_14']
        df['dmp']   = adx_df['DMP_14']   # +DI
        df['dmn']   = adx_df['DMN_14']   # -DI
    else:
        df['adx'] = 20
        df['dmp'] = 0
        df['dmn'] = 0

    # MACD
    macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
    if macd is not None:
        df = pd.concat([df, macd], axis=1)

    # Bollinger Bands
    bb = ta.bbands(df['close'], length=20, std=2.0)
    if bb is not None:
        df = pd.concat([df, bb], axis=1)

    df['vol_ma'] = df['volume'].rolling(14).mean()
    return df.dropna()


def get_market_mode(row):
    """
    تحديد نوع السوق بناءً على ADX:
    - 'trend'  : ADX > 25  → استراتيجية الترند
    - 'range'  : ADX < 20  → استراتيجية القناة
    - 'neutral': بينهما   → انتظار
    """
    adx = row.get('adx', 20)
    if adx > ADX_TREND_MIN:
        return 'trend'
    elif adx < ADX_RANGE_MAX:
        return 'range'
    return 'neutral'


def get_btc_trend():
    """
    فلتر BTC: جلب اتجاه BTC على الساعة مع كاش 5 دقائق
    يعيد: 'up', 'down', أو 'neutral'
    """
    now = datetime.now()
    if btc_cache['ts'] and (now - btc_cache['ts']).seconds < 300:
        return btc_cache['trend']
    try:
        df = fetch_ohlcv("BTC/USDT", "1h", limit=60)
        df = calculate_indicators(df)
        r  = df.iloc[-1]
        if r['ema9'] > r['ema21'] and r['ema21'] > r['ema50']:
            trend = 'up'
        elif r['ema9'] < r['ema21'] and r['ema21'] < r['ema50']:
            trend = 'down'
        else:
            trend = 'neutral'
        btc_cache['ts']    = now
        btc_cache['trend'] = trend
        return trend
    except:
        return 'neutral'


def get_signal_trend(r, r_prev, r1h):
    """
    ====== وضع الترند ======
    شراء: EMA9>EMA21>EMA50 + MACD صاعد + RSI 40-65
          + +DI > -DI + حجم مرتفع + ساعة صاعدة
    بيع:  EMA9<EMA21<EMA50 + MACD هابط + RSI 35-60
          + -DI > +DI + حجم مرتفع + ساعة هابطة
    """
    mc  = 'MACD_12_26_9'
    mcs = 'MACDs_12_26_9'

    for col in ['ema9','ema21','ema50','rsi','dmp','dmn',
                mc, mcs,'vol_ma','volume']:
        if col not in r.index:
            return None

    rsi     = r['rsi']
    rsi_ok_long  = 40 < rsi < 65
    rsi_ok_short = 35 < rsi < 60
    rsi_rising   = rsi > r_prev['rsi']
    rsi_falling  = rsi < r_prev['rsi']
    vol_ok  = r['volume'] > r['vol_ma']
    macd_up = r[mc] > r[mcs]
    macd_dn = r[mc] < r[mcs]
    di_long  = r['dmp'] > r['dmn']
    di_short = r['dmn'] > r['dmp']

    h_up   = r1h.get('ema9',0) > r1h.get('ema21',0)
    h_down = r1h.get('ema9',0) < r1h.get('ema21',0)

    # شراء
    if (r['ema9'] > r['ema21'] > r['ema50']
            and macd_up and rsi_ok_long and rsi_rising
            and vol_ok and di_long and h_up):
        return 'buy'

    # بيع
    if (r['ema9'] < r['ema21'] < r['ema50']
            and macd_dn and rsi_ok_short and rsi_falling
            and vol_ok and di_short and h_down):
        return 'sell'

    return None


def get_signal_range(r, r_prev, df_5m):
    """
    ====== وضع القناة (Bollinger Bands + RSI) ======
    شراء: السعر يلمس الحد السفلي لـ BB
          + RSI < 35 (ذروة البيع) + RSI بدأ يرتد للأعلى
          + الشمعة أغلقت فوق الحد السفلي (تأكيد الارتداد)
    بيع:  السعر يلمس الحد العلوي لـ BB
          + RSI > 65 (ذروة الشراء) + RSI بدأ يهبط
          + الشمعة أغلقت تحت الحد العلوي (تأكيد الرفض)
    """
    bb_low  = 'BBL_20_2.0'
    bb_mid  = 'BBM_20_2.0'
    bb_high = 'BBU_20_2.0'

    for col in [bb_low, bb_mid, bb_high, 'rsi']:
        if col not in r.index:
            return None

    price      = r['close']
    rsi        = r['rsi']
    rsi_prev   = r_prev['rsi']
    bb_l       = r[bb_low]
    bb_u       = r[bb_high]
    bb_width   = (bb_u - bb_l) / r[bb_mid]  # عرض القناة النسبي

    # تجاهل القنوات الضيقة جداً (أقل من 0.5%)
    if bb_width < 0.005:
        return None

    # شراء عند الدعم
    touched_low  = r_prev['low'] <= bb_l or price <= bb_l * 1.002
    bounce_up    = price > bb_l and r['close'] > r['open']   # شمعة خضراء
    rsi_bounce   = rsi < 35 and rsi > rsi_prev               # RSI يرتد

    if touched_low and bounce_up and rsi_bounce:
        return 'buy'

    # بيع عند المقاومة
    touched_high = r_prev['high'] >= bb_u or price >= bb_u * 0.998
    reject_down  = price < bb_u and r['close'] < r['open']   # شمعة حمراء
    rsi_reject   = rsi > 65 and rsi < rsi_prev               # RSI يهبط

    if touched_high and reject_down and rsi_reject:
        return 'sell'

    return None


def get_signal(df_5m, df_1h):
    """الدالة الرئيسية لتوليد الإشارة بالوضعين"""
    if len(df_5m) < 5 or len(df_1h) < 5:
        return None, None

    r      = df_5m.iloc[-1]
    r_prev = df_5m.iloc[-2]
    r1h    = df_1h.iloc[-1]

    mode = get_market_mode(r)
    if mode == 'neutral':
        return None, None

    # فلتر BTC
    btc = get_btc_trend()

    if mode == 'trend':
        sig = get_signal_trend(r, r_prev, r1h)
        # في وضع الترند: BTC يجب ألا يكون عكس الإشارة
        if sig == 'buy'  and btc == 'down': return None, None
        if sig == 'sell' and btc == 'up':   return None, None
        return sig, 'trend'

    if mode == 'range':
        sig = get_signal_range(r, r_prev, df_5m)
        # في وضع القناة: نسمح بالدخول حتى لو BTC محايد
        if sig == 'buy'  and btc == 'down': return None, None
        if sig == 'sell' and btc == 'up':   return None, None
        return sig, 'range'

    return None, None


def get_sl_tp(symbol, price, side, atr, mode):
    """
    SL و TP ديناميكيان بناءً على ATR ونوع السوق:
    وضع الترند: ATR × 2.0 للـ SL, ATR × 4.0 للـ TP
    وضع القناة: ATR × 1.5 للـ SL, ATR × 3.0 للـ TP
    مع حدود دنيا من النسب الثابتة
    """
    if mode == 'trend':
        sl_dist = max(2.0 * atr, price * TREND_SL_PCT)
        tp_dist = max(4.0 * atr, price * TREND_TP_PCT)
    else:
        sl_dist = max(1.5 * atr, price * RANGE_SL_PCT)
        tp_dist = max(3.0 * atr, price * RANGE_TP_PCT)

    if side == 'buy':
        sl = price - sl_dist
        tp = price + tp_dist
    else:
        sl = price + sl_dist
        tp = price - tp_dist

    sl = float(exchange.price_to_precision(symbol, sl))
    tp = float(exchange.price_to_precision(symbol, tp))
    return sl, tp


def get_amount(symbol, price):
    raw = (BASE_USDT * LEVERAGE) / price
    return float(exchange.amount_to_precision(symbol, raw))


def sync_open_positions():
    """
    استرجاع الصفقات المفتوحة من Binance عند بدء التشغيل
    لضمان عدم فقدان التتبع عند إعادة التشغيل
    """
    global positions
    try:
        open_pos = exchange.fetch_positions()
        for p in open_pos:
            contracts = float(p.get('contracts', 0) or 0)
            if contracts <= 0:
                continue
            sym    = p['symbol']
            side   = 'buy' if p['side'] == 'long' else 'sell'
            entry  = float(p.get('entryPrice', 0) or 0)
            if sym not in positions and entry > 0:
                # حساب SL/TP افتراضي
                atr_approx = entry * 0.003
                sl, tp = get_sl_tp(sym, entry, side, atr_approx, 'trend')
                positions[sym] = {
                    'entry_price': entry,
                    'side':        side,
                    'amount':      contracts,
                    'tp_price':    tp,
                    'sl_price':    sl,
                    'tp_id':       None,
                    'sl_id':       None,
                    'open_time':   datetime.now(),
                    'atr':         atr_approx,
                    'mode':        'synced',
                }
                print(f"  🔄 استرجاع صفقة: {sym} {side.upper()} @ {entry}")
        if positions:
            print(f"✅ تم استرجاع {len(positions)} صفقة مفتوحة.")
    except Exception as e:
        print(f"⚠️ فشل استرجاع الصفقات: {e}")


def open_position(symbol, signal, atr, mode):
    global positions
    if len(positions) >= MAX_OPEN_POSITIONS:
        return

    try:
        price = exchange.fetch_ticker(symbol)['last']
    except Exception as e:
        print(f"  ⚠️ فشل جلب السعر {symbol}: {e}")
        return

    amount = get_amount(symbol, price)
    if amount <= 0:
        return

    try:
        exchange.set_leverage(LEVERAGE, symbol)
    except:
        pass

    try:
        exchange.create_order(symbol, 'market', signal, amount)
        entry = price
    except Exception as e:
        print(f"  ❌ فشل الدخول {symbol}: {e}")
        return

    sl, tp = get_sl_tp(symbol, entry, signal, atr, mode)
    close_side = 'sell' if signal == 'buy' else 'buy'

    mode_icon = "📈 TREND" if mode == 'trend' else "📊 RANGE"
    print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] {mode_icon} | {signal.upper()} {symbol} @ {entry:.4f}")
    print(f"   🎯 TP: {tp:.4f}  🛑 SL: {sl:.4f}  ATR: {atr:.4f}")

    # Take Profit
    tp_id = None
    try:
        o = exchange.create_order(symbol, 'limit', close_side, amount, tp,
                                  params={'reduceOnly': True, 'timeInForce': 'GTC'})
        tp_id = o.get('id')
    except Exception as e:
        print(f"  ⚠️ فشل TP: {e}")

    # Stop Loss (STOP_MARKET)
    sl_id = None
    try:
        o = exchange.create_order(symbol, 'STOP_MARKET', close_side, amount,
                                  params={'stopPrice': sl, 'reduceOnly': True,
                                          'closePosition': False})
        sl_id = o.get('id')
    except Exception as e:
        try:
            sl_lim = sl * (0.999 if signal == 'buy' else 1.001)
            sl_lim = float(exchange.price_to_precision(symbol, sl_lim))
            o = exchange.create_order(symbol, 'limit', close_side, amount, sl_lim,
                                      params={'stopPrice': sl, 'reduceOnly': True,
                                              'timeInForce': 'GTC'})
            sl_id = o.get('id')
        except Exception as e2:
            print(f"  ⚠️ فشل SL: {e2}")

    positions[symbol] = {
        'entry_price':   entry,
        'side':          signal,
        'amount':        amount,
        'tp_price':      tp,
        'sl_price':      sl,
        'tp_id':         tp_id,
        'sl_id':         sl_id,
        'open_time':     datetime.now(),
        'atr':           atr,
        'mode':          mode,
        'trailing_done': False,
    }


def manage_positions():
    """
    إدارة الصفقات:
    1. Trailing Stop عند 50% من TP
    2. إغلاق عند TP أو SL
    3. إغلاق إجباري بعد MAX_HOLD_HOURS
    """
    global positions, daily_loss, initial_balance

    for symbol in list(positions.keys()):
        pos = positions[symbol]
        try:
            price = exchange.fetch_ticker(symbol)['last']
        except:
            continue

        side  = pos['side']
        tp    = pos['tp_price']
        sl    = pos['sl_price']
        entry = pos['entry_price']
        now   = datetime.now()

        pnl = ((price-entry)/entry*100) if side=='buy' else ((entry-price)/entry*100)

        # ---- Trailing Stop عند 50% من المسافة للـ TP ----
        if not pos.get('trailing_done', False):
            half = (entry + (tp - entry) * 0.5) if side == 'buy' else (entry - (entry - tp) * 0.5)
            trail_hit = (side == 'buy' and price >= half) or (side == 'sell' and price <= half)

            if trail_hit:
                new_sl = float(exchange.price_to_precision(symbol, entry))
                if pos.get('sl_id'):
                    try: exchange.cancel_order(pos['sl_id'], symbol)
                    except: pass
                close_side = 'sell' if side == 'buy' else 'buy'
                try:
                    o = exchange.create_order(symbol, 'STOP_MARKET', close_side, pos['amount'],
                                              params={'stopPrice': new_sl, 'reduceOnly': True})
                    pos['sl_id']         = o.get('id')
                    pos['sl_price']      = new_sl
                    pos['trailing_done'] = True
                    print(f"  🔒 Trailing → {symbol} SL نقطة التعادل @ {new_sl:.4f}")
                except:
                    pos['trailing_done'] = True

        # ---- شروط الإغلاق ----
        hit_tp   = (side=='buy' and price>=tp)  or (side=='sell' and price<=tp)
        hit_sl   = (side=='buy' and price<=sl)  or (side=='sell' and price>=sl)
        timeout  = (now - pos['open_time']).total_seconds() > MAX_HOLD_HOURS * 3600

        if hit_tp or hit_sl or timeout:
            label      = "🎯 TP" if hit_tp else ("🛑 SL" if hit_sl else "⏱️ TimeOut")
            close_side = 'sell' if side == 'buy' else 'buy'

            for oid in [pos.get('tp_id'), pos.get('sl_id')]:
                if oid:
                    try: exchange.cancel_order(oid, symbol)
                    except: pass

            try:
                exchange.create_order(symbol, 'market', close_side, pos['amount'],
                                      params={'reduceOnly': True})
                mode_str = pos.get('mode','?').upper()
                print(f"{label} [{now.strftime('%H:%M:%S')}] [{mode_str}] {symbol} @ {price:.4f} | PnL: {pnl:+.2f}%")
                trade_log.append({
                    'symbol': symbol, 'side': side, 'mode': pos.get('mode'),
                    'entry': entry, 'exit': price,
                    'pnl_pct': pnl, 'result': label, 'time': now,
                })
            except Exception as e:
                print(f"  ⚠️ فشل إغلاق {symbol}: {e}")

            del positions[symbol]

            if hit_sl or (timeout and pnl < 0):
                try:
                    cur = exchange.fetch_balance()['total']['USDT']
                    loss = (initial_balance - cur) / initial_balance * 100
                    daily_loss = max(daily_loss, loss)
                except:
                    pass


def check_daily_loss():
    global initial_balance, daily_loss, last_reset_date
    today = datetime.now().date()
    if today != last_reset_date:
        last_reset_date = today
        daily_loss      = 0.0
        try:
            initial_balance = exchange.fetch_balance()['total']['USDT']
        except:
            pass
    try:
        cur  = exchange.fetch_balance()['total']['USDT']
        loss = (initial_balance - cur) / initial_balance * 100
        daily_loss = max(daily_loss, loss)
    except:
        pass

    if daily_loss > MAX_DAILY_LOSS_PCT:
        print(f"⛔ تجاوز حد الخسارة اليومي ({MAX_DAILY_LOSS_PCT}%). إيقاف البوت.")
        return False
    return True


def print_summary():
    if not trade_log:
        return
    wins   = [t for t in trade_log if t['pnl_pct'] > 0]
    losses = [t for t in trade_log if t['pnl_pct'] <= 0]
    t_wins   = [t for t in wins   if t.get('mode') == 'trend']
    r_wins   = [t for t in wins   if t.get('mode') == 'range']
    t_losses = [t for t in losses if t.get('mode') == 'trend']
    r_losses = [t for t in losses if t.get('mode') == 'range']
    total_pnl = sum(t['pnl_pct'] for t in trade_log)
    wr = len(wins) / len(trade_log) * 100

    print("\n" + "="*60)
    print(f"📊 ملخص الجلسة:")
    print(f"   إجمالي الصفقات   : {len(trade_log)}")
    print(f"   رابحة / خاسرة    : {len(wins)} / {len(losses)}")
    print(f"   نسبة الفوز        : {wr:.1f}%")
    print(f"   PnL الإجمالي      : {total_pnl:+.2f}%")
    print(f"   ── وضع الترند ──")
    print(f"   رابحة / خاسرة    : {len(t_wins)} / {len(t_losses)}")
    print(f"   ── وضع القناة ──")
    print(f"   رابحة / خاسرة    : {len(r_wins)} / {len(r_losses)}")
    print("="*60)


# ==========================================
#           الدالة الرئيسية
# ==========================================
def main():
    global initial_balance

    print("=" * 60)
    print(f"🚀 بوت التداول v4 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   رافعة       : {LEVERAGE}x")
    print(f"   وضع الترند  : TP={TREND_TP_PCT*100:.1f}%  SL={TREND_SL_PCT*100:.1f}%")
    print(f"   وضع القناة  : TP={RANGE_TP_PCT*100:.1f}%  SL={RANGE_SL_PCT*100:.1f}%")
    print(f"   ADX فلتر    : ترند>{ADX_TREND_MIN} | قناة<{ADX_RANGE_MAX}")
    print(f"   فريم        : {TIMEFRAME} + {TREND_TIMEFRAME}")
    print(f"   فلتر BTC    : ✅  |  Trailing Stop: ✅  |  Max Hold: {MAX_HOLD_HOURS}h")
    print("=" * 60)

    syms = filter_available_symbols()

    try:
        initial_balance = exchange.fetch_balance()['total']['USDT']
        print(f"💰 الرصيد الأولي: {initial_balance:.2f} USDT\n")
    except Exception as e:
        print(f"❌ فشل جلب الرصيد: {e}")
        return

    # استرجاع الصفقات المفتوحة
    sync_open_positions()

    scan = 0
    while True:
        try:
            if not check_daily_loss():
                break

            manage_positions()

            scan += 1
            try:
                cur     = exchange.fetch_balance()['total']['USDT']
                pnl_day = cur - initial_balance
                bal_str = f"رصيد: {cur:.2f} ({pnl_day:+.2f}) USDT"
            except:
                bal_str = ""

            btc_t = get_btc_trend()
            print(f"\n🔍 #{scan} | {len(positions)}/{MAX_OPEN_POSITIONS} مفتوحة | BTC:{btc_t.upper()} | {bal_str} | {datetime.now().strftime('%H:%M:%S')}")

            for symbol in syms:
                if symbol in positions:
                    continue
                if len(positions) >= MAX_OPEN_POSITIONS:
                    break

                try:
                    df_5m = fetch_ohlcv(symbol, TIMEFRAME,       limit=120)
                    df_1h = fetch_ohlcv(symbol, TREND_TIMEFRAME, limit=100)
                    df_5m = calculate_indicators(df_5m)
                    df_1h = calculate_indicators(df_1h)
                except:
                    continue

                if df_5m.empty or df_1h.empty:
                    continue

                signal, mode = get_signal(df_5m, df_1h)
                if signal and mode:
                    atr   = df_5m['atr'].iloc[-1]
                    price = df_5m['close'].iloc[-1]
                    print(f"  📊 {signal.upper()} [{mode.upper()}] {symbol} @ {price:.4f}")
                    open_position(symbol, signal, atr, mode)

            time.sleep(20)

        except KeyboardInterrupt:
            print("\n⏹️ إيقاف يدوي.")
            break
        except Exception as e:
            print(f"❌ خطأ: {e}")
            time.sleep(30)

    print_summary()


if __name__ == "__main__":
    main()
