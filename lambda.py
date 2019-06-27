from telegram.ext import Updater, CommandHandler
import requests
import boto3
from bs4 import BeautifulSoup

token = <BOTTOKEN>


# Extracting the necessary information from the website
def get_info():
    page = requests.get('https://www.jma.go.jp/en/quake/')
    bs_page = BeautifulSoup(page.text, 'html.parser')
    datetime = bs_page.find(attrs={'class': 'textframe'}).findAll('td')[6]
    magnitude = bs_page.find(attrs={'class': 'textframe'}).findAll('td')[10]
    region = bs_page.find(attrs={'class': 'textframe'}).findAll('td')[11]
    return datetime.text, magnitude.text, region.text


# Basic message sender for the 'help' command
def eq_message(bot, update):
    datetime, magnitude, region = get_info()
    chat_id = update.message.chat_id
    text = "New earthquake!\n{} with {} magnitude, in {}.".format(datetime, magnitude, region)
    bot.send_message(chat_id=chat_id, text=text)


# Function for the 'add' command, subscribing the user by adding the chat_id to the db
def subscribe(bot, update):
    chat_id = update.message.chat_id
    dynamodb = boto3.client('dynamodb')
    try:
        dynamodb.put_item(TableName='subscribers', Item={'chat_id': {'N': str(chat_id)}})
    except Exception as e:
        print(e)
    bot.send_message(chat_id=chat_id, text="You have subscribed!")


# Function for the 'delete' command, unsubscribe the user by deleting her chat_id from the db
def unsubscribe(bot, update):
    chat_id = update.message.chat_id
    dynamodb = boto3.client('dynamodb')
    try:
        dynamodb.delete_item(TableName='subscribers', Key={'chat_id': {'N': str(chat_id)}})
    except Exception as e:
        print(e)
    bot.send_message(chat_id=chat_id, text="You have unsubscribed!")


# send notification to the chat_ids in the db, in case there is a new earthquake
def send_notification(bot):
    # collect all chat_ids
    dynamodb = boto3.client('dynamodb')
    ids = dynamodb.scan(TableName='subscribers')
    # collect the actual information
    datetime, magnitude, region = get_info()
    eq_info = datetime+magnitude+region
    # collect the last information sent
    old_info = dynamodb.scan(TableName='earthquake_info')
    old_info = old_info['Items'][0]['info']['S']

    # if the information is new, send a notification to all the chat_ids in the db
    if not old_info == eq_info:
        dynamodb.delete_item(TableName='earthquake_info', Key={'info': {'S': str(old_info)}})
        dynamodb.put_item(TableName='earthquake_info', Item={'info': {'S': str(eq_info)}})
        text = "New earthquake!\n{} with {} magnitude, in {}.".format(datetime, magnitude, region)
        for item in ids['Items']:
            id_number = item['chat_id']['N']
            try:
                bot.send_message(chat_id=id_number, text=text)
            except Exception as e:
                print(e)


# lambda handler for aws
def lambda_handler(event, context):

    updater = Updater(token)
    dp = updater.dispatcher
    bot = updater.bot
    dp.add_handler(CommandHandler('help', eq_message))
    dp.add_handler(CommandHandler('add', subscribe))
    dp.add_handler(CommandHandler('delete', unsubscribe))

    updater.start_polling()
    send_notification(bot)
    updater.idle()
