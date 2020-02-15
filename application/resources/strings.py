import os
import json
from application.core.models import Dish, Order, Comment, OrderItem
from telebot.types import LabeledPrice
from typing import List
import settings

_basedir = os.path.abspath(os.path.dirname(__file__))

# Load strings from json
# Russian language
_strings_ru = json.loads(open(os.path.join(_basedir, 'strings_ru.json'), 'r', encoding='utf8').read())

# Uzbek language
_strings_uz = json.loads(open(os.path.join(_basedir, 'strings_uz.json'), 'r', encoding='utf8').read())


def _format_number(number: int):
    return '{0:,}'.format(number).replace(',', ' ')


def get_string(key, language='ru'):
    if language == 'ru':
        return _strings_ru.get(key, 'no_string')
    elif language == 'uz':
        return _strings_uz.get(key, 'no_string')
    else:
        raise Exception('Invalid language')


def from_cart_items(cart_items, language, total) -> str:
    cart_contains = ''
    cart_contains += '<b>{}</b>:'.format(get_string('catalog.cart', language))
    cart_contains += '\n\n'
    cart_str_item = "<b>{name}</b>\n{count} x {price} = {sum}"
    for cart_item in cart_items:
        if language == 'uz':
            dish_item = cart_str_item.format(name=cart_item.dish.name_uz,
                                             count=cart_item.count,
                                             price=_format_number(cart_item.dish.price),
                                             sum=_format_number(cart_item.count * cart_item.dish.price))
        else:
            dish_item = cart_str_item.format(name=cart_item.dish.name,
                                             count=cart_item.count,
                                             price=_format_number(cart_item.dish.price),
                                             sum=_format_number(cart_item.count * cart_item.dish.price))
        dish_item += " {}\n".format(get_string('sum', language))
        cart_contains += dish_item
    cart_contains += "\n<b>{}</b>: {} {}".format(get_string('cart.summary', language),
                                                 _format_number(total),
                                                 get_string('sum', language))

    return cart_contains


def from_dish(dish: Dish, language: str) -> str:
    dish_content = ""
    if language == 'uz':
        dish_content += dish.name_uz
    else:
        dish_content += dish.name
    dish_content += '\n\n'
    if language == 'uz':
        if dish.description_uz:
            dish_content += dish.description_uz
            dish_content += '\n\n'
    else:
        if dish.description:
            dish_content += dish.description
            dish_content += '\n\n'
    dish_content += "{}: {} {}".format(get_string('dish.price', language),
                                       _format_number(dish.price), get_string('sum', language))
    return dish_content


def from_order_shipping_method(value: str, language: str) -> str:
    return get_string('order.' + value, language)


def from_order_payment_method(value: str, language: str) -> str:
    return get_string('order.' + value, language)


def from_order(order: Order, language: str, total: int) -> str:
    order_content = "<b>{}:</b>".format(get_string('your_order', language))
    order_content += '\n\n'
    order_content += '<b>{phone}:</b> {phone_value}\n'.format(phone=get_string('phone', language),
                                                              phone_value=order.phone_number)
    if order.address_txt:
        order_content += '<b>{address}:</b> {address_value}'.format(address=get_string('address', language),
                                                                    address_value=order.address_txt)
    elif order.location:
        order_content += '<b>{address}:</b> {address_value}'.format(address=get_string('address', language),
                                                                    address_value=order.location.address)
    order_content += '\n\n'
    order_item_tmpl = '<b>{name}</b>\n{count} x {price} = {sum} {sum_str}\n'
    for order_item in order.order_items.all():
        dish = order_item.dish
        if language == 'uz':
            dish_name = dish.name_uz
        else:
            dish_name = dish.name
        order_item_str = order_item_tmpl.format(name=dish_name,
                                                count=order_item.count,
                                                price=_format_number(dish.price),
                                                sum=_format_number(order_item.count * dish.price),
                                                sum_str=get_string('sum', language))
        order_content += order_item_str
    order_content += "<b>{}</b>: {} {}".format(get_string('cart.summary', language),
                                               _format_number(total),
                                               get_string('sum', language))
    return order_content


def from_order_notification(order: Order, total_sum):
    order_content = "<b>Новый заказ! #{}</b>".format(order.id)
    order_content += '\n\n'
    order_content += '<b>Номер телефона:</b> {}\n'.format(order.phone_number)
    order_content += '<b>Имя покупателя:</b> {}\n'.format(order.user_name)
    order_content += '<b>Способ оплаты:</b> {}\n'.format(from_order_payment_method(order.payment_method, 'ru'))
    if order.address_txt:
        order_content += '<b>Адрес:</b> {}'.format(order.address_txt)
    elif order.location:
        order_content += '<b>Адрес:</b> {}'.format(order.location.address)
    order_content += '\n\n'
    order_item_tmpl = '    <i>{name}</i>\n    {count} x {price} = {sum} сум\n'
    order_items = order.order_items.all()
    grouped_order_items = {}
    categories_list = [oi.dish.category for oi in order_items]
    categories_list = list(set(categories_list))
    for category in categories_list:
        order_items_by_category = list(filter(lambda oi: oi.dish.category_id == category.id, order_items))
        grouped_order_items[category.name] = order_items_by_category
    for category, ois in grouped_order_items.items():
        group_content = '<b>%s</b>:\n' % category
        for order_item in ois:
            group_content += order_item_tmpl.format(name=order_item.dish.name,
                                                    count=order_item.count,
                                                    price=_format_number(order_item.dish.price),
                                                    sum=_format_number(order_item.dish.price * order_item.count))
        order_content += group_content
    order_content += "<b>Общая стоимость заказа</b>: {} сум".format(_format_number(order.total_amount))
    if order.delivery_price:
        order_content += '\n\n'
        order_content += '<b>Стоимость доставки</b>: {} сум'.format(_format_number(order.delivery_price))
    return order_content


def from_comment_notification(comment: Comment):
    comment_content = "<b>У вас новый отзыв!</b>\n\n"
    comment_content += "<b>От кого:</b> {}".format(comment.username)
    if comment.author.username:
        comment_content += " <i>{}</i>".format(comment.author.username)
    comment_content += "\n"
    if comment.author.phone_number:
        comment_content += "<b>Номер телефона:</b> {}".format(comment.author.phone_number)
        comment_content += '\n'
    comment_content += comment.text
    return comment_content


def from_category_name(category, language):
    if language == 'uz':
        return category.name_uz
    else:
        return category.name


def from_dish_name(dish: Dish, language):
    if language == 'uz':
        return dish.name_uz
    else:
        return dish.name


def from_order_items_to_labeled_prices(order_items: List[OrderItem], language) -> List[LabeledPrice]:
    currency_value = settings.get_currency_value()
    return [LabeledPrice(from_dish_name(oi.dish, language) + ' x ' + str(oi.count), oi.count * oi.dish.price * currency_value * 100) for oi in order_items]


def get_pavalions(language: str):
    if language == 'uz':
        return [
            '1 Павильон', '2 Павильон', '3 Павильон', '4 Павильон',
            '5 Павильон', '7 Павильон', 'Kiyim Kechak', 'Yerto`la'
        ]
    else:
        return [
            '1 Павильон', '2 Павильон', '3 Павильон', '4 Павильон',
            '5 Павильон', '7 Павильон', 'Одежда', 'Подвал'
        ]


def get_footer_blocks(language: str):
    if language == 'uz':
        return [
            '1 Blok', '2 Blok', '3 Blok', '4 Blok',
            '5 Blok', '6 Blok', '7 Blok', '8 Blok',
            '9 Blok',
        ]
    else:
        return [
            '1 Блок', '2 Блок', '3 Блок', '4 Блок',
            '5 Блок', '6 Блок', '7 Блок', '8 Блок',
            '9 Блок',
        ]


def get_clothes_blocks(language: str):
    if language == 'uz':
        return [
            '1 Blok', '2 Blok', '3 Blok', '4 Blok',
            '5 Blok', '6 Blok'
        ]
    else:
        return [
            '1 Блок', '2 Блок', '3 Блок', '4 Блок',
            '5 Блок', '6 Блок'
        ]


def check_footer_pavilion(pavilion: str, language: str):
    if language == 'uz':
        return pavilion == 'Yerto`la'
    else:
        return pavilion == 'Подвал'


def check_clothes_pavilion(pavilion: str, language: str):
    if language == 'uz':
        return pavilion == 'Kiyim Kechak'
    else:
        return pavilion == 'Одежда'
