import os
import traceback
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

# 创建Flask应用
app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_ticket_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 编码设置，确保中文正常显示
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'
# 设置静态文件的编码
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300  # 添加缓存控制

# 初始化扩展
# 启用CSRF保护
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# 导入模型
from models import db, User, Movie, Cinema, Hall, Screening, Seat, Order, OrderSeat, Review, ReviewLike

# 初始化数据库
db.init_app(app)

# 初始化登录管理器
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# 用户加载器
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 创建数据库表
with app.app_context():
    db.create_all()

# 添加定时任务清理过期电影
import threading
import time

def cleanup_expired_movies():
    with app.app_context():
        while True:
            try:
                # 获取当前时间
                current_time = datetime.now()
                # 计算5小时前的时间
                cutoff_time = current_time - timedelta(hours=5)
                
                # 查找并删除5小时前结束的电影场次
                expired_screenings = Screening.query.filter(Screening.end_time < cutoff_time).all()
                
                for screening in expired_screenings:
                    # 删除相关的订单座位
                    order_seats = OrderSeat.query.filter_by(screening_id=screening.screening_id).all()
                    for order_seat in order_seats:
                        db.session.delete(order_seat)
                    
                    # 删除相关的订单
                    orders = Order.query.filter_by(screening_id=screening.screening_id).all()
                    for order in orders:
                        db.session.delete(order)
                    
                    # 删除场次
                    db.session.delete(screening)
                
                db.session.commit()
                print(f"[{current_time}] 已清理 {len(expired_screenings)} 个过期场次")
                
            except Exception as e:
                print(f"清理过期场次时出错: {e}")
            
            # 每小时检查一次
            time.sleep(3600)

# 启动后台清理线程
cleanup_thread = threading.Thread(target=cleanup_expired_movies, daemon=True)
cleanup_thread.start()

# 首页
@app.route('/')
def home():
    movies = Movie.query.all()
    return render_template('home.html', movies=movies)

# 电影列表
@app.route('/movies')
def movie_list():
    # 获取搜索和筛选参数
    search_query = request.args.get('search', '')
    genre_filter = request.args.get('genre', '')
    year_filter = request.args.get('year', '')
    
    # 构建查询
    query = Movie.query
    
    # 应用搜索条件
    if search_query:
        query = query.filter(Movie.title.contains(search_query))
    
    # 应用类型筛选
    if genre_filter:
        query = query.filter(Movie.genre == genre_filter)
    
    # 应用年份筛选
    if year_filter:
        query = query.filter(db.extract('year', Movie.release_date) == year_filter)
    
    movies = query.all()
    
    # 获取所有类型用于筛选
    genres = db.session.query(Movie.genre).distinct().all()
    genres = [g[0] for g in genres if g[0]]
    
    # 获取所有年份用于筛选
    years = db.session.query(db.extract('year', Movie.release_date)).distinct().all()
    years = sorted([str(int(y[0])) for y in years if y[0]], reverse=True)
    
    return render_template('movie_list.html', 
                         movies=movies, 
                         search_query=search_query,
                         genre_filter=genre_filter,
                         year_filter=year_filter,
                         genres=genres,
                         years=years)

# 电影详情
@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    reviews = Review.query.filter_by(movie_id=movie_id).order_by(Review.created_at.desc()).all()
    
    # 获取所有未来场次，按时间排序
    screenings = Screening.query.filter_by(movie_id=movie_id).filter(Screening.start_time > datetime.now()).order_by(Screening.start_time).all()
    
    # 按日期分组场次
    from itertools import groupby
    
    # 定义分组键函数
    def get_date_key(s):
        return s.start_time.date()
    
    # 分组（screenings已经按时间排序，所以groupby可以直接工作）
    screenings_by_date = []
    for date, group in groupby(screenings, key=get_date_key):
        screenings_by_date.append({
            'date': date,
            'screenings': list(group)
        })
    
    return render_template('movie_detail.html', movie=movie, reviews=reviews, screenings_by_date=screenings_by_date)

# 选座页面
@app.route('/screening/<int:screening_id>/seats')
@login_required
def select_seats(screening_id):
    screening = Screening.query.get_or_404(screening_id)
    print(f"DEBUG: screening对象 = {screening}")
    print(f"DEBUG: screening.__dict__ = {screening.__dict__}")
    print(f"DEBUG: screening.screening_id = {screening.screening_id}")
    hall = Hall.query.get(screening.hall_id)
    cinema = Cinema.query.get(hall.cinema_id)
    
    # 获取所有座位
    seats = Seat.query.filter_by(hall_id=hall.hall_id).order_by(Seat.seat_row, Seat.seat_col).all()
    
    # 获取已选座位
    booked_seats = db.session.query(OrderSeat.seat_id).join(Order).filter(
        Order.screening_id == screening_id,
        Order.status.in_(['pending', 'paid'])
    ).all()
    booked_seat_ids = [seat_id for (seat_id,) in booked_seats]
    
    return render_template('select_seats.html', screening=screening, hall=hall, cinema=cinema, seats=seats, booked_seat_ids=booked_seat_ids, screening_id=screening_id)

# 创建订单
@app.route('/create_order', methods=['POST'])
@login_required
def create_order():
    # 调试：打印请求方法和完整的请求对象
    print(f"DEBUG: 请求方法 = {request.method}")
    print(f"DEBUG: 请求URL = {request.url}")
    print(f"DEBUG: 请求头 = {request.headers}")
    print(f"DEBUG: 所有表单数据 = {request.form}")
    
    screening_id = request.form.get('screening_id')
    
    print(f"DEBUG: 表单中的screening_id = '{screening_id}'")
    
    # 如果表单中的screening_id为空，尝试从Referer头中提取
    if not screening_id or screening_id == 'NaN' or screening_id.strip() == '':
        print("DEBUG: 进入从Referer提取screening_id的逻辑")
        referer = request.headers.get('Referer', '')
        print(f"DEBUG: Referer = '{referer}'")
        import re
        match = re.search(r'/screening/(\d+)', referer)
        if match:
            screening_id = match.group(1)
            print(f"DEBUG: 从Referer中提取到screening_id = {screening_id}")
        else:
            print("DEBUG: 正则表达式匹配失败，Referer中没有找到screening_id")
    
    seat_ids_str = request.form.get('seat_ids')
    
    print(f"DEBUG: screening_id = {screening_id}, seat_ids_str = {seat_ids_str}")
    print(f"DEBUG: screening_id类型 = {type(screening_id)}, seat_ids_str类型 = {type(seat_ids_str)}")
    
    # 检查screening_id和seat_ids_str是否存在且有效
    if not screening_id or screening_id == 'NaN':
        print("DEBUG: screening_id无效，重定向到首页")
        flash('无效的放映信息！', 'danger')
        return redirect(url_for('home'))  # 将index改为home

    if not seat_ids_str or seat_ids_str == 'NaN' or seat_ids_str.strip() == '' or 'NaN' in seat_ids_str:
        print("DEBUG: seat_ids_str无效，重定向到选座页面")
        flash('请选择座位！', 'danger')
        return redirect(url_for('select_seats', screening_id=screening_id))
    
    try:
        # 解析座位ID字符串为列表
        seat_ids = []
        for id_str in seat_ids_str.split(','):
            id_str = id_str.strip()
            print(f"DEBUG: 正在处理ID字符串: '{id_str}'")
            if id_str and id_str != 'NaN':
                seat_ids.append(int(id_str))
                print(f"DEBUG: 成功解析ID: {int(id_str)}")
        
        # 检查是否有有效的座位ID
        if not seat_ids:
            print("DEBUG: 没有有效的座位ID，重定向到选座页面")
            flash('请选择座位！', 'danger')
            return redirect(url_for('select_seats', screening_id=screening_id))
            
    except ValueError as e:
        print(f"DEBUG: ValueError occurred: {e}")
        print(f"DEBUG: 错误类型 = {type(e).__name__}")
        print(f"DEBUG: 错误堆栈 = {traceback.format_exc()}")
        flash('座位选择无效，请重新选择！', 'danger')
        return redirect(url_for('select_seats', screening_id=screening_id))
    
    print(f"DEBUG: 解析后的座位ID = {seat_ids}")
    
    screening = Screening.query.get_or_404(screening_id)
    
    # 计算总价
    total_price = screening.price * len(seat_ids)
    
    # 创建订单
    order = Order(
        user_id=current_user.user_id,
        screening_id=screening_id,
        total_price=total_price,
        status='pending'
    )
    
    db.session.add(order)
    db.session.flush()  # 获取order_id而不提交
    
    # 添加订单座位
    for seat_id in seat_ids:
        order_seat = OrderSeat(order_id=order.order_id, seat_id=seat_id)
        db.session.add(order_seat)
    
    # 更新剩余座位
    screening.remaining_seats -= len(seat_ids)
    
    db.session.commit()
    
    return redirect(url_for('order_confirmation', order_id=order.order_id))

# 订单确认
@app.route('/order/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.user_id:
        flash('无权访问该订单！', 'danger')
        return redirect(url_for('home'))
    
    screening = Screening.query.get(order.screening_id)
    movie = Movie.query.get(screening.movie_id)
    hall = Hall.query.get(screening.hall_id)
    cinema = Cinema.query.get(hall.cinema_id)
    
    order_seats = OrderSeat.query.filter_by(order_id=order_id).all()
    seats = []
    for order_seat in order_seats:
        seat = Seat.query.get(order_seat.seat_id)
        seats.append(seat)
    
    return render_template('order_confirmation.html', order=order, screening=screening, movie=movie, hall=hall, cinema=cinema, seats=seats)

# 支付订单
@app.route('/order/<int:order_id>/pay', methods=['POST'])
@login_required
def pay_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.user_id:
        flash('无权操作该订单！', 'danger')
        return redirect(url_for('home'))
    
    if order.status != 'pending':
        flash('订单状态错误！', 'danger')
        return redirect(url_for('order_confirmation', order_id=order_id))
    
    order.status = 'paid'
    order.payment_method = 'online'
    order.transaction_id = f'TX{datetime.now().strftime("%Y%m%d%H%M%S")}{order_id}'
    
    db.session.commit()
    flash('订单支付成功！', 'success')
    return redirect(url_for('order_confirmation', order_id=order_id))

# 用户中心
@app.route('/user/profile')
@login_required
def user_profile():
    orders = Order.query.filter_by(user_id=current_user.user_id).order_by(Order.order_time.desc()).all()
    return render_template('user_center.html', user=current_user, orders=orders)

# 订单详情
@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.filter_by(order_id=order_id, user_id=current_user.user_id).first_or_404()
    
    # 获取订单相关信息
    screening = Screening.query.get(order.screening_id)
    movie = Movie.query.get(screening.movie_id)
    hall = Hall.query.get(screening.hall_id)
    cinema = Cinema.query.get(hall.cinema_id)
    
    # 获取订单座位
    order_seats = OrderSeat.query.filter_by(order_id=order_id).all()
    seats = []
    for order_seat in order_seats:
        seat = Seat.query.get(order_seat.seat_id)
        seats.append(seat)
    
    return render_template('order_detail.html', 
                        order=order, 
                        screening=screening, 
                        movie=movie, 
                        hall=hall, 
                        cinema=cinema, 
                        seats=seats)

# 编辑个人资料
@app.route('/user/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # 更新用户信息
        current_user.real_name = request.form.get('real_name', current_user.real_name)
        current_user.phone = request.form.get('phone', current_user.phone)
        
        # 处理头像上传
        if 'avatar' in request.files:
            avatar_file = request.files['avatar']
            if avatar_file and avatar_file.filename != '':
                # 保存头像文件
                filename = f"avatar_{current_user.user_id}_{int(datetime.now().timestamp())}.png"
                avatar_path = os.path.join(app.root_path, 'static', 'images', filename)
                avatar_file.save(avatar_path)
                current_user.avatar = filename
        
        db.session.commit()
        flash('个人资料更新成功！', 'success')
        return redirect(url_for('user_profile'))
    
    return render_template('edit_profile.html', user=current_user)

# 注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在！', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册！', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('两次密码不一致！', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user = User(username=username, email=email, password=hashed_password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功！请登录', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 同时支持用户名和邮箱登录
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('登录失败！用户名或密码错误', 'danger')
    
    return render_template('login.html')

# 退出登录
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# 发布影评
@app.route('/movie/<int:movie_id>/review', methods=['POST'])
@login_required
def add_review(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    
    rating = int(request.form['rating'])
    content = request.form['content']
    
    # 检查用户是否已评论过该电影
    existing_review = Review.query.filter_by(user_id=current_user.user_id, movie_id=movie_id).first()
    if existing_review:
        flash('您已经评论过这部电影！', 'warning')
        return redirect(url_for('movie_detail', movie_id=movie_id))
    
    review = Review(
        user_id=current_user.user_id,
        movie_id=movie_id,
        rating=rating,
        content=content
    )
    
    db.session.add(review)
    db.session.commit()
    
    # 更新电影评分
    reviews = Review.query.filter_by(movie_id=movie_id).all()
    avg_rating = sum(review.rating for review in reviews) / len(reviews)
    movie.rating = round(avg_rating, 1)
    
    db.session.commit()
    
    flash('影评发布成功！', 'success')
    return redirect(url_for('movie_detail', movie_id=movie_id))

# 点赞影评
@app.route('/review/<int:review_id>/like', methods=['POST'])
@login_required
def like_review(review_id):
    review = Review.query.get_or_404(review_id)
    
    existing_like = ReviewLike.query.filter_by(user_id=current_user.user_id, review_id=review_id).first()
    
    if existing_like:
        # 取消点赞
        db.session.delete(existing_like)
        review.likes -= 1
        db.session.commit()
        return jsonify({'status': 'unliked', 'likes': review.likes})
    else:
        # 点赞
        like = ReviewLike(user_id=current_user.user_id, review_id=review_id)
        db.session.add(like)
        review.likes += 1
        db.session.commit()
        return jsonify({'status': 'liked', 'likes': review.likes})

# 取消订单
@app.route('/order/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.user_id:
        flash('无权操作该订单！', 'danger')
        return redirect(url_for('home'))
    
    if order.status != 'pending':
        flash('订单状态错误！', 'danger')
        return redirect(url_for('order_confirmation', order_id=order_id))
    
    order.status = 'cancelled'
    db.session.commit()
    flash('订单已取消！', 'success')
    return redirect(url_for('user_profile'))

# 运行应用
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)