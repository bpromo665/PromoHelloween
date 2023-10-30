from project import bot
from telebot import types

from project.models import User
from project import session

import project.modules.admin as admin
from project.models import PromoCode


def is_registered(telegram_id):
    if session.query(User).filter_by(telegram_id=str(telegram_id)).first():
        return True
    return False


def welcome_message(message: types.Message):
    if not is_registered(message.from_user.id):
        bot.send_message(message.chat.id, f'~~Вітаю!~~ Цукерки або смерть🎃?\n\n'
                                          f'Бачу що ти вже вибрав цукерки, тому маєш можливість виграти 1 із 300 призів,\n\n'
                                          f'які ми підготували.\n\n', parse_mode='MarkdownV2')

    handle_start(message)


def handle_start(message: types.Message):
    if is_registered(message.from_user.id):
        handle_promo_code(message)
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        reg_button = types.KeyboardButton(text="Поділитися номером", request_contact=True)
        markup.add(reg_button)
        bot.send_message(message.chat.id, 'Нам потрібен твій номер телефону, щоб звʼязатися з тобою, коли ти виграєш приз. 📲',
                         reply_markup=markup)
        bot.register_next_step_handler(message, get_the_phone)


@bot.message_handler(content_types=['contact'])
def get_the_phone(message: types.Message):
    try:
        user = User(telegram_id=message.from_user.id, username=message.from_user.username)
        user.phone_number = message.contact.phone_number
        session.add(user)
        session.commit()
        bot.send_message(message.chat.id, 'Дякую! Тепер ми знаємо, як зв\'язатись з тобою.🔑')
        bot.send_message(message.chat.id, 'Як це працює?😎\n\n'
                                          '1. Придбати банку у будь-кого з наших партнерів\n'
                                          '2. Отримати виграшний промокод\n'
                                          '3. Ввести свій промокод у чат бота\n'
                                          '4. Отримати винагороду 🥳\n\n'
                                          '_Після використання промокод стає недійсний, отже подарунок ви зможете отримати лише один раз_', parse_mode='Markdown')
    except ValueError as value_error:
        session.rollback()
        bot.send_message(message.chat.id, value_error)

    except Exception as e:
        print(e)
        session.rollback()
        bot.send_message(message.chat.id, 'Магічна куля не бачить такого промокоду. Перевір уважно ще раз.')
    finally:
        handle_start(message)


@bot.message_handler(content_types=['text'])
def handle_promo_code(message: types.Message):
    temp = 0
    if message.text == '/admin':
        message.text = ''
        admin.handle_admin(message)
    else:
        if temp == 0:
            bot.send_message(message.chat.id, 'Напиши свій промокод, а я спробую начаклувати тобі перемогу! ⬇️',
                             reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.send_message(message.chat.id, 'Магічна куля не бачить такого промокоду. Перевір уважно ще раз. 🔮', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, check_promo_code)


def check_promo_code(message: types.Message):
    try:
        code = session.query(PromoCode).filter_by(code=str(message.text)).first()
        user = session.query(User).filter_by(telegram_id=str(message.from_user.id)).first()
        admins = session.query(User).filter(User.is_admin.is_(True))

        if code.is_used:
            bot.send_message(message.chat.id, 'Хтось вже використав цей промокод. Спробуй ввести інший. ☹️')
        elif code.prize is None:
            bot.send_message(message.chat.id, 'Ой-ой! Здається злі духи проти твоєї перемоги... Спробуй інший промокод.')
            code.is_used = True
            session.commit()
        else:
            bot.send_message(message.chat.id, f"Вітаємо з перемогою!  🎊🥳🎉\n\n"
                                              f"Ти - справжній чемпіон у світі тіней і жахів. Ура! 😈\n\n"
                                              f"Ти виграв {code.prize} \n\n"
                                              f"Ми передали інформацію нашому менеджеру! Найближчим часом він з вами зв'яжеться")
            code.is_used = True
            session.commit()
            for admin in admins:
                bot.send_message(chat_id=admin.telegram_id, text=f'Юзер @{user.username} виграв приз!\n'
                                                                         f'Номер телефону: {user.phone_number}\n\n'
                                                                         f'Виграш:\n'
                                                                         f'Код: {code.code}\n'
                                                                         f'Приз: {code.prize}')
    except Exception as e:
        print(e)
        # bot.send_message(message.chat.id, 'Здається ви ввели неправильний промокод!❌')
    handle_promo_code(message)
