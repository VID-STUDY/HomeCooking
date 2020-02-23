from application import telegram_bot
from application.core import userservice
from application.resources import strings, keyboards
from application.utils import bot as botutils
from telebot.types import Message, CallbackQuery
import re


users_data = {}


def delete_message_handler(message: Message):
    telegram_bot.delete_message(message.chat.id, message.message_id)
    telegram_bot.register_next_step_handler_by_chat_id(message.chat.id, delete_message_handler)


@telegram_bot.callback_query_handler(func=lambda query: 'address' in query.data)
def address_inline_handler(query: CallbackQuery):
    if query.from_user.id not in users_data:
        return
    data = query.data.split(':')

    shop_number = data[1]
    user_data = users_data[query.from_user.id]
    if 'confirm' in shop_number:
        if 'shop_number' not in user_data or user_data['shop_number'] == '':
            telegram_bot.answer_callback_query(query.id, strings.get_string('registration.shop_number_required'))
            return
        if 'block' in user_data:
            shop_address = '{}, {} - {}'.format(user_data['pavilion'], user_data['block'], user_data['shop_number'])
        else:
            shop_address = '{}, {}'.format(user_data['pavilion'], user_data['shop_number'])

        username = user_data['username']
        userservice.register_user(query.message.chat.id, username, user_data['name'], user_data['phone_number'],
                                  user_data['language'], shop_address)
        telegram_bot.edit_message_text(strings.get_string('registration.shop_number.success', user_data['language']),
                                       query.message.chat.id, query.message.message_id)
        success_message = strings.get_string("welcome.registration_successfully", user_data['language'])
        telegram_bot.clear_step_handler_by_chat_id(query.message.chat.id)
        botutils.to_main_menu(query.message.chat.id, user_data['language'], success_message)
    elif 'delete' in shop_number:
        if 'shop_number' in user_data:
            user_data['shop_number'] = user_data['shop_number'][:-1]
        address_message = strings.get_string('registration.shop_number', language=user_data['language']).format(
            user_data['shop_number'])
        address_keyboard = keyboards.get_address_inline_keyboard(user_data['language'])
        telegram_bot.edit_message_text(address_message, query.from_user.id, query.message.message_id, parse_mode='HTML',
                                       reply_markup=address_keyboard)
    else:
        if 'shop_number' in user_data:
            user_data['shop_number'] += shop_number
        else:
            user_data['shop_number'] = shop_number
        address_message = strings.get_string('registration.shop_number', language=user_data['language']).format(
            user_data['shop_number'])
        address_keyboard = keyboards.get_address_inline_keyboard(user_data['language'])
        telegram_bot.edit_message_text(address_message, query.from_user.id, query.message.message_id, parse_mode='HTML', reply_markup=address_keyboard)


def request_registration_phone_number_handler(message: Message, **kwargs):
    chat_id = message.chat.id
    user_id = message.from_user.id
    name = kwargs.get('name')
    language = kwargs.get('language')

    def error():
        error_msg = strings.get_string('registration.request.phone_number', language)
        telegram_bot.send_message(chat_id, error_msg, parse_mode='HTML')
        telegram_bot.register_next_step_handler_by_chat_id(chat_id, request_registration_phone_number_handler, name=name, language=language)

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
    shop_address_message = strings.get_string('registration.pavilion', language)
    remove_keyboard = keyboards.get_pavilions_keyboard(language)
    telegram_bot.send_message(chat_id, shop_address_message, reply_markup=remove_keyboard)
    telegram_bot.register_next_step_handler_by_chat_id(chat_id, pavilion_handler, name=name, language=language, phone_number=phone_number)


def pavilion_handler(message: Message, **kwargs):
    chat_id = message.chat.id
    language = kwargs.get('language')
    name = kwargs.get('name')
    phone_number = kwargs.get('phone_number')
    
    def error():
        error_message = strings.get_string('registration.pavilion', language)
        telegram_bot.send_message(chat_id, error_message)
        telegram_bot.register_next_step_handler_by_chat_id(chat_id, pavilion_handler, name=name, language=language, phone_number=phone_number)
    
    if not message.text:
        error()
        return
    pavilion = message.text
    if pavilion not in strings.get_pavalions(language):
        error()
        return
    if strings.check_footer_pavilion(pavilion, language) or strings.check_clothes_pavilion(pavilion, language):
        block_message = strings.get_string('registration.block', language)
        if strings.check_clothes_pavilion(pavilion, language):
            blocks_keyboard = keyboards.get_clothes_blocks_ketboard(language)
            pavilion_type = 'clothes'
        else:
            blocks_keyboard = keyboards.get_footer_blocks_keyboard(language)
            pavilion_type = 'footer'
        telegram_bot.send_message(chat_id, block_message, reply_markup=blocks_keyboard)
        telegram_bot.register_next_step_handler_by_chat_id(chat_id, block_handler, language=language, name=name, 
                                                           phone_number=phone_number, pavilion=pavilion, pavilion_type=pavilion_type)
    else:
        shop_address_message = strings.get_string('registration.shop_number', language).format('')
        address_keyboard = keyboards.get_address_inline_keyboard(language)
        telegram_bot.send_message(chat_id, shop_address_message, reply_markup=address_keyboard, parse_mode='HTML')
        users_data[chat_id] = {
            'language': language,
            'name': name,
            'phone_number': phone_number,
            'pavilion': pavilion,
            'username': message.from_user.username
        }
        telegram_bot.register_next_step_handler_by_chat_id(chat_id, delete_message_handler)


def block_handler(message: Message, **kwargs):
    chat_id = message.chat.id
    language = kwargs.get('language')
    name = kwargs.get('name')
    phone_number = kwargs.get('phone_number')
    pavilion = kwargs.get('pavilion')
    pavilion_type = kwargs.get('pavilion_type')

    def error():
        error_message = strings.get_string('registration.block', language)
        telegram_bot.send_message(chat_id, error_message)
        telegram_bot.register_next_step_handler_by_chat_id(chat_id, block_handler, language=language, name=name, 
                                                           phone_number=phone_number, pavilion=pavilion, pavilion_type=pavilion_type)
    
    if not message.text:
        error()
        return
    if pavilion_type == 'clothes':
        blocks_list = strings.get_clothes_blocks(language)
    else:
        blocks_list = strings.get_footer_blocks(language)
    block = message.text
    if block not in blocks_list:
        error()
        return
    shop_address_message = strings.get_string('registration.shop_number', language).format('')
    address_keyboard = keyboards.get_address_inline_keyboard(language)
    telegram_bot.send_message(chat_id, shop_address_message, reply_markup=address_keyboard, parse_mode='HTML')
    users_data[chat_id] = {
        'language': language,
        'name': name,
        'phone_number': phone_number,
        'pavilion': pavilion,
        'block': block,
        'username': message.from_user.username
    }
    telegram_bot.register_next_step_handler_by_chat_id(chat_id, delete_message_handler)


def shop_handler(message: Message, **kwargs):
    chat_id = message.chat.id
    language = kwargs.get('language')
    name = kwargs.get('name')
    phone_number = kwargs.get('phone_number')
    pavilion = kwargs.get('pavilion')
    block = kwargs.get('block', None)

    def error():
        shop_address_message = strings.get_string('registration.shop_number', language)
        telegram_bot.send_message(chat_id, shop_address_message)
        telegram_bot.register_next_step_handler_by_chat_id(chat_id, shop_handler, language=language, name=name, phone_number=phone_number, pavilion=pavilion, block=block)
    
    if not message.text:
        error()
        return
    shop_number = message.text
    if block:
        shop_address = '{}, {} - {}'.format(pavilion, block, shop_number)
    else:
        shop_address = '{}, {}'.format(pavilion, shop_number)

    username = message.from_user.username
    userservice.register_user(chat_id, username, name, phone_number, language, shop_address)
    success_message = strings.get_string("welcome.registration_successfully", language)
    botutils.to_main_menu(chat_id, language, success_message)


def process_user_language(message: Message):
    chat_id = message.chat.id

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
    request_registration_handler(message, language)


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
        userservice.remove_user(user_id)
        telegram_bot.clear_step_handler_by_chat_id(chat_id)
    welcome_message = strings.get_string('welcome')
    language_keyboard = keyboards.get_keyboard('welcome.language')
    telegram_bot.send_message(chat_id, welcome_message, reply_markup=language_keyboard, parse_mode='HTML')
    telegram_bot.register_next_step_handler_by_chat_id(chat_id, process_user_language)


def request_registration_handler(message: Message, language: str):
    chat_id = message.chat.id

    welcome_message = strings.get_string('registration.request.welcome', language)
    remove_keyboard = keyboards.get_keyboard('remove')
    telegram_bot.send_message(chat_id, welcome_message, reply_markup=remove_keyboard)
    telegram_bot.register_next_step_handler_by_chat_id(chat_id, request_registration_name_handler, language=language)


def request_registration_name_handler(message: Message, **kwargs):
    chat_id = message.chat.id
    language = kwargs.get('language')

    def error():
        error_msg = strings.get_string('registration.request.welcome', language)
        telegram_bot.send_message(chat_id, error_msg)
        telegram_bot.register_next_step_handler_by_chat_id(chat_id, request_registration_name_handler, language=language)

    if not message.text:
        error()
        return
    name = message.text
    phone_number_message = strings.get_string('registration.request.phone_number', language)
    phone_number_keyboard = keyboards.from_user_phone_number(language, go_back=False)
    telegram_bot.send_message(chat_id, phone_number_message, parse_mode='HTML', reply_markup=phone_number_keyboard)
    telegram_bot.register_next_step_handler_by_chat_id(chat_id, request_registration_phone_number_handler, name=name, language=language)
