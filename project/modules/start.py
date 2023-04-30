from project import bot
from telebot import types


async def handle_start(message: types.Message):
    await bot.send_message(message.chat.id, 'Hello! This is bot template!')
