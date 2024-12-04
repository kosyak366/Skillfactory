import telebot
from extensions import APIException, CryptoConverter
from config import keys, TOKEN

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def help(message: telebot.types.Message):
    text = ('Здравствуйте, вы пришли к боту, который переводит валюту, чтобы попробовать напишите сообщение \n\
по следующему примеру:\n\
<имя валюты, цену которой хотите узнать> \n\
<имя валюты, в которой надо узнать цену> \n\
<количество первой валюты> \nЧтобы увидеть список валют напишите: /values')
    bot.reply_to(message, text)

@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты: '
    for key in keys.keys():
        text = '\n'.join((text, key, ))
    bot.reply_to(message, text)

@bot.message_handler(content_types = ['text', ])
def convert(message: telebot.types.Message):
    try:
        val = message.text.split(' ')

        if len(val) != 3:
            raise APIException('Параметров должно быть ровно 3, проверьте еще раз. /help')

        quote, base, amount = val

        total, price = CryptoConverter.get_price(base, quote, amount)
    except APIException as e:
        bot.reply_to(message, f'Ошибка пользователя при вводе:\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Программе не удалось обработать команду:\n{e}')
    else:
        text = f'Цена может меняться, но сейчас {quote} в {base} = {price} \nСтоимость {amount} {quote} = {total} {base}'
        bot.send_message(message.chat.id, text)

bot.polling()