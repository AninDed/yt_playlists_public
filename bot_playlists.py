import util
import telebot
import schedule
import time
from datetime import datetime, timezone
import threading
import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)
file_handler = TimedRotatingFileHandler('logfile.log', when="midnight", interval=1, backupCount=7)
file_handler.suffix = "%Y-%m-%d"
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
    logger.info("Starting ping")
    bot.send_message(message.chat.id, "pong")
    logger.info("Ending ping")


@bot.message_handler(commands=['logs'])
def logs(message):
    logger.info("Starting logs")
    send_log_file()
    logger.info("Ending logs")


@bot.message_handler(commands=['run'])
def run(message):
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


def scheduled_function():
    logger.info("Starting run")

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

    logger.info("Ending run")
    send_log_file()


def send_log_file():
    with open('logfile.log', 'rb') as log_file:
        bot.send_document(logs_id, log_file)

def check_time_and_run():
    now = datetime.now(timezone.utc)
    if now.hour == 7 and now.minute == 0:
        scheduled_function()


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


schedule.every().minute.do(check_time_and_run)
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()

bot.infinity_polling(timeout=10, long_polling_timeout=5)
