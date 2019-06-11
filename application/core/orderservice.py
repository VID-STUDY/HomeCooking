from application import db
from application.core.models import Order, User, Location
from application.utils import geocode, date
from . import userservice
from datetime import datetime, timedelta
import settings
from math import floor
from typing import List


def get_current_order_by_user(user_id: int) -> Order:
    user = User.query.get(user_id)
    return user.orders.filter(Order.confirmed != True).first()


def get_order_yesterday_today_statistic():
    all_orders = Order.query.filter(Order.confirmed == True).all()
    yesterday = date.convert_utc_to_asia_tz(datetime.utcnow() - timedelta(days=1))
    yesterday_start = datetime(yesterday.year, yesterday.month, yesterday.day, tzinfo=yesterday.tzinfo)
    yesterday_end = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59, tzinfo=yesterday.tzinfo)
    today = date.convert_utc_to_asia_tz(datetime.utcnow())
    today_start = datetime(today.year, today.month, today.day, tzinfo=today.tzinfo)
    yesterday_orders_count = len([o for o in all_orders if yesterday_start <= date.convert_utc_to_asia_tz(o.confirmation_date) <= yesterday_end])
    today_orders_count = len([o for o in all_orders if today_start <= date.convert_utc_to_asia_tz(o.confirmation_date) <= today])
    return yesterday_orders_count, today_orders_count


def get_all_confirmed_orders() -> List[Order]:
    return Order.query.filter(Order.confirmed == True).order_by(Order.confirmation_date.desc()).all()


def get_order_by_id(order_id) -> Order:
    return Order.query.get_or_404(order_id)


def get_all_order_locations() -> List[Location]:
    orders = get_all_confirmed_orders()
    return [order.location for order in orders if order.location]


def make_an_order(user_id: int):
    """
    Make a new empty order if doesn't exist in user's orders
    :param user_id: User's Telegram-ID
    :return: void
    """
    user = User.query.get(user_id)
    current_order = get_current_order_by_user(user_id)
    if not current_order:
        new_order = Order()
        new_order.fill_from_user_cart(user.cart.all())
        user.orders.append(new_order)
        db.session.add(new_order)
    else:
        current_order.fill_from_user_cart(user.cart.all())
        current_order.payment_method = None
        current_order.address_txt = None
        if current_order.location:
            db.session.delete(current_order.location)
        current_order.shipping_method = None
        current_order.delivery_price = None
    db.session.commit()


def set_shipping_method(user_id: int, shipping_method: str):
    """
    Set shipping method to user's current order
    :param user_id: User's Telegram-ID
    :param shipping_method: String value of shipping method (Order.ShippingMethods is recommended to use)
    :return: void
    """
    current_order = get_current_order_by_user(user_id)
    current_order.shipping_method = shipping_method
    db.session.commit()


def set_payment_method(user_id: int, payment_method: str):
    """
    Set payment method to user's current order
    :param user_id: User's Telegram-ID
    :param payment_method: String value of payment method (Order.PaymentMethods is recommended to use)
    :return: void
    """
    current_order = get_current_order_by_user(user_id)
    current_order.payment_method = payment_method
    db.session.commit()


def set_address_by_string(user_id: int, address: str):
    """
    Set address by user's address string
    :param user_id: Telegram-ID
    :param address: String value of address
    :return: void
    """
    current_order = get_current_order_by_user(user_id)
    current_order.address_txt = address
    db.session.commit()


def set_address_by_map_location(user_id: int, map_location: tuple) -> bool:
    """
    Set address by location sent by user
    :param user_id: User's Telegram-ID
    :param map_location: tuple of latitude and longitude
    :return: void
    """
    latitude = map_location[0]
    longitude = map_location[1]
    address = geocode.get_address_by_coordinates(map_location)
    if not address:
        return False
    current_order = get_current_order_by_user(user_id)
    order_location = Location(latitude=latitude, longitude=longitude, address=address)
    current_order.location = order_location
    # Calculate a delivery price
    delivery_cost = settings.get_delivery_cost()
    first_3_km = delivery_cost[0]
    others_km = delivery_cost[0]
    # Calculate distance from cafe to customer
    distance = geocode.distance_between_two_points(map_location, settings.get_cafe_coordinates())
    rest_distance = distance[0]
    if distance[1] == 'm':
        # If distance less than 1 kilometer, dont't care about it
        current_order.delivery_price = first_3_km
    else:
        # And most cheerful actions begin here...
        if rest_distance <= 3:
            # If distance is in limits 3 kilometres, don't care about it
            delivery_price = first_3_km
        else:
            # Else, calculate first 3 kilometres, than others kilometres
            price = first_3_km
            rest_distance -= 3.0
            price += rest_distance * others_km
            delivery_price = price
        # Check if calculated delivery price is more than limit
        limit_delivery_price = settings.get_limit_delivery_price()
        if delivery_price > limit_delivery_price:
            current_order.delivery_price = limit_delivery_price
        # If the delivery price is less than limit, round price
        else:
            # -- Round the delivery price --
            # Here we get the rounded price without hundreds
            int_value = floor(delivery_price / 1000) * 1000
            if delivery_price != int_value:
                # Add 500 to compare if delivery price less or more the half integer value
                half_int_value = int_value + 500
                if delivery_price < half_int_value:
                    difference = half_int_value - delivery_price
                    delivery_price += (difference - 100)
                    delivery_price = round(delivery_price/1000 + 5/100, 1) * 1000
                elif delivery_price > half_int_value:
                    delivery_price = round(delivery_price / 1000) * 1000
            current_order.delivery_price = delivery_price
    db.session.commit()
    return True


def set_phone_number(user_id: int, phone_number: str) -> Order:
    current_order = get_current_order_by_user(user_id)
    current_order.phone_number = phone_number
    userservice.set_user_phone_number(user_id, phone_number)
    db.session.commit()
    return current_order


def confirm_order(user_id: int, first_name: str, last_name: str):
    """
    Confirm order and let him show on admin panel
    :param user_id: User's Telegram-ID
    :return: void
    """
    current_order = get_current_order_by_user(user_id)
    current_order.confirmed = True
    current_order.confirmation_date = datetime.utcnow()
    current_order.user_name = first_name
    if last_name:
        current_order.user_name += " " + last_name
    userservice.clear_user_cart(user_id)
    db.session.commit()
    return current_order
