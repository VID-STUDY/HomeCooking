from application import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class CartItem(db.Model):
    """
    Model for cart item
    """
    __tablename__ = 'cart_items'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), primary_key=True)
    count = db.Column(db.Integer)
    dish = db.relationship('Dish')


class OrderItem(db.Model):
    """
    Model for order item
    """
    __tablename__ = 'order_items'
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), primary_key=True)
    count = db.Column(db.Integer)
    dish = db.relationship('Dish')


class User(db.Model):
    """
    Model for users in Telegram Bot
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    language = db.Column(db.String(5))
    cart = db.relationship('CartItem', lazy='dynamic', backref='user', cascade='all, delete-orphan')
    orders = db.relationship('Order', lazy='dynamic', backref='customer')
    comments = db.relationship('Comment', lazy='dynamic', backref='author')

    def _get_cart_item_for_dish(self, dish) -> CartItem:
        """
        Check if dish is exists in cart
        :param dish: Dish
        :return: Check's result
        """
        return self.cart.filter(CartItem.dish_id == dish.id).first()

    def add_dish_to_cart(self, dish, count):
        """
        Add a dish to cart if there isn't it in cart.
        And add cart item to database session
        :param dish: Dish
        :param count: Numbers of the dish
        :return: void
        """
        cart_item = self._get_cart_item_for_dish(dish)
        if cart_item:
            cart_item.count = count
            return
        cart_item = CartItem(count=count, dish=dish)
        self.cart.append(cart_item)
        db.session.add(cart_item)

    def remove_dish_from_cart(self, dish):
        """
        Remove dish from cart if it exists
        :param dish: Dish
        :return: void
        """
        cart_item = self._get_cart_item_for_dish(dish)
        if not cart_item:
            return
        self.cart.remove(cart_item)


class UserAdmin(db.Model, UserMixin):
    """
    Model for users in admin panel
    """
    __tablename__ = 'user_admins'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), index=True)
    password_hash = db.Column(db.String(120))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class DishCategory(db.Model):
    """
    Model for dish category
    """
    __tablename__ = 'dish_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    name_uz = db.Column(db.String(100))
    dishes = db.relationship('Dish', lazy='dynamic', backref='category')


class Dish(db.Model):
    """
    Model for dishes
    """
    __tablename__ = 'dishes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    name_uz = db.Column(db.String(100))
    image_id = db.Column(db.String(150))
    image_path = db.Column(db.String(150))
    description = db.Column(db.String(500))
    description_uz = db.Column(db.String(500))
    price = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey('dish_categories.id'))


class Order(db.Model):
    """
    Model for orders
    Contains class OrderTypes to set type of order
    """
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    shipping_method = db.Column(db.String(50))
    payment_method = db.Column(db.String(50))
    address_txt = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    confirmed = db.Column(db.Boolean, default=False)
    confirmation_date = db.Column(db.DateTime)
    delivery_price = db.Column(db.Integer)
    order_items = db.relationship('OrderItem', lazy='dynamic',
                                  backref='order', cascade='all, delete-orphan')
    location = db.relationship('Location', uselist=False, cascade='all,delete')

    def fill_from_user_cart(self, cart):
        """
        Fill order items from user's cart.
        Add new objects to db.session
        :param cart: User's cart
        :return: void
        """
        # Clear current order items collection
        for order_item in self.order_items.all():
            self.order_items.remove(order_item)
        # And add fresh cart items to order
        for cart_item in cart:
            order_item = OrderItem()
            order_item.count = cart_item.count
            order_item.dish = cart_item.dish
            self.order_items.append(order_item)
            db.session.add(order_item)

    class ShippingMethods:
        PICK_UP = 'pickup'
        DELIVERY = 'delivery'

    class PaymentMethods:
        CASH = 'cash'
        TERMINAL = 'terminal'
        CLICK = 'click'
        PAYME = 'payme'


class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    address = db.Column(db.String(100))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))


class Comment(db.Model):
    """
    Model for users' comments
    """
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class UserDish(db.Model):
    """
    Model for saving current dish of user
    """
    user_id = db.Column(db.Integer, index=True, primary_key=True)
    dish_id = db.Column(db.Integer, index=True)


@login.user_loader
def load_user(user_id):
    return UserAdmin.query.get(int(user_id))
