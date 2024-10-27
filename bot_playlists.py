import util
import telebot
import schedule
import time
from datetime import datetime, timezone
import threading
import logging

logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('logfile.log')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

ut = util.Util(logger)
logs_id = ut.LOGS_ID
bot = telebot.TeleBot(ut.BOT_TOKEN)
del ut


@bot.message_handler(commands=['ping'])
def ping(message):
    try:
        logger.info("Starting ping")
        bot.send_message(message.chat.id, "pong")
        logger.info("Ending ping")
    except Exception as e:
        logger.exception("Error in ping command")


@bot.message_handler(commands=['logs'])
def logs(message):
    try:
        logger.info("Starting logs")
        send_log_file()
        logger.info("Ending logs")
    except Exception as e:
        logger.exception("Error in logs command")


@bot.message_handler(commands=['run'])
def run(message):
    try:
        logger.info("Starting run")
        bot.send_message(message.chat.id, "Starting")

        ut = util.Util(logger)
        msgs = ut.all_way()

        bot.send_message(chat_id=ut.CHAT_IDS['games'],
                         text=msgs['games'],
                         parse_mode='HTML',
                         disable_web_page_preview=True)

        bot.send_message(chat_id=ut.CHAT_IDS['enter'],
                         text=msgs['enter'],
                         parse_mode='HTML',
                         disable_web_page_preview=True)

        del ut

        bot.send_message(message.chat.id, "Ending")
        logger.info("Ending run")
        send_log_file()
    except Exception as e:
        logger.exception("Error in run command")


@bot.message_handler(commands=['time'])
def server_time(message):
    try:
        logger.info("Starting server_time")

        now = datetime.now(timezone.utc)

        bot.send_message(message.chat.id, now)
        logger.info("Ending server_time")
    except Exception as e:
        logger.exception("Error in server_time command")


def scheduled_function():
    try:
        logger.info("Starting scheduled run")

        ut = util.Util(logger)
        msgs = ut.all_way()

        bot.send_message(chat_id=ut.CHAT_IDS['games'],
                         text=msgs['games'],
                         parse_mode='HTML',
                         disable_web_page_preview=True)

        bot.send_message(chat_id=ut.CHAT_IDS['enter'],
                         text=msgs['enter'],
                         parse_mode='HTML',
                         disable_web_page_preview=True)

        del ut

        logger.info("Ending scheduled run")
        send_log_file()
    except Exception as e:
        logger.exception("Error in scheduled function")


def send_log_file():
    with open('logfile.log', 'rb') as log_file:
        bot.send_document(logs_id, log_file)


def check_time_and_run():
    now = datetime.now(timezone.utc)
    if now.hour == 8 and now.minute == 0:
        scheduled_function()


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


schedule.every().minute.do(check_time_and_run)
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()

bot.infinity_polling(timeout=10, long_polling_timeout=5)
