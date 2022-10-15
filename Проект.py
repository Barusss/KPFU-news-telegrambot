import requests
from lxml import etree
import lxml.html
import telebot
from telebot import types
import urllib
import os
import re


def parse(pg_num):
    api = requests.get('https://students.kpfu.ru/news')
    tree = lxml.html.document_fromstring(api.text)
    title_of_news = tree.xpath(f'//*[@id="block-kpfu2-content"]/div/div/div[{pg_num}]/span/div/a/text()')
    news =  tree.xpath(f'//*[@id="block-kpfu2-content"]/div/div/div[{pg_num}]/div[3]/div')[0]
    text_of_news = "".join([el for el in list(news.itertext())])
    
    
    return f'  __{title_of_news[0]}__ \n\n {text_of_news}'
       
def parse_img(pg_num):
    api = requests.get('https://students.kpfu.ru/news')
    tree = lxml.html.document_fromstring(api.text)
    src = tree.xpath(f'//*[@id="block-kpfu2-content"]/div/div/div[{pg_num}]/div[2]/div/img/@src')
    return 'https://students.kpfu.ru' + src[0]

def print_news(message,pg_num):
    url = parse_img(pg_num)
    keyboard = types.InlineKeyboardMarkup()
    button_to_watch_more = types.InlineKeyboardButton(text="Узанть больще", callback_data=str(pg_num))
    keyboard.add(button_to_watch_more)
    img = open('out.jpg','wb')
    img.write(urllib.request.urlopen(url).read())
    img.close()
    img = open('out.jpg', 'rb')
    bot.send_photo(message.chat.id, img, caption = parse(pg_num), parse_mode= 'Markdown', reply_markup = keyboard)
    img.close()
    os.remove('out.jpg')
    
    
def print_more_about(message,pg_num):
    api = requests.get('https://students.kpfu.ru/news')
    tree = lxml.html.document_fromstring(api.text)
    href = tree.xpath(f'//*[@id="block-kpfu2-content"]/div/div/div[{pg_num}]/span/div/a/@href')
    api = requests.get(f'https://students.kpfu.ru{href[0]}')
    tree = lxml.html.document_fromstring(api.text)
    title = tree.xpath('//*[@id="block-kpfu2-page-title"]')[0]
    title_text = list(title.itertext())
    content = tree.xpath('//*[@id="block-kpfu2-content"]/article/div/div[1]')[0]
    content_text = "".join([list(content.itertext())[i] for i in range(len(list(content.itertext()))//3 )])
    bot.send_message(message.chat.id, text = f'{title_text[1]} \n\n {content_text}')
    content_text = "".join([list(content.itertext())[i + len(list(content.itertext()))//3] for i in range(len(list(content.itertext()))//3) ])
    bot.send_message(message.chat.id, text = content_text)
    content_text = "".join([list(content.itertext())[i + 2*(len(list(content.itertext()))//3)] for i in range(len(list(content.itertext()))//3 + len(list(content.itertext()))%3) ])
    bot.send_message(message.chat.id, text = content_text)
    
    


token = "Your token"
bot = telebot.TeleBot(token)
@bot.message_handler(commands=['start'])
def start (message, res=False):
    keyboard = types.InlineKeyboardMarkup()
    buttn_1 = types.InlineKeyboardButton(text="Узнать последнюю новость", callback_data="last one")
    buttn_2 = types.InlineKeyboardButton(text="Недавние события", callback_data="all")
    keyboard.add(buttn_1, buttn_2)  
    bot.send_message(message.chat.id, 'Что хотитите сделать?', reply_markup=keyboard)
    
    
    
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == "last one" :
            print_news(call.message, 1)
            start(call.message)
        elif call.data == "all":
            for i in range(10):
                    print_news(call.message, i + 1)
            start(call.message)
        elif re.fullmatch("[0-9]+", call.data) != None:
            print_more_about(call.message, int(call.data))
            start(call.message)
            

if __name__ == "__main__":
    bot.infinity_polling()
