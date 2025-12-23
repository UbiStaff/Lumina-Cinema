from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# 创建数据库实例
db = SQLAlchemy()

# 用户信息表
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    real_name = db.Column(db.String(50))
    avatar = db.Column(db.String(255), default='default_avatar.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    review_likes = db.relationship('ReviewLike', backref='user', lazy=True)
    
    # Flask-Login required methods
    def get_id(self):
        return str(self.user_id)
    
    def __repr__(self):
        return f"<User {self.username}>"

# 电影信息表
class Movie(db.Model):
    __tablename__ = 'movies'
    
    movie_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(50))
    actors = db.Column(db.Text)
    genre = db.Column(db.String(50))
    duration = db.Column(db.Integer)  # 分钟
    release_date = db.Column(db.Date)
    description = db.Column(db.Text)
    poster = db.Column(db.String(255))
    rating = db.Column(db.Numeric(3, 1), default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    screenings = db.relationship('Screening', backref='movie', lazy=True)
    reviews = db.relationship('Review', backref='movie', lazy=True)
    
    def __repr__(self):
        return f"<Movie {self.title}>"

# 影院信息表
class Cinema(db.Model):
    __tablename__ = 'cinemas'
    
    cinema_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    halls = db.relationship('Hall', backref='cinema', lazy=True)
    
    def __repr__(self):
        return f"<Cinema {self.name}>"

# 放映厅表
class Hall(db.Model):
    __tablename__ = 'halls'
    
    hall_id = db.Column(db.Integer, primary_key=True)
    cinema_id = db.Column(db.Integer, db.ForeignKey('cinemas.cinema_id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    rows = db.Column(db.Integer, nullable=False)
    cols = db.Column(db.Integer, nullable=False)
    
    # 关系
    screenings = db.relationship('Screening', backref='hall', lazy=True)
    seats = db.relationship('Seat', backref='hall', lazy=True)
    
    def __repr__(self):
        return f"<Hall {self.name}>"

# 放映场次表
class Screening(db.Model):
    __tablename__ = 'screenings'
    
    screening_id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable=False)
    hall_id = db.Column(db.Integer, db.ForeignKey('halls.hall_id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    remaining_seats = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum('upcoming', 'ongoing', 'ended'), default='upcoming')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    orders = db.relationship('Order', backref='screening', lazy=True)
    
    def __repr__(self):
        return f"<Screening {self.screening_id}>"

# 座位表
class Seat(db.Model):
    __tablename__ = 'seats'
    
    seat_id = db.Column(db.Integer, primary_key=True)
    hall_id = db.Column(db.Integer, db.ForeignKey('halls.hall_id'), nullable=False)
    seat_row = db.Column(db.String(2), nullable=False)  # A, B, C...
    seat_col = db.Column(db.Integer, nullable=False)  # 1, 2, 3...
    type = db.Column(db.Enum('regular', 'vip', 'disabled'), default='regular')
    
    # 关系
    order_seats = db.relationship('OrderSeat', backref='seat', lazy=True)
    
    def __repr__(self):
        return f"<Seat {self.seat_row}{self.seat_col}>"

# 订单表
class Order(db.Model):
    __tablename__ = 'orders'
    
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    screening_id = db.Column(db.Integer, db.ForeignKey('screenings.screening_id'), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    order_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('pending', 'paid', 'cancelled', 'completed'), default='pending')
    payment_method = db.Column(db.String(20))
    transaction_id = db.Column(db.String(100))
    
    # 关系
    order_seats = db.relationship('OrderSeat', backref='order', lazy=True)
    
    def __repr__(self):
        return f"<Order {self.order_id}>"

# 订单座位表
class OrderSeat(db.Model):
    __tablename__ = 'order_seats'
    
    order_seat_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seats.seat_id'), nullable=False)
    
    def __repr__(self):
        return f"<OrderSeat {self.order_seat_id}>"

# 影评表
class Review(db.Model):
    __tablename__ = 'reviews'
    
    review_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5星
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    
    # 关系
    review_likes = db.relationship('ReviewLike', backref='review', lazy=True)
    
    def __repr__(self):
        return f"<Review {self.review_id}>"

# 影评点赞表
class ReviewLike(db.Model):
    __tablename__ = 'review_likes'
    
    like_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.review_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ReviewLike {self.like_id}>"