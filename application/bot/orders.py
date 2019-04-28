from application import telegram_bot as bot
from application.core import orderservice, userservice
from application.resources import strings, keyboards
from telebot.types import Message
from .catalog import back_to_the_catalog
from application.core.models import Order


def _total_order_sum(order_items) -> int:
    summary_dishes_sum = [order_item.count * order_item.dish.price for order_item in order_items]
    total = sum(summary_dishes_sum)
    return total


def _to_the_shipping_method(chat_id, language):
    order_shipping_method_message = strings.get_string('order.shipping_method', language)
    order_shipping_method_keyboard = keyboards.get_string('order.shipping_methods', language)
    bot.send_message(chat_id, order_shipping_method_message, parse_mode='HTML',
                     reply_markup=order_shipping_method_keyboard)
    bot.register_next_step_handler_by_chat_id(chat_id, shipping_method_processor)


def _to_the_payment_method(chat_id, language):
    payment_message = strings.get_string('order.payment', language)
    payment_keyboard = keyboards.get_keyboard('order.payment', language)
    bot.send_message(chat_id, payment_message, reply_markup=payment_keyboard)
    bot.register_next_step_handler_by_chat_id(chat_id, payment_method_processor)


def _to_the_address(chat_id, language):
    address_message = strings.get_string('order.address', language)
    address_keyboard = keyboards.get_keyboard('order.address', language)
    bot.send_message(chat_id, address_message, parse_mode='HTML', reply_markup=address_keyboard)
    bot.register_next_step_handler_by_chat_id(chat_id, address_processor)


def _to_the_confirmation(chat_id, current_order, language):
    total = _total_order_sum(current_order.order_items.all())
    summary_order_message = strings.from_order(current_order, language, total)
    confirmation_keyboard = keyboards.get_keyboard('order.confirmation', language)
    bot.send_message(chat_id, summary_order_message, parse_mode='HTML', reply_markup=confirmation_keyboard)
    bot.register_next_step_handler_by_chat_id(chat_id, confirmation_processor)


def order_processor(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    language = userservice.get_user_language(user_id)

    cart = userservice.get_user_cart(user_id)
    if len(cart) == 0:
        cart_empty_message = strings.get_string('cart.empty', language)
        back_to_the_catalog(chat_id, language, cart_empty_message)
        return
    _to_the_shipping_method(chat_id, language)


def shipping_method_processor(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    language = userservice.get_user_language(user_id)

    def error():
        error_msg = strings.get_string('order.shipping_method_error', language)
        bot.send_message(chat_id, error_msg)
        bot.register_next_step_handler_by_chat_id(chat_id, shipping_method_processor)

    if not message.text:
        error()
        return
    orderservice.make_an_order(user_id)
    if strings.get_string('go_back', language) in message.text:
        back_to_the_catalog(chat_id, language)
    elif strings.from_order_shipping_method(Order.ShippingMethods.PICK_UP, language) in message.text:
        orderservice.set_shipping_method(user_id, Order.ShippingMethods.PICK_UP)
        _to_the_payment_method(chat_id, language)
    elif strings.from_order_shipping_method(Order.ShippingMethods.DELIVERY, language) in message.text:
        orderservice.set_shipping_method(user_id, Order.ShippingMethods.DELIVERY)
        _to_the_address(chat_id, language)
    else:
        error()
        return


def payment_method_processor(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    language = userservice.get_user_language(user_id)
    current_order = orderservice.get_current_order_by_user(user_id)

    def error():
        error_msg = strings.get_string('order.payment_error', language)
        bot.send_message(chat_id, error_msg)
        bot.register_next_step_handler_by_chat_id(chat_id, payment_method_processor)

    def confirm_order():
        _to_the_confirmation(chat_id, current_order, language)

    if not message.text:
        error()
        return
    if strings.get_string('go_to_menu', language) in message.text:
        back_to_the_catalog(chat_id, language)
    elif strings.get_string('go_back', language) in message.text:
        if current_order.shipping_method == Order.ShippingMethods.PICK_UP:
            _to_the_shipping_method(chat_id, language)
        elif current_order.shipping_method == Order.ShippingMethods.DELIVERY:
            _to_the_address(chat_id, language)
    elif strings.from_order_payment_method(Order.PaymentMethods.CASH, language) in message.text:
        orderservice.set_payment_method(user_id, Order.PaymentMethods.CASH)
        confirm_order()
    elif strings.from_order_payment_method(Order.PaymentMethods.CLICK, language) in message.text:
        orderservice.set_payment_method(user_id, Order.PaymentMethods.CLICK)
        confirm_order()
    elif strings.from_order_payment_method(Order.PaymentMethods.PAYME, language) in message.text:
        orderservice.set_payment_method(user_id, Order.PaymentMethods.PAYME)
        confirm_order()
    elif strings.from_order_payment_method(Order.PaymentMethods.TERMINAL, language) in message.text:
        orderservice.set_payment_method(user_id, Order.PaymentMethods.TERMINAL)
        confirm_order()
    else:
        error()


def address_processor(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    language = userservice.get_user_language(user_id)

    def error():
        error_msg = strings.get_string('order.address_error')
        bot.send_message(chat_id, error_msg)
        bot.register_next_step_handler_by_chat_id(chat_id, address_processor)

    if message.text:
        orderservice.set_address_by_string(user_id, message.text)
        _to_the_payment_method(chat_id, language)
    elif message.location:
        location = message.location
        orderservice.set_address_by_map_location(user_id, (location.latitude, location.longitude))
        _to_the_payment_method(chat_id, language)
    else:
        error()


def confirmation_processor(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    language = userservice.get_user_language(user_id)

    def error():
        error_msg = strings.get_string('order.confirmation_error', language)
        bot.send_message(chat_id, error_msg)
        bot.register_next_step_handler_by_chat_id(chat_id, confirmation_processor)

    if not message.text:
        error()
        return
    if strings.get_string('order.confirm', language) in message.text:
        orderservice.confirm_order(user_id)
        order_success_message = strings.get_string('order.success')
        back_to_the_catalog(chat_id, language, order_success_message)
    elif strings.get_string('order.cancel', language) in message.text:
        order_canceled_message = strings.get_string('order.canceled')
        back_to_the_catalog(chat_id, language, order_canceled_message)
    else:
        error()