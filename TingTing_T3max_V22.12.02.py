from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import pandas as pd
import numpy as np
import ccxt
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
List1_0 = []
List2 = []
List3 = []


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
    if hour>8 and hour<22:
        try:
            MMbot.send_message(userid, text, disable_web_page_preview=True)
        except:
            print(text)
            time.sleep(6)
            MMbot.send_message(userid, text, disable_web_page_preview=True)

##############################################

def T3MAX_bot_send_message(userid, text):
    hour = (datetime.now().hour + 7)
    if hour>6 and hour<23:
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

def check():
  Checkbot_send_message(user_id, text=f'ok')    







##############################################
# T3MAX Module
##############################################

def a_T3max(coin_name, timeframe, vol_rate):
  price = np.zeros((22,8), dtype = float)
  try:
    binance = ccxt.binanceusdm()
    price = binance.fetch_ohlcv(coin_name,timeframe,limit=22)
  except:
    time.sleep(3)
    binance = ccxt.binanceusdm()
    price = binance.fetch_ohlcv(coin_name,timeframe,limit=22)  
  finally:
    price     = pd.DataFrame(price)
    bull_bear = price[0].astype(int)
    open      = price[1].astype(float)
    high      = price[2].astype(float)
    low       = price[3].astype(float)
    close     = price[4].astype(float)
    vol       = price[5].astype(float)
    vol_ma20  = (sum(vol) - vol[21])/21

    for position_index in range(21):
      bull_bear[position_index] = 0
      if ((min(open[position_index],close[position_index])) > (low[position_index]+(5*(high[position_index]-low[position_index])/8))):
        bull_bear[position_index] = 1
      if ((max(open[position_index],close[position_index])) < (high[position_index]-(5*(high[position_index]-low[position_index])/8))):
        bull_bear[position_index] = -1

    if ((bull_bear[20] == 1) and (vol[20] > vol_rate*vol_ma20)):
      for i in range(1, 6):
        if (bull_bear[20-i] == 1) and (max(open[20], close[20]) > min(open[20-i], close[20-i])) and (low[20] < high[20-i]):     
          T3MAX_bot_send_message(user_id, text=f'{coin_name.replace("/USDT","")} {timeframe} T3MAX BULL https://www.binance.com/vi/futures/{coin_name.replace("/","")}')

    if ((bull_bear[20] == -1) and (vol[20] > vol_rate*vol_ma20)):
      for i in range(1, 6):
        if (bull_bear[20-i] == -1) and (min(open[20], close[20]) < max(open[20-i], close[20-i])) and (high[20] > low[20-i]):     
          T3MAX_bot_send_message(user_id, text=f'{coin_name.replace("/USDT","")} {timeframe} T3MAX BEAR https://www.binance.com/vi/futures/{coin_name.replace("/","")}')


def T3MAX_1H():
  global List1
  for i in range(len(List1)):
    a_T3max(List1[i], '1h', 1.5)

def T3MAX_4H():
  global List1
  for i in range(len(List1)):
    a_T3max(List1[i], '4h', 1.5)


def T3MAX_15m():
  global List1
  for i in range(len(List1)):
    a_T3max(List1[i], '15m', 1.5)


def T3MAX_5m():
  global List1
  for i in range(len(List1)):
    a_T3max(List1[i], '5m', 1.5)
  

##############################################
# Main Functions
##############################################

def tingting():

  schedule.every().hour.at("03:26").do(T3MAX_1H)

  schedule.every().day.at("08:01").do(T3MAX_4H)
  schedule.every().day.at("12:01").do(T3MAX_4H)
  schedule.every().day.at("16:01").do(T3MAX_4H)
  schedule.every().day.at("20:01").do(T3MAX_4H)

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

