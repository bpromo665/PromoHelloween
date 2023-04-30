from project import bot
from telebot import types


def handle_start(message: types.Message):
    bot.send_message(message.chat.id, 'Hello! This is bot template!')
