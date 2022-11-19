# sửa l,u thành đóng nến (done)
# thêm cảnh cáo giá độ trễ 5p
# loại bỏ vài coin khác (done busd)
# fix lỗi nhảy liên tục
# tắt thông báo sau 22h (done)

# add t3max

from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import pandas as pd
import numpy as np
import ccxt
import talib
import time
import datetime
from datetime import datetime
import schedule
import threading

##############################################
# GLOBAL VARIABLE
##############################################

moneymoney_bot_id = '5159271179:AAFe1TqRfmU6dq470k2MrNBOMYCK9vML4zs'
tingting_bot_id   = '5284937344:AAEv54J0PMS8yPR0XtoxXyRe2qWrev5v-zg'
T3MAX_bot_id      = '5780761968:AAHItVeyA0sW9N6t30PWfSSwOjX4Qf2KKeI'
check_bot_id      = '5113753168:AAHckXoT8crDW9oNBT1nrV1wLOh62EuhHqs'

updater = Updater(tingting_bot_id)
TTbot = Bot(tingting_bot_id)
MMbot = Bot(moneymoney_bot_id)
T3MAXbot = Bot(T3MAX_bot_id)
Checkbot = Bot(check_bot_id)
user_id = 1944995901

#input:
List1 = []
List1_0 = ['SOL/USDT','AVAX/USDT',
           'LUNA/USDT','RSR/USDT','DOGE/USDT','JASMY/USDT','VET/USDT','LINA/USDT','XRP/USDT','STMX/USDT','1000SHIB/USDT','HOT/USDT']

#Đã chạm 2 đầu:
List2 = []
List2_0 = []  # Đã chạm BB Middle
#Đã chạm giữa -> đọc nến
List3 = []


X = np.zeros((268,6), dtype = int)

####################### Vol Filter #######################

MINIMUM_VOL = 66  # M.USDT

binance = ccxt.binanceusdm()  # Connect binance usdt-m
binance.load_markets()
all_coin_list=list(binance.markets.keys())

def filter_vol(coin_name):
  price = np.zeros((32,6), dtype = float)
  try:
    binance = ccxt.binanceusdm()
    price = binance.fetch_ohlcv(coin_name,'1d',limit=3)
    price = pd.DataFrame(price)
    close = price[4].astype(float)
    coin_vol  = price[5].astype(float)
    usdt_vol  = coin_vol[1]*close[2]/1000000     # Unit: Million USDT
    if usdt_vol >= MINIMUM_VOL :
      List1.append(coin_name)
  except:
    print(coin_name)
        
for i in range(len(all_coin_list)):
    filter_vol(all_coin_list[i])

for c in List1:
  if 'BUSD' in c:
    List1_0.append(c)
  if '_' in c:
    List1_0.append(c)    

for i in range(len(List1_0)):
    if List1.count(List1_0[i])==1:  
        List1.remove(List1_0[i])

##############################################

def TTbot_send_message(userid, text):
  try:
    TTbot.send_message(userid, text, disable_web_page_preview=True)
  except:
    print(text)
    time.sleep(6)
    TTbot.send_message(userid, text, disable_web_page_preview=True)


##############################################

def MMbot_send_message(userid, text):
    hour = (datetime.now().hour + 7)
    if hour<25:
        try:
            MMbot.send_message(userid, text, disable_web_page_preview=True)
        except:
            print(text)
            time.sleep(6)
            MMbot.send_message(userid, text, disable_web_page_preview=True)

##############################################

def T3MAX_bot_send_message(userid, text):
    hour = (datetime.now().hour + 7)
#    if hour>6 and hour<22:
    if hour<25:
        try:
            T3MAXbot.send_message(userid, text, disable_web_page_preview=True)
        except:
            print(text)
            time.sleep(6)
            T3MAXbot.send_message(userid, text, disable_web_page_preview=True)


##############################################

def Checkbot_send_message(userid, text):
  try:
    Checkbot.send_message(userid, text, disable_web_page_preview=True)
  except:
    print(text)
    time.sleep(6)
    Checkbot.send_message(userid, text, disable_web_page_preview=True)


##############################################
# PRE LONG SHORT MODULE
##############################################

def load_data(coin_name, timeframe):
  price = np.zeros((32,6), dtype = float)
  try:
    binance = ccxt.binanceusdm()
    price = binance.fetch_ohlcv(coin_name,timeframe,limit=28)
  except:
    time.sleep(3)
    binance = ccxt.binanceusdm()
    price = binance.fetch_ohlcv(coin_name,timeframe,limit=28)  
  finally:  
    price = pd.DataFrame(price)
    open  = price[1].astype(float)
    high  = price[2].astype(float)
    low   = price[3].astype(float)
    close = price[4].astype(float)
    bollinger_upper, bollinger_middle, bollinger_lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
    ATR = talib.ATR(high, low, close, timeperiod=12)
    return open[26], high[26], low[26], close[26], bollinger_upper[26], bollinger_middle[26], bollinger_lower[26], ATR[26]


##############################################

def touch_bollinger_band(coin_name,timeframe):
    open, high, low, close, bollinger_upper, bollinger_middle, bollinger_lower, atr = load_data(coin_name,timeframe)

    if max(open,close) > (bollinger_upper - atr/3):
        a=1
    else:
        a=0
    if min(open,close) < (bollinger_lower + atr/3):
        l=1
    else:
        l=0
    return a,l


##############################################

def setup(coin_name, timeframe, n):
    a,l = touch_bollinger_band(coin_name, timeframe)
    global X
    global List2

    if l==1:
        X[n,0]=1
        X[n,1]=1
    else: 
        X[n,1] = X[n,1] + 1
    if a==1 and X[n,0]==1 and X[n,1] <=8:
        List2.append(coin_name)
        #update.message.reply_text(f'PRE LONG {coin_name}')
        X[n,0]=0

    if a==1:
        X[n,2]=1
        X[n,3]=1
    else:
        X[n,3] = X[n,3] + 1
    if l==1 and X[n,2]==1 and X[n,3] <=8:
        List2.append(coin_name)
        #update.message.reply_text(f'PRE SHORT {coin_name}')
        X[n,2]=0
     
        
##############################################

def Pre_longshort():
  global List1
  for i in range(len(List1)):
    setup(List1[i], '15m', i)


##############################################
# Touch_Middle Module
##############################################

def load_dataT_M(coin_name, timeframe):
  price = np.zeros((32,6), dtype = float)
  price_1m = np.zeros((32,6), dtype = float)
  try:
    binance = ccxt.binanceusdm()  # Connect binance
    price = binance.fetch_ohlcv(coin_name, timeframe, limit=28)
    price_1m = binance.fetch_ohlcv(coin_name,'1m',limit=8)
  except:
    time.sleep(3)
    binance = ccxt.binanceusdm()  # Connect binance
    price = binance.fetch_ohlcv(coin_name, timeframe, limit=28)  
    price_1m = binance.fetch_ohlcv(coin_name,'1m',limit=8)  
  finally:
    price = pd.DataFrame(price)
    high  = price[2].astype(float)
    low   = price[3].astype(float)
    close = price[4].astype(float)
    bollinger_upper, bollinger_middle, bollinger_lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
    ATR = talib.ATR(high, low, close, timeperiod=12)

    price_1m = pd.DataFrame(price_1m)
    high_1m  = price_1m[2].astype(float)
    low_1m   = price_1m[3].astype(float)

    return bollinger_middle[26+1], high_1m[6], low_1m[6], ATR[26]


##############################################

def touch_bollinger_middle(coin_name, timeframe):
  global List2_0
  bollinger_middle, high_1m, low_1m, atr = load_dataT_M(coin_name, timeframe)
  if ((low_1m - atr/3) < bollinger_middle) and ((high_1m  + atr/3) > bollinger_middle):
    MMbot_send_message(user_id, text=f'{coin_name.replace("/USDT","")} https://www.binance.com/vi/futures/{coin_name.replace("/","")}')
    List2_0.append(coin_name)


##############################################

def Touch_middle():
  global List2
  global List2_0
  for i in range(len(List2)):
    touch_bollinger_middle(List2[i], '15m')
  for i in range(len(List2_0)):
    List2.remove(List2_0[i])
  List2_0.clear()






        
        
##############################################
# Candlestick Module
##############################################

candle_rankings = {
        "CDL3LINESTRIKE_Bull": 1,
        "CDL3LINESTRIKE_Bear": 2,
        "CDL3BLACKCROWS_Bull": 3,
        "CDL3BLACKCROWS_Bear": 3,
        "CDLEVENINGSTAR_Bull": 4,
        "CDLEVENINGSTAR_Bear": 4,
        "CDLTASUKIGAP_Bull": 5,
        "CDLTASUKIGAP_Bear": 5,
        "CDLINVERTEDHAMMER_Bull": 6,
        "CDLINVERTEDHAMMER_Bear": 6,
        "CDLMATCHINGLOW_Bull": 7,
        "CDLMATCHINGLOW_Bear": 7,
        "CDLABANDONEDBABY_Bull": 8,
        "CDLABANDONEDBABY_Bear": 8,
        "CDLBREAKAWAY_Bull": 10,
        "CDLBREAKAWAY_Bear": 10,
        "CDLMORNINGSTAR_Bull": 12,
        "CDLMORNINGSTAR_Bear": 12,
        "CDLPIERCING_Bull": 13,
        "CDLPIERCING_Bear": 13,
        "CDLSTICKSANDWICH_Bull": 14,
        "CDLSTICKSANDWICH_Bear": 14,
        "CDLTHRUSTING_Bull": 15,
        "CDLTHRUSTING_Bear": 15,
        "CDLINNECK_Bull": 17,
        "CDLINNECK_Bear": 17,
        "CDL3INSIDE_Bull": 20,
        "CDL3INSIDE_Bear": 56,
        "CDLHOMINGPIGEON_Bull": 21,
        "CDLHOMINGPIGEON_Bear": 21,
        "CDLDARKCLOUDCOVER_Bull": 22,
        "CDLDARKCLOUDCOVER_Bear": 22,
        "CDLIDENTICAL3CROWS_Bull": 24,
        "CDLIDENTICAL3CROWS_Bear": 24,
        "CDLMORNINGDOJISTAR_Bull": 25,
        "CDLMORNINGDOJISTAR_Bear": 25,
        "CDLXSIDEGAP3METHODS_Bull": 27,
        "CDLXSIDEGAP3METHODS_Bear": 26,
        "CDLTRISTAR_Bull": 28,
        "CDLTRISTAR_Bear": 76,
        "CDLGAPSIDESIDEWHITE_Bull": 46,
        "CDLGAPSIDESIDEWHITE_Bear": 29,
        "CDLEVENINGDOJISTAR_Bull": 30,
        "CDLEVENINGDOJISTAR_Bear": 30,
        "CDL3WHITESOLDIERS_Bull": 32,
        "CDL3WHITESOLDIERS_Bear": 32,
        "CDLONNECK_Bull": 33,
        "CDLONNECK_Bear": 33,
        "CDL3OUTSIDE_Bull": 34,
        "CDL3OUTSIDE_Bear": 39,
        "CDLRICKSHAWMAN_Bull": 35,
        "CDLRICKSHAWMAN_Bear": 35,
        "CDLSEPARATINGLINES_Bull": 36,
        "CDLSEPARATINGLINES_Bear": 40,
        "CDLLONGLEGGEDDOJI_Bull": 37,
        "CDLLONGLEGGEDDOJI_Bear": 37,
        "CDLHARAMI_Bull": 38,
        "CDLHARAMI_Bear": 72,
        "CDLLADDERBOTTOM_Bull": 41,
        "CDLLADDERBOTTOM_Bear": 41,
        "CDLCLOSINGMARUBOZU_Bull": 70,
        "CDLCLOSINGMARUBOZU_Bear": 43,
        "CDLTAKURI_Bull": 47,
        "CDLTAKURI_Bear": 47,
        "CDLDOJISTAR_Bull": 49,
        "CDLDOJISTAR_Bear": 51,
        "CDLHARAMICROSS_Bull": 50,
        "CDLHARAMICROSS_Bear": 80,
        "CDLADVANCEBLOCK_Bull": 54,
        "CDLADVANCEBLOCK_Bear": 54,
        "CDLSHOOTINGSTAR_Bull": 55,
        "CDLSHOOTINGSTAR_Bear": 55,
        "CDLMARUBOZU_Bull": 71,
        "CDLMARUBOZU_Bear": 57,
        "CDLUNIQUE3RIVER_Bull": 60,
        "CDLUNIQUE3RIVER_Bear": 60,
        "CDL2CROWS_Bull": 61,
        "CDL2CROWS_Bear": 61,
        "CDLBELTHOLD_Bull": 62,
        "CDLBELTHOLD_Bear": 63,
        "CDLHAMMER_Bull": 65,
        "CDLHAMMER_Bear": 65,
        "CDLHIGHWAVE_Bull": 67,
        "CDLHIGHWAVE_Bear": 67,
        "CDLSPINNINGTOP_Bull": 69,
        "CDLSPINNINGTOP_Bear": 73,
        "CDLUPSIDEGAP2CROWS_Bull": 74,
        "CDLUPSIDEGAP2CROWS_Bear": 74,
        "CDLGRAVESTONEDOJI_Bull": 77,
        "CDLGRAVESTONEDOJI_Bear": 77,
        "CDLHIKKAKEMOD_Bull": 82,
        "CDLHIKKAKEMOD_Bear": 81,
        "CDLHIKKAKE_Bull": 85,
        "CDLHIKKAKE_Bear": 83,
        "CDLENGULFING_Bull": 84,
        "CDLENGULFING_Bear": 91,
        "CDLMATHOLD_Bull": 86,
        "CDLMATHOLD_Bear": 86,
        "CDLHANGINGMAN_Bull": 87,
        "CDLHANGINGMAN_Bear": 87,
        "CDLRISEFALL3METHODS_Bull": 94,
        "CDLRISEFALL3METHODS_Bear": 89,
        "CDLKICKING_Bull": 96,
        "CDLKICKING_Bear": 102,
        "CDLDRAGONFLYDOJI_Bull": 98,
        "CDLDRAGONFLYDOJI_Bear": 98,
        "CDLCONCEALBABYSWALL_Bull": 101,
        "CDLCONCEALBABYSWALL_Bear": 101,
        "CDL3STARSINSOUTH_Bull": 103,
        "CDL3STARSINSOUTH_Bear": 103,
        "CDLDOJI_Bull": 104,
        "CDLDOJI_Bear": 104
    }

from itertools import compress


##############################################

def recognize_candlestick(df):
    """
    Recognizes candlestick patterns and appends 2 additional columns to df;
    1st - Best Performance candlestick pattern matched by www.thepatternsite.com
    2nd - # of matched patterns
    """

    op = df[1].astype(float)
    hi = df[2].astype(float)
    lo = df[3].astype(float)
    cl = df[4].astype(float)

    candle_names = talib.get_function_groups()['Pattern Recognition']

    # patterns not found in the patternsite.com
    exclude_items = ('CDLCOUNTERATTACK',
                     'CDLLONGLINE',
                     'CDLSHORTLINE',
                     'CDLSTALLEDPATTERN',                
                     )

    candle_names = [candle for candle in candle_names if candle not in exclude_items]

    # create columns for each candle
    for candle in candle_names:
        # below is same as;
        # df["CDL3LINESTRIKE"] = talib.CDL3LINESTRIKE(op, hi, lo, cl)
        df[candle] = getattr(talib, candle)(op, hi, lo, cl)

    df['candlestick_pattern'] = np.nan
    df['candlestick_match_count'] = np.nan
        
    for index, row in df.iterrows():

        # no pattern found
        if len(row[candle_names]) - sum(row[candle_names] == 0) == 0:
            df.loc[index,'candlestick_pattern'] = "NO_PATTERN"
            df.loc[index, 'candlestick_match_count'] = 0
        # single pattern found
        elif len(row[candle_names]) - sum(row[candle_names] == 0) == 1:
            # bull pattern 100 or 200
            if any(row[candle_names].values > 0):
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bull'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1
            # bear pattern -100 or -200
            else:
                pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bear'
                df.loc[index, 'candlestick_pattern'] = pattern
                df.loc[index, 'candlestick_match_count'] = 1
        # multiple patterns matched -- select best performance
        else:
            # filter out pattern names from bool list of values
            patterns = list(compress(row[candle_names].keys(), row[candle_names].values != 0))
            container = []
            for pattern in patterns:
                if row[pattern] > 0:
                    container.append(pattern + '_Bull')
                else:
                    container.append(pattern + '_Bear')
            rank_list = [candle_rankings[p] for p in container]
            if len(rank_list) == len(container):
                rank_index_best = rank_list.index(min(rank_list))
                df.loc[index, 'candlestick_pattern'] = container[rank_index_best]
                df.loc[index, 'candlestick_match_count'] = len(container)
    # clean up candle columns
    cols_to_drop = candle_names
    df.drop(cols_to_drop, axis = 1, inplace = True)
    return df


##############################################

def Candlestick(coin_name, timeframe):
    price = np.zeros((32,6), dtype = float)
    try: 
        binance = ccxt.binanceusdm()  # Connect binance
        price = binance.fetch_ohlcv(coin_name, timeframe,limit=28)   # Download data
    except:
        time.sleep(3)
        binance = ccxt.binanceusdm()  # Connect binance
        price = binance.fetch_ohlcv(coin_name, timeframe,limit=28)   # Download data
    finally:
        price = pd.DataFrame(price)
        df = price

        recognize_candlestick(df)
        df = np.array(df)

        TTbot_send_message(user_id, text=f'{coin_name} {timeframe} {df[27,4]}\n{df[27,6]} {df[27,7]}')
        
##############################################

def Candlestick_5m():
  global List3
  for i in range(len(List3)):
    Candlestick(List3[i], '5m')


##############################################

def Candlestick_15m():
  global List3
  for i in range(len(List3)):
    Candlestick(List3[i], '15m')

##############################################

def check():
  Checkbot_send_message(user_id, text=f'List2: '+str(List2))    







##############################################
# T3MAX Module
##############################################

def long_beard_candle_bull(position_index, coin_name, timeframe):
  price = np.zeros((16,6), dtype = float)
  try:
    binance = ccxt.binanceusdm()
    price = binance.fetch_ohlcv(coin_name,timeframe,limit=8)
  except:
    time.sleep(3)
    binance = ccxt.binanceusdm()
    price = binance.fetch_ohlcv(coin_name,timeframe,limit=8)  
  finally:
    price = pd.DataFrame(price)
    open  = price[1].astype(float)
    high  = price[2].astype(float)
    low   = price[3].astype(float)
    close = price[4].astype(float)

    if ((min(open[position_index],low[position_index])) > (low[position_index]+(5*(high[position_index]-low[position_index])/8))):
      return 1
    else:
      return 0

def long_beard_candle_bear(position_index, coin_name, timeframe):
  price = np.zeros((16,6), dtype = float)
  try:
    binance = ccxt.binanceusdm()
    price = binance.fetch_ohlcv(coin_name,timeframe,limit=8)
  except:
    time.sleep(3)
    binance = ccxt.binanceusdm()
    price = binance.fetch_ohlcv(coin_name,timeframe,limit=8)  
  finally:
    price = pd.DataFrame(price)
    open  = price[1].astype(float)
    high  = price[2].astype(float)
    low   = price[3].astype(float)
    close = price[4].astype(float)

    if ((max(open[position_index],low[position_index])) < (high[position_index]-(5*(high[position_index]-low[position_index])/8))):
      return 1
    else:
      return 0

  


def AT3MAX(coin_name, timeframe):                            #...h 01 phút
  if (long_beard_candle_bull(6, coin_name, timeframe)):
    if (long_beard_candle_bull(5, coin_name, timeframe)|long_beard_candle_bull(4, coin_name, timeframe)|long_beard_candle_bull(3, coin_name, timeframe)|long_beard_candle_bull(2, coin_name, timeframe)):
      T3MAX_bot_send_message(user_id, text=f'{coin_name.replace("/USDT","")} {timeframe} T3MAX BULL https://www.binance.com/vi/futures/{coin_name.replace("/","")}')

  if (long_beard_candle_bear(6, coin_name, timeframe)):
    if (long_beard_candle_bear(5, coin_name, timeframe)|long_beard_candle_bear(4, coin_name, timeframe)|long_beard_candle_bear(3, coin_name, timeframe)|long_beard_candle_bear(2, coin_name, timeframe)):
      T3MAX_bot_send_message(user_id, text=f'{coin_name.replace("/USDT","")} {timeframe} T3MAX BEAR https://www.binance.com/vi/futures/{coin_name.replace("/","")}')


def T3MAX_1H():
  global List1
  for i in range(len(List1)):
    AT3MAX(List1[i], '1h')

def T3MAX_4H():
  global List1
  for i in range(len(List1)):
    AT3MAX(List1[i], '4h')

def T3MAX_5m():
  global List2
  for i in range(len(List2)):
    AT3MAX(List1[i], '5m')

def T3MAX_15m():
  global List2
  for i in range(len(List2)):
    AT3MAX(List1[i], '15m')


##############################################
# Main Functions
##############################################

def tingting():
  #Pre_longshort every hour at 00,15,30,45 minute 23s
  schedule.every().hour.at("00:23").do(Pre_longshort)
  schedule.every().hour.at("15:23").do(Pre_longshort)
  schedule.every().hour.at("30:23").do(Pre_longshort)
  schedule.every().hour.at("45:23").do(Pre_longshort)

  #Touch_middle every minute at 05s
  schedule.every().minute.at(":16").do(Touch_middle)






  schedule.every().hour.at("03:26").do(T3MAX_1H)

  schedule.every().day.at("07:01").do(T3MAX_4H)
  schedule.every().day.at("11:01").do(T3MAX_4H)
  schedule.every().day.at("15:01").do(T3MAX_4H)
  schedule.every().day.at("19:01").do(T3MAX_4H)

  schedule.every().hour.at("00:05").do(T3MAX_5m)
  schedule.every().hour.at("05:05").do(T3MAX_5m)
  schedule.every().hour.at("10:05").do(T3MAX_5m)
  schedule.every().hour.at("15:05").do(T3MAX_5m)
  schedule.every().hour.at("20:05").do(T3MAX_5m)
  schedule.every().hour.at("25:05").do(T3MAX_5m)
  schedule.every().hour.at("30:05").do(T3MAX_5m)
  schedule.every().hour.at("35:05").do(T3MAX_5m)
  schedule.every().hour.at("40:05").do(T3MAX_5m)
  schedule.every().hour.at("45:05").do(T3MAX_5m)
  schedule.every().hour.at("50:05").do(T3MAX_5m)
  schedule.every().hour.at("55:05").do(T3MAX_5m)

  schedule.every().hour.at("00:30").do(T3MAX_15m)
  schedule.every().hour.at("15:30").do(T3MAX_15m)
  schedule.every().hour.at("30:30").do(T3MAX_15m)
  schedule.every().hour.at("45:30").do(T3MAX_15m)





  #Candlestick_5m every hour at
  schedule.every().hour.at("59:55").do(Candlestick_5m)
  schedule.every().hour.at("04:55").do(Candlestick_5m)
  schedule.every().hour.at("09:55").do(Candlestick_5m)
  schedule.every().hour.at("14:55").do(Candlestick_5m)
  schedule.every().hour.at("19:55").do(Candlestick_5m)
  schedule.every().hour.at("24:55").do(Candlestick_5m)
  schedule.every().hour.at("29:55").do(Candlestick_5m)
  schedule.every().hour.at("34:55").do(Candlestick_5m)
  schedule.every().hour.at("39:55").do(Candlestick_5m)
  schedule.every().hour.at("44:55").do(Candlestick_5m)
  schedule.every().hour.at("49:55").do(Candlestick_5m)
  schedule.every().hour.at("54:55").do(Candlestick_5m)

  #Candlestick_15m every hour at 00,15,30,45minute 02s
  schedule.every().hour.at("59:50").do(Candlestick_15m)
  schedule.every().hour.at("14:50").do(Candlestick_15m)
  schedule.every().hour.at("29:50").do(Candlestick_15m)
  schedule.every().hour.at("44:50").do(Candlestick_15m)

  #check
  schedule.every(15).minutes.do(check)

  while 1:
    schedule.run_pending()
    time.sleep(1)


##############################################

def add_remove(update: Update, context: CallbackContext) -> None:
  global List1
  global List2
  global List3

  mess = str(update.message.text)
  if mess.count(' ', 0, len(mess))==2: # check syntax
    str1,str2,str3 = mess.split(" ")   # form: "Add 1 btc"
    str3 = str3.upper() + '/USDT'
    if all_coin_list.count(str3)==0:   # check do binance support?
      TTbot_send_message(user_id, text=f"Binance USDT-M does't have "+ str3)
    else:
      if str1 == 'Add':
        if str2 == '1':
          if List1.count(str3)==0:
            List1.append(str3)
          TTbot_send_message(user_id, text=f'List1: '+str(List1))
        if str2 == '2':
          if List2.count(str3)==0:
            List2.append(str3)
          TTbot_send_message(user_id, text=f'List2: '+str(List2))
        if str2 == '3':
          if List3.count(str3)==0:
            List3.append(str3)
          TTbot_send_message(user_id, text=f'List3: '+str(List3))
      if str1 == 'Remove':
        if str2 == '1':
          if List1.count(str3)==1:
            List1.remove(str3)
          TTbot_send_message(user_id, text=f'List1: '+str(List1))
        if str2 == '2':
          if List2.count(str3)==1:
            List2.remove(str3)
          TTbot_send_message(user_id, text=f'List2: '+str(List2))
        if str2 == '3':
          if List3.count(str3)==1:
            List3.remove(str3)
          TTbot_send_message(user_id, text=f'List3: '+str(List3))
  else:
    TTbot_send_message(user_id, text=f'Resend according to form: "Add 3 btc"')

    
##############################################

def show_list(update: Update, context: CallbackContext) -> None:
  global List1
  global List2
  global List3
  mess = str(update.message.text)
  if mess == 'List1':
    TTbot_send_message(user_id, text=f'List1: '+str(List1))
  if mess == 'List2':
    TTbot_send_message(user_id, text=f'List2: '+str(List2))
  if mess == 'List3':
    TTbot_send_message(user_id, text=f'List3: '+str(List3))

##############################################

def TingTing():
  Checkbot_send_message(user_id, text=f'GOODLUCK, SIR')

##############################################

TingTing()
thread1 = threading.Thread(target= tingting, args=())
thread1.start()

updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'Add') | Filters.regex(r'Remove'), add_remove))
updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'List'), show_list))
updater.start_polling()
updater.idle()