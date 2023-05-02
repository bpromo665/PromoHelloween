from project import bot

import project.modules.start as start
import project.modules.admin as admin


@bot.message_handler(commands=['start'])
def start_handler(message):
    start.welcome_message(message)


@bot.message_handler(commands=['admin'])
def start_handler(message):
    admin.handle_admin(message)
