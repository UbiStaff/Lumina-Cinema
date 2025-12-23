from app import app
from models import db, User, Movie, Cinema, Hall, Screening, Seat
from datetime import datetime, timedelta

with app.app_context():
    # 创建数据库表
    db.create_all()
    
    # 添加测试电影
    if not Movie.query.first():
        # 当前上线的10部电影
        movies_data = [
            {
                'title': '流浪地球3',
                'director': '郭帆',
                'actors': '吴京, 刘德华, 李雪健, 沙溢',
                'genre': '科幻',
                'duration': 170,
                'release_date': datetime.now().date(),
                'description': '太阳危机爆发，人类开启流浪地球计划，联合政府决定启用“方舟计划”，带领人类寻找新家园。在这场横跨宇宙的旅程中，人类将面临前所未有的挑战。',
                'poster': 'https://placehold.co/250x350/1E90FF/FFFFFF?text=流浪地球3'
            },
            {
                'title': '疯狂动物城2',
                'director': '拜伦·霍华德',
                'actors': '金妮弗·古德温, 杰森·贝特曼, 伊德里斯·艾尔巴',
                'genre': '动画',
                'duration': 125,
                'release_date': datetime.now().date(),
                'description': '兔朱迪和狐尼克将继续在动物城展开新的冒险，他们将面对更大的阴谋和挑战，同时探索动物城不为人知的秘密。',
                'poster': 'https://placehold.co/250x350/FF6B6B/FFFFFF?text=疯狂动物城2'
            },
            {
                'title': '复仇者联盟6',
                'director': '乔·罗素',
                'actors': '小罗伯特·唐尼, 克里斯·埃文斯, 斯嘉丽·约翰逊',
                'genre': '动作',
                'duration': 180,
                'release_date': datetime.now().date(),
                'description': '复仇者联盟再次集结，面对来自多元宇宙的威胁。他们必须超越时空，拯救整个宇宙免受毁灭。',
                'poster': 'https://placehold.co/250x350/4ECDC4/FFFFFF?text=复仇者联盟6'
            },
            {
                'title': '哈利·波特与被诅咒的孩子',
                'director': '大卫·叶茨',
                'actors': '丹尼尔·雷德克里夫, 艾玛·沃特森, 鲁伯特·格林特',
                'genre': '奇幻',
                'duration': 160,
                'release_date': datetime.now().date(),
                'description': '哈利·波特与被诅咒的孩子讲述了哈利·波特与儿子阿不思·西弗勒斯·波特的故事，他们将面对新的黑魔法威胁。',
                'poster': 'https://placehold.co/250x350/45B7D1/FFFFFF?text=哈利波特'
            },
            {
                'title': '速度与激情12',
                'director': '路易斯·莱特里尔',
                'actors': '范·迪塞尔, 杰森·莫玛, 米歇尔·罗德里格兹',
                'genre': '动作',
                'duration': 140,
                'release_date': datetime.now().date(),
                'description': '多米尼克·托莱多和他的团队将再次面对新的挑战，这次他们将跨越全球，展开一场前所未有的速度与激情。',
                'poster': 'https://placehold.co/250x350/FF9F43/FFFFFF?text=速度与激情12'
            },
            {
                'title': '阿凡达3：带种者',
                'director': '詹姆斯·卡梅隆',
                'actors': '萨姆·沃辛顿, 佐伊·索尔达娜, 西格妮·韦弗',
                'genre': '科幻',
                'duration': 190,
                'release_date': datetime.now().date(),
                'description': '杰克·萨利和奈蒂莉的孩子将在潘多拉星球上成长，他们将面对来自人类的新威胁，同时探索潘多拉星球不为人知的秘密。',
                'poster': 'https://placehold.co/250x350/26DE81/FFFFFF?text=阿凡达3'
            },
            {
                'title': '碟中谍8',
                'director': '克里斯托夫·迈考利',
                'actors': '汤姆·克鲁斯, 海莉·阿特维尔, 文·瑞姆斯',
                'genre': '动作',
                'duration': 150,
                'release_date': datetime.now().date(),
                'description': '伊森·亨特和IMF团队将再次展开全球性的冒险，他们必须阻止一个威胁世界安全的巨大阴谋。',
                'poster': 'https://placehold.co/250x350/FF3838/FFFFFF?text=碟中谍8'
            },
            {
                'title': '蜘蛛侠：超越宇宙',
                'director': '乔伊姆·多斯·桑托斯',
                'actors': '沙梅克·摩尔, 海莉·斯坦菲尔德, 奥斯卡·伊萨克',
                'genre': '动画',
                'duration': 130,
                'release_date': datetime.now().date(),
                'description': '迈尔斯·莫拉莱斯将再次穿越多元宇宙，与不同版本的蜘蛛侠一起面对新的威胁，同时探索自己的身份认同。',
                'poster': 'https://placehold.co/250x350/7158E2/FFFFFF?text=蜘蛛侠：超越宇宙'
            },
            {
                'title': '霸王别姬',
                'director': '陈凯歌',
                'actors': '张国荣, 巩俐, 张丰毅',
                'genre': '剧情',
                'duration': 171,
                'release_date': datetime.now().date(),
                'description': '电影讲述了程蝶衣和段小楼两位京剧演员半个世纪的命运纠葛，展现了中国传统文化的魅力和人性的复杂。',
                'poster': 'https://placehold.co/250x350/3742FA/FFFFFF?text=霸王别姬'
            },
            {
                'title': '星际穿越2',
                'director': '克里斯托弗·诺兰',
                'actors': '马修·麦康纳, 安妮·海瑟薇, 杰西卡·查斯坦',
                'genre': '科幻',
                'duration': 185,
                'release_date': datetime.now().date(),
                'description': '人类继续探索宇宙的奥秘，面对新的时空挑战和未知的外星文明，寻找人类的未来。',
                'poster': 'https://placehold.co/250x350/10AC84/FFFFFF?text=星际穿越2'
            }
        ]
        
        for movie_data in movies_data:
            movie = Movie(**movie_data)
            db.session.add(movie)
        db.session.commit()
        print('添加10部测试电影成功！')
    
    # 添加测试影院
    if not Cinema.query.first():
        cinemas = [
            {
                'name': '万达影城',
                'address': '北京市朝阳区建国路93号万达购物中心',
                'phone': '010-12345678'
            },
            {
                'name': '大地影院',
                'address': '北京市海淀区中关村大街1号海龙大厦',
                'phone': '010-87654321'
            },
            {
                'name': '星美影城',
                'address': '北京市东城区王府井大街138号',
                'phone': '010-135792468'
            }
        ]
        
        for cinema_data in cinemas:
            cinema = Cinema(**cinema_data)
            db.session.add(cinema)
        db.session.commit()
        print('添加3家测试影院成功！')
    
    # 添加测试放映厅
    if not Hall.query.first():
        # 为每家影院添加3个放映厅
        for cinema_id in range(1, 4):
            for hall_num in range(1, 4):
                hall = Hall(
                    cinema_id=cinema_id,
                    name=f'{hall_num}号厅',
                    total_seats=100,
                    rows=10,
                    cols=10
                )
                db.session.add(hall)
        db.session.commit()
        print('添加9个测试放映厅成功！')
    
    # 添加测试座位
    if not Seat.query.first():
        # 为每个放映厅添加座位
        for hall_id in range(1, 10):
            for row in range(10):
                for col in range(10):
                    seat = Seat(
                        hall_id=hall_id,
                        seat_row=chr(65+row),  # A, B, C...
                        seat_col=col+1,        # 1, 2, 3...
                        type='regular'
                    )
                    db.session.add(seat)
        db.session.commit()
        print('添加所有测试座位成功！')
    
    # 添加测试场次
    if not Screening.query.first():
        # 获取所有电影和放映厅
        movies = Movie.query.all()
        halls = Hall.query.all()
        
        # 为每个电影添加多个场次
        for movie in movies:
            # 为每个放映厅添加场次
            for hall in halls:
                # 未来3天内的场次
                for day in range(3):
                    # 每天添加5个场次
                    for hour in range(10, 22, 2):
                        start_time = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0) + timedelta(days=day)
                        end_time = start_time + timedelta(minutes=movie.duration)
                        
                        screening = Screening(
                            movie_id=movie.movie_id,
                            hall_id=hall.hall_id,
                            start_time=start_time,
                            end_time=end_time,
                            price=50 + (hour % 4) * 10,  # 不同时间段不同价格
                            remaining_seats=hall.total_seats,
                            status='upcoming'
                        )
                        db.session.add(screening)
        
        db.session.commit()
        print('添加所有测试场次成功！')
    
    print('所有测试数据添加完成！')