from application import telegram_bot
from application.core import userservice
from application.resources import strings, keyboards
from application.utils import bot as botutils
from telebot.types import Message
import re


def process_phone_number(message: Message, **kwargs):
    chat_id = message.chat.id
    user_id = message.from_user.id
    language = kwargs.get('language', 'ru')

    def error():
        error_msg = strings.get_string('welcome.phone_number', language)
        telegram_bot.send_message(chat_id, error_msg, parse_mode='HTML')
        telegram_bot.register_next_step_handler_by_chat_id(chat_id, process_phone_number)

    if message.contact is not None:
        phone_number = message.contact.phone_number
    else:
        if message.text is None:
            error()
            return
        else:
            match = re.match(r'\+*998\s*\d{2}\s*\d{3}\s*\d{2}\s*\d{2}', message.text)
            if match is None:
                error()
                return
            phone_number = match.group()
    full_user_name = message.from_user.first_name
    if message.from_user.last_name:
        full_user_name += " " + message.from_user.last_name
    userservice.register_user(user_id, message.from_user.username, full_user_name, phone_number, language)
    success_message = strings.get_string('welcome.registration_successfully', language)
    botutils.to_main_menu(chat_id, language, success_message)


def process_user_language(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    def error():
        error_msg = strings.get_string('welcome.say_me_language')
        telegram_bot.send_message(chat_id, error_msg)
        telegram_bot.register_next_step_handler_by_chat_id(chat_id, process_user_language)

    if not message.text:
        error()
        return
    if message.text.startswith('/'):
        error()
        return
    if strings.get_string('language.russian') in message.text:
        language = 'ru'
    elif strings.get_string('language.uzbek') in message.text:
        language = 'uz'
    else:
        error()
        return
    userservice.set_user_language(user_id, language)
    success_message = strings.get_string('welcome.registration_successfully', language)
    botutils.to_main_menu(chat_id, language, success_message)


@telegram_bot.message_handler(commands=['start'], func=lambda m: m.chat.type == 'private')
def welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    def not_allowed():
        not_allowed_message = strings.get_string('registration.not_allowed')
        remove_keyboard = keyboards.get_keyboard('remove')
        telegram_bot.send_message(chat_id, not_allowed_message, reply_markup=remove_keyboard)

    current_user = userservice.get_user_by_telegram_id(user_id)
    if current_user:
        botutils.to_main_menu(chat_id, current_user.language)
        return
    msg_text = message.text
    message_text_parts = msg_text.split(' ')
    try:
        token = message_text_parts[1]
    except IndexError:
        not_allowed()
        return
    user = userservice.get_user_by_token(token)
    if not user:
        not_allowed()
        return
    confirmation_result = userservice.confirm_user(user, user_id, message.from_user.username)
    if not confirmation_result:
        not_allowed()
        return
    welcome_message = strings.get_string('registration.welcome').format(user.full_user_name)
    language_keyboard = keyboards.get_keyboard('welcome.language')
    telegram_bot.send_message(chat_id, welcome_message, reply_markup=language_keyboard, parse_mode='HTML')
    telegram_bot.register_next_step_handler_by_chat_id(chat_id, process_user_language)
