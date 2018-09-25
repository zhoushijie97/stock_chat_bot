from iexfinance import Stock
from iexfinance import get_historical_data
from iexfinance import get_market_tops
import re
from wxpy import *
import itchat
from itchat.content import *
import datetime
import sqlite3
import matplotlib.pyplot as plt
import pandas
from iexfinance import get_historical_data
from datetime import datetime
import nltk
import sqlite3
from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer
from rasa_nlu import config
trainer = Trainer(config.load("/Users/zhoushijie/rasa_nlu/sample_configs/config_spacy.yml"))
training_data = load_data('stock.json')
interpreter = trainer.train(training_data)
#得到股票代码名(无论用户直接给出股票代码还是公司名)


def get_company_name(message):
    message = xiaoxie(message)
    company_name_pattern=re.compile('[A-Z]{3,5}')
    company_name_word = company_name_pattern.findall(message)
    if company_name_word:
        namea=''.join(company_name_word)
        if get_company_name3(namea):
            name=namea
        else  :
            if  get_company_name2(message):
                name = get_company_name2(message)[0][0]
            else:
                return "Sorry,i can't find this company for you."

    else:
        if  get_company_name2(message):
            name = get_company_name2(message)[0][0]
        else:
            return "Sorry,i can't find this company for you."
    return name
#从数据库模糊查询的到公司名对应的公司代码
def get_company_name2(msg):
    o=-1
    t="january february march april may june july august september october november december"
    msg=xiaoxie(msg)
    company_name_pattern2=re.compile("[A-Z]{1}[a-z]*")
    company_name_word = company_name_pattern2.findall(msg)
    for r in company_name_word:
        o=o+1
        if r.lower() not in t:
            company_name_word=r
            break
    p="SELECT symbol FROM stock WHERE cname LIKE '{}%'".format(company_name_word)
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    c.execute(p)
    return c.fetchall()
#避免公司名格式和股票代码相似
def get_company_name3(msg):
    p="SELECT * FROM stock WHERE symbol='{}'".format(msg)
    conn = sqlite3.connect('stocks.db')
    c = conn.cursor()
    c.execute(p)
    return c.fetchall()
#将句子开头大写转为小写
def xiaoxie(msg):
    if msg[0].isupper():
        msg=msg.replace(msg[0],msg[0].lower())
    return msg

#回答价格
responce={'price':'The price of {} today is {}'}
def respond(message):
    company_name=get_company_name(message)
    price = Stock(company_name).get_price()
    answer=responce['price'].format(company_name,price)
    return answer

def fur_intent(msg):
    if "volume" in msg.lower():
        return "get_volume"
    if "vol" in msg.lower():
        return "get_volume"
    if "cap" in msg.lower():
        return "get_market_cap"
    if "capacity" in msg.lower():
        return "get_market_cap"
    if "price" in msg.lower():
        return "get_price"
    return "Sorry,I can't obtain this for you.You can ask me something like price,volume,market capacity"

init=0
ask=1
ask_date=2
els=3
policy1={
    (init,None):(init,"You can ask me information you need about stocks!",None),
    (init,"get_something"):(ask,"Which kind of information do you want to know about this company?",None),
    (ask,"get_price"):(ask_date,"Give me the date of the information you want.",None),
    (ask,"get_volume"):(ask_date,"Give me the date of the information you want.",None),
    (ask,"get_cap"):(ask_date,"Give me the date of the information you want.",None),
    (ask_date,None):(els,"What's else do you want to know?",None),
    (els,None):(init,None),
    (els,"deny"):(init,"Ok,have fun!"),
    (init,"get_price"):(ask_date,"Give me the date of the information you want.",None),
    (init,"get_volume"):(ask_date,"Give me the date of the information you want.",None),
    (init,"get_cap"):(ask_date,"Give me the date of the information you want.",None)
}
mon={
    "January":1,
    "February":2,
    "March":3,
    "April":4,
    "May":5,
    "June":6,
    "July":7,
    "August":8,
    "September":9,
    "October":10,
    "November":11,
    "December":12
}
def find_date2(msg):
    msg=xiaoxie(msg)
    p=0
    day1 = {
        0: {'month': ''},
        1: {'month': ''}
    }
    t = "january february march april may june july august september october november december"
    y=re.compile("\d{4}")
    if y.findall(msg):
        year=y.findall(msg)
        m=re.compile("[A-Z]{1}[a-z]{2,8}")
        month=m.findall(msg)
        d=re.compile("(?<!\d)\d\d(?!\d)")
        day=d.findall(msg)
        for i in month:
            if i.lower() in t:
                day1[p]["month"]=mon[i]
                p=p+1
        if len(year) == 1:
            start = datetime(int(year[0]), int(day1[0]['month']), int(day[0]))
            end = datetime(int(year[0]), int(day1[0]['month']), int(day[0]))
        else:
            start = datetime(int(year[0]), int(day1[0]['month']), int(day[0]))
            end = datetime(int(year[1]), int(day1[1]['month']), int(day[1]))
        return start, end
    else:
        return None

yy={
    "get_volume":"volume",
    "get_price":"close",
    "get_market_cap":"wow"
}

#p0=input()
def decision(msg):
    if "yes" in msg.lower():
        return True
    if "ye" in msg.lower():
        return True
    if "sure" in msg.lower():
        return True
    if "fine" in msg.lower():
        return True
    if "ok" in msg.lower():
        return True
    if "no" or "not" in msg.lower():
        return False
    if "sorry" in msg.lower():
        return False
bot=Bot()
def chat_bot():
 @bot.register()
 def reply_msg(msg):
     data = interpreter.parse(msg.text)
     if len(data["entities"]) > 1 or "today" in msg.text:
         if "today" not in msg.text:
             start1, end1 = find_date2(msg.text)
             row=0
         if "today" in msg.text:
             row=1
     if data["intent"]["name"] == "get_something":
        stock_n = get_company_name(msg.text)
        msg.reply("Which kind of information do you want to know about this company?You can ask me something like price,volume,market capacity")
        @bot.register()
        def reply_msg(msg):
            fur_In=fur_intent(msg.text)
            if fur_In == "get_market_cap":
                msg.reply("ok,the information about the market capacity of {} is following:".format(stock_n))
                df=Stock(stock_n).get_market_cap()
                msg.reply(df)
                msg.reply("Here some updated news about {}:".format(stock_n))
                y = Stock(stock_n).get_news()
                for i in y:
                    if i['summary'] != 'No summary available.':
                        msg.reply(i['summary'])
                        msg.reply(i['url'])
                msg.reply("What else do you want to know?")
                chat_bot()
            if fur_In =="get_price":
                if len(data["entities"])>1 or "today" in msg.text:
                    if row==0 :
                        df = get_historical_data(stock_n, start=start1, end=end1, output_format='pandas')['close']
                        msg.reply("ok,the information about the price of {} is following:".format(stock_n))
                        msg.reply(df)
                        msg.reply("Do you need a chart of the data?")
                        @bot.register()
                        def reply_msg(msg):
                            if decision(msg.text) is True:
                                df.plot()
                                plt.ylabel('PRICE', fontproperties='SimHei', fontsize=14)
                                plt.xlabel(stock_n, fontproperties='SimHei', fontsize=14)
                                plt.savefig('1.png')
                                msg.reply_image('1.png')
                                msg.reply("Here some updated news about {}:".format(stock_n))
                                y = Stock(stock_n).get_news()
                                for i in y:
                                    if i['summary'] != 'No summary available.':
                                        msg.reply(i['summary'])
                                        msg.reply(i['url'])
                                msg.reply("What else do you want to know?")
                                chat_bot()
                            else:
                                msg.reply("Fine,here some updated news about {}:".format(stock_n))
                                y = Stock(stock_n).get_news()
                                for i in y:
                                    if i['summary'] != 'No summary available.':
                                        msg.reply(i['summary'])
                                        msg.reply(i['url'])
                                msg.reply("What else do you want to know?")
                                chat_bot()
                    if row==1:
                        df = Stock(stock_n).get_price
                        msg.reply("ok,the information about the price of {} is following:".format(stock_n))
                        msg.reply(df)
                        msg.reply("Here some updated news about {}:".format(stock_n))
                        y = Stock(stock_n).get_news()
                        for i in y:
                            if i['summary'] != 'No summary available.':
                                msg.reply(i['summary'])
                                msg.reply(i['url'])
                        msg.reply("What else do you want to know?")
                        chat_bot()

                if len(data["entities"]) <= 1:
                        msg.reply("When?(pattern like a period of time'from 23 October 2014 to 3 June 2017' or one day'23 October 2014')")
                        @bot.register()
                        def reply_msg(msg):
                            if "today" not in msg.text:
                                start, end = find_date2(msg.text)
                                df = get_historical_data(stock_n, start=start, end=end, output_format='pandas')["close"]
                                msg.reply("ok,the information about the price of {} is following:".format(stock_n))
                                msg.reply(df)
                                msg.reply("Do you need a chart of the data?")
                                @bot.register()
                                def reply_msg(msg):
                                    if decision(msg.text) is True:
                                        df.plot()
                                        plt.ylabel('PRICE', fontproperties='SimHei', fontsize=14)
                                        plt.xlabel(stock_n, fontproperties='SimHei', fontsize=14)
                                        plt.savefig('1.png')
                                        msg.reply_image('1.png')
                                        msg.reply("Here some updated news about {}:".format(stock_n))
                                        y = Stock(stock_n).get_news()
                                        for i in y:
                                            if i['summary'] != 'No summary available.':
                                                msg.reply(i['summary'])
                                                msg.reply(i['url'])
                                        msg.reply("What else do you want to know?")
                                        chat_bot()
                                    else:
                                        msg.reply("Fine,here some updated news about {}:".format(stock_n))
                                        y = Stock(stock_n).get_news()
                                        for i in y:
                                            if i['summary'] != 'No summary available.':
                                                msg.reply(i['summary'])
                                                msg.reply(i['url'])
                                        msg.reply("What else do you want to know?")
                                        chat_bot()
                            else:
                                df = Stock(stock_n).get_price()
                                msg.reply("ok,the information about the price of {} is following:".format(stock_n))
                                msg.reply(df)
                                msg.reply("Here some updated news about {}:".format(stock_n))
                                y = Stock(stock_n).get_news()
                                for i in y:
                                    if i['summary'] != 'No summary available.':
                                        msg.reply(i['summary'])
                                        msg.reply(i['url'])
                                msg.reply("What else do you want to know?")
                                chat_bot()
            if fur_In == "get_volume":
                if len(data["entities"]) > 1 or "today" in msg.text:
                    if row==0:
                        df = get_historical_data(stock_n, start=start1, end=end1, output_format='pandas')['volume']
                        msg.reply("ok,the information about the volume of {} is following:".format(stock_n))
                        msg.reply(df)
                        msg.reply("Do you need a chart of the data?")

                        @bot.register()
                        def reply_msg(msg):
                            if decision(msg.text) is True:
                                df.plot()
                                plt.ylabel('VOLUME', fontproperties='SimHei', fontsize=14)
                                plt.xlabel(stock_n, fontproperties='SimHei', fontsize=14)
                                plt.savefig('1.png')
                                msg.reply_image('1.png')
                                msg.reply("Here some updated news about {}:".format(stock_n))
                                y = Stock(stock_n).get_news()
                                for i in y:
                                    if i['summary'] != 'No summary available.':
                                        msg.reply(i['summary'])
                                        msg.reply(i['url'])
                                msg.reply("What else do you want to know?")
                                chat_bot()
                            else:
                                msg.reply("Fine,here some updated news about {}:".format(stock_n))
                                y = Stock(stock_n).get_news()
                                for i in y:
                                    if i['summary'] != 'No summary available.':
                                        msg.reply(i['summary'])
                                        msg.reply(i['url'])
                                msg.reply("What else do you want to know?")
                                chat_bot()
                    if row==1:
                        df = Stock(stock_n).get_volume()
                        msg.reply("ok,the information about the volume of {} is following:".format(stock_n))
                        msg.reply(df)
                        msg.reply("Here some updated news about {}:".format(stock_n))
                        y = Stock(stock_n).get_news()
                        for i in y:
                            if i['summary'] != 'No summary available.':
                                msg.reply(i['summary'])
                                msg.reply(i['url'])
                        msg.reply("What else do you want to know?")
                        chat_bot()

                if len(data["entities"]) <= 1:
                    msg.reply("When?(pattern like a period of time'from 23 October 2014 to 3 June 2017' or one day'23 October 2014')")
                    @bot.register()
                    def reply_msg(msg):
                        if "today" not in msg.text:
                            start, end = find_date2(msg.text)
                            df = get_historical_data(stock_n, start=start, end=end, output_format='pandas')['volume']
                            msg.reply("ok,the information about the volume of {} is following:".format(stock_n))
                            msg.reply(df)
                            msg.reply("Do you need a chart of the data?")

                            @bot.register()
                            def reply_msg(msg):
                                if decision(msg.text) is True:
                                    df.plot()
                                    plt.ylabel('VOLUME', fontproperties='SimHei', fontsize=14)
                                    plt.xlabel(stock_n, fontproperties='SimHei', fontsize=14)
                                    plt.savefig('1.png')
                                    msg.reply_image('1.png')
                                    msg.reply("Here some updated news about {}:".format(stock_n))
                                    y = Stock(stock_n).get_news()
                                    for i in y:
                                        if i['summary'] != 'No summary available.':
                                            msg.reply(i['summary'])
                                            msg.reply(i['url'])
                                    msg.reply("What else do you want to know?")
                                    chat_bot()
                                else:
                                    msg.reply("Fine,here some updated news about {}:".format(stock_n))
                                    y = Stock(stock_n).get_news()
                                    for i in y:
                                        if i['summary'] != 'No summary available.':
                                            msg.reply(i['summary'])
                                            msg.reply(i['url'])
                                    msg.reply("What else do you want to know?")
                                    chat_bot()
                        else:
                            df = Stock(stock_n).get_volume()
                            msg.reply("ok,the information about the volume of {} is following:".format(stock_n))
                            msg.reply(df)
                            msg.reply("Here some updated news about {}:".format(stock_n))
                            y = Stock(stock_n).get_news()
                            for i in y:
                                if i['summary'] != 'No summary available.':
                                    msg.reply(i['summary'])
                                    msg.reply(i['url'])
                            msg.reply("What else do you want to know?")
                            chat_bot()
     if data["intent"]["name"] == "get_price":
        stock_n = get_company_name(msg.text)
        if find_date2(msg.text) is None and "today" not in msg.text:
            msg.reply("When?(pattern like a periodof time'from 23 October 2014 to 3 June 2017' or one day'23 October 2014')")
            @bot.register()
            def reply_msg(msg):
                if "today" not in msg.text :
                    start,end=find_date2(msg.text)
                    df = get_historical_data(stock_n, start=start, end=end, output_format='pandas')["high"]
                else:
                    df=Stock(stock_n).get_price()
                    msg.reply("ok,the information about the price of {} is following:".format(stock_n))
                    msg.reply(df)
                    msg.reply("Here some updated news about {}:".format(stock_n))
                    y = Stock(stock_n).get_news()
                    for i in y:
                        if i['summary'] != 'No summary available.':
                            msg.reply(i['summary'])
                            msg.reply(i['url'])
                    msg.reply("What else do you want to know?")
                    chat_bot()
                msg.reply("ok,the information about the price of {} is following:".format(stock_n))
                msg.reply(df)
                msg.reply("Do you need a chart of the data?")
                @bot.register()
                def reply_msg(msg):
                    if decision(msg.text) is True:
                        df.plot()
                        plt.ylabel('PRICE', fontproperties='SimHei', fontsize=14)
                        plt.xlabel(stock_n, fontproperties='SimHei', fontsize=14)
                        plt.savefig('1.png')
                        msg.reply_image('1.png')
                        msg.reply("Here some updated news about {}:".format(stock_n))
                        y = Stock(stock_n).get_news()
                        for i in y:
                            if i['summary'] != 'No summary available.':
                                msg.reply(i['summary'])
                                msg.reply(i['url'])
                        msg.reply("What else do you want to know?")
                        chat_bot()
                    else:
                        msg.reply("Fine,here some updated news about {}:".format(stock_n))
                        y = Stock(stock_n).get_news()
                        for i in y:
                            if i['summary'] != 'No summary available.':
                                msg.reply(i['summary'])
                                msg.reply(i['url'])
                        msg.reply("What else do you want to know?")
                        chat_bot()
        if find_date2(msg.text) or "today" in msg.text:
            if "today" not in msg.text :
                start,end=find_date2(msg.text)
                df = get_historical_data(stock_n, start=start, end=end, output_format='pandas')["close"]
            else:
                df=Stock(stock_n).get_price()
                msg.reply("ok,the information about the price of {} is following:".format(stock_n))
                msg.reply(df)
                msg.reply("Here some updated news about {}:".format(stock_n))
                y = Stock(stock_n).get_news()
                for i in y:
                    if i['summary'] != 'No summary available.':
                        msg.reply(i['summary'])
                        msg.reply(i['url'])
                msg.reply("What else do you want to know?")
                chat_bot()
            msg.reply("ok,the information about the price of {} is following:".format(stock_n))
            msg.reply(df)
            msg.reply("Do you need a chart of the data?")
            @bot.register()
            def reply_msg(msg):
                if decision(msg.text) is True:
                    df.plot()
                    y = "u'{}'".format(stock_n)
                    plt.ylabel('PRICE', fontproperties='SimHei', fontsize=14)
                    plt.xlabel(stock_n, fontproperties='SimHei', fontsize=14)
                    plt.savefig('1.png')
                    msg.reply_image('1.png')
                    msg.reply("Here some updated news about {}:".format(stock_n))
                    y = Stock(stock_n).get_news()
                    for i in y:
                        if i['summary'] != 'No summary available.':
                            msg.reply(i['summary'])
                            msg.reply(i['url'])
                    msg.reply("What else do you want to know?")
                    chat_bot()
                else:
                    msg.reply("Fine,here some updated news about {}:".format(stock_n))
                    y = Stock(stock_n).get_news()
                    for i in y:
                        if i['summary'] != 'No summary available.':
                            msg.reply(i['summary'])
                            msg.reply(i['url'])
                    msg.reply("What else do you want to know?")
                    chat_bot()
     if data["intent"]["name"] == "get_volume":
        stock_n = get_company_name(msg.text)
        if find_date2(msg.text) is None and "today" not in msg.text:
            msg.reply("When?(pattern like a periodof time'from 23 October 2014 to 3 June 2017' or one day'23 October 2014')")
            @bot.register()
            def reply_msg(msg):
                if "today" not in msg.text:
                    start0, end0 = find_date2(msg.text)
                    df = get_historical_data(stock_n, start=start0, end=end0, output_format='pandas')["volume"]
                else:
                    df=Stock(stock_n).get_volume()
                    msg.reply("ok,the information about the volume of {} is following:".format(stock_n))
                    msg.reply(df)
                    msg.reply("Here some updated news about {}:".format(stock_n))
                    y = Stock(stock_n).get_news()
                    for i in y:
                        if i['summary'] != 'No summary available.':
                            msg.reply(i['summary'])
                            msg.reply(i['url'])
                    msg.reply("What else do you want to know?")
                    chat_bot()
                msg.reply("ok,the information about the volume of {} is following:".format(stock_n))
                msg.reply(df)
                msg.reply("Do you need a chart of the data?")
                @bot.register()
                def reply_msg(msg):
                    if decision(msg.text) is True:
                        df.plot()
                        plt.ylabel('VOLUME', fontproperties='SimHei', fontsize=14)
                        plt.xlabel(stock_n, fontproperties='SimHei', fontsize=14)
                        plt.savefig('1.png')
                        msg.reply_image('1.png')
                        msg.reply("Here some updated news about {}:".format(stock_n))
                        y = Stock(stock_n).get_news()
                        for i in y:
                            if i['summary'] != 'No summary available.':
                                msg.reply(i['summary'])
                                msg.reply(i['url'])
                        msg.reply("What else do you want to know?")
                        chat_bot()
                    else:
                        msg.reply("Fine,here some updated news about {}:".format(stock_n))
                        y = Stock(stock_n).get_news()
                        for i in y:
                            if i['summary'] != 'No summary available.':
                                msg.reply(i['summary'])
                                msg.reply(i['url'])
                        msg.reply("What else do you want to know?")
                        chat_bot()
        if find_date2(msg.text) or "today" in msg.text:
            if "today" not in msg.text:
                start1, end1 = find_date2(msg.text)
                df = get_historical_data(stock_n, start=start1, end=end1, output_format='pandas')["volume"]
            else:
                df = Stock(stock_n).get_volume()
                msg.reply("ok,the information about the volume of {} is following:".format(stock_n))
                msg.reply(df)
                msg.reply("Here some updated news about {}:".format(stock_n))
                y = Stock(stock_n).get_news()
                for i in y:
                    if i['summary'] != 'No summary available.':
                        msg.reply(i['summary'])
                        msg.reply(i['url'])
                msg.reply("What else do you want to know?")
                chat_bot()
            msg.reply("ok,the information about the volume of {} is following:".format(stock_n))
            msg.reply(df)
            msg.reply("Do you need a chart of the data?")
            @bot.register()
            def reply_msg(msg):
                if decision(msg.text) is True:
                    df.plot()
                    plt.ylabel('VOLUME',fontproperties='SimHei',fontsize=14)
                    plt.xlabel(stock_n, fontproperties='SimHei', fontsize=14)
                    plt.savefig('1.png')
                    msg.reply_image('1.png')
                    msg.reply("Here some updated news about {}:".format(stock_n))
                    y = Stock(stock_n).get_news()
                    for i in y:
                        if i['summary'] != 'No summary available.':
                            msg.reply(i['summary'])
                            msg.reply(i['url'])
                    msg.reply("What else do you want to know?")
                    chat_bot()
                else:
                    msg.reply("Fine,here some updated news about {}:".format(stock_n))
                    y = Stock(stock_n).get_news()
                    for i in y:
                        if i['summary'] != 'No summary available.':
                            msg.reply(i['summary'])
                            msg.reply(i['url'])
                    msg.reply("What else do you want to know?")
                    chat_bot()
 embed()
chat_bot()