import config
from project import bot
from telebot import types
import threading

from project.modules import start


@bot.message_handler(commands=['start'])
def start_handler(message: types.Message):
    start.handle_start(message)

