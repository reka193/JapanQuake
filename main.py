from telegram.ext import Updater, CommandHandler
import requests
from bs4 import BeautifulSoup


def get_info():
    page = requests.get('https://www.jma.go.jp/en/quake/')
    bs_page = BeautifulSoup(page.text, 'html.parser')
    datetime = bs_page.find(attrs={'class': 'textframe'}).findAll('td')[6]
    magnitude = bs_page.find(attrs={'class': 'textframe'}).findAll('td')[10]
    region = bs_page.find(attrs={'class': 'textframe'}).findAll('td')[11]
    return datetime.text, magnitude.text, region.text


def eq_message(bot, update):
    datetime, magnitude, region = get_info()
    chat_id = update.message.chat_id
    text = "New earthquake!\n{} with {} magnitude, in {}.".format(datetime, magnitude, region)
    bot.send_message(chat_id=chat_id, text=text)


def main():
    updater = Updater('889819370:AAEmCPz47xgffA9rPPy6V8NuJee-FzaYscw')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('help', eq_message))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
