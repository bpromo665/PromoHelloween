import config

from project import bot
from telebot import types
import threading
from project import app

from project.modules import start
from flask import request, render_template


@bot.message_handler(commands=['start'])
def start_handler(message: types.Message):
    start.handle_start(message)


@app.route('/settings', methods=['POST', 'GET'])
def settings():
    if request.method == 'POST':
        print("success")
        return render_template('index.html', commands=['start'])
    else:
        return render_template('index.html', commands=['start'])
