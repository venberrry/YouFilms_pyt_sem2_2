import os
import random
import string

from werkzeug.utils import secure_filename

from YouFilmsPython.forms import ReviewFormCreate, LoginForm, ProfileForm, SerialReviewFormCreate
from app import app, just_session, db, mail
from models.models import Film, Serial, FilmReview, SerialReview, User, Profile
from flask import render_template, request, redirect, url_for, abort, make_response, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message

extensions = {'png', 'jpg'}
UPLOAD_FOLDER = 'static/users_photos'

'''
Вспомогательные функции
'''
def generate_verification_code(length=5):
    """
        Генерирует случайный код подтверждения из букв и цифр заданной длины.

        :param length: Длина кода подтверждения
        :return: Строка с кодом
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

def send_confirmation_email(email, code):
    """
        Отправляет письмо с кодом подтверждения на указанный email.

        :param email: Email адрес получателя
        :param code: Код подтверждения для отправки
    """
    try:
        msg = Message(
            "Confirm your email",
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )
        msg.body = f"Your confirmation code is {code}."
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")

'''
ОСНОВНОЙ БЛОК СТРАНИЦ
'''

@app.route('/', methods=['GET', 'POST'])
def film_list():
    """
        Обрабатывает главную страницу, отображающую список фильмов.
    """
    films = db.session.execute(db.select(Film)).scalars().all()
    return render_template("HomePage.html", films=films)

@app.route('/film/<int:film_id>', methods=['GET', 'POST'])
def film(film_id):
    """
        Обрабатывает страницу конкретного фильма, отображает детали фильма и отзывы к нему.

        :param film_id: ID фильма для отображения
    """
    film_obj = db.session.query(Film).filter_by(fid=film_id).first()
    if not film_obj:
        return redirect(url_for('main_page'))  # Если фильм не найден, перенаправляем на главную страницу

    reviews = db.session.query(FilmReview).filter_by(film_id=film_id).all()
    review_commentator_pairs = []
    for review in reviews:
        commentator = db.session.query(Profile, User).join(User).filter(Profile.pid == review.profile_id).first()
        review_commentator_pairs.append({"review": review, "commentator": commentator})
        print(review_commentator_pairs)
        for pair in review_commentator_pairs:
            profile = pair['commentator'][0]  # Получение объекта Profile
            user = pair['commentator'][1]  # Получение объекта User
            print("Profile ID:", profile.pid)
            print("User Login:", user.login)
            print("Avatar:", profile.avatar)
            print("Email:", profile.email)
            print("Bio:", profile.bio)
            print(dir(profile))

    form = ReviewFormCreate()
    form.film_id.data = film_id
    form.profile_id.data = just_session['uid']
    if form.validate_on_submit() and request.method == 'POST':
        short_text = form.title.data
        long_text = form.review_text.data
        stars_value = form.rating.data

        new_review = FilmReview(
            profile_id=just_session['uid'],
            film_id=film_id,
            title=short_text,
            review_text=long_text,
            rating=int(stars_value)
        )
        db.session.add(new_review)
        db.session.commit()

        # Обновляем информацию о фильме
        film_obj.amount_rating += 1
        film_obj.average_rating = db.session.query(db.func.avg(FilmReview.rating)).filter(FilmReview.film_id == film_id).scalar()
        film_obj.average_rating = round(film_obj.average_rating, 1)
        db.session.commit()
        return redirect(url_for('film', film_id=film_id))

    return render_template("FilmPage.html", film_obj=film_obj, review_commentator_pairs=review_commentator_pairs, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
        Обрабатывает страницу входа в систему, аутентифицирует пользователя.
    """
    form = LoginForm()
    warning = None
    if form.validate_on_submit():
        username = form.username.data.lower()
        password = form.password.data

        # Проверка наличия пользователя в базе данных
        user = db.session.query(User).filter_by(login=username).first()

        if user:
            # Проверка пароля
            if check_password_hash(user.password, password):
                # Авторизация успешна
                just_session['auth'] = True
                just_session['login'] = username
                just_session['counter'] = just_session.get('counter', 0)
                just_session['uid'] = user.uid
                return redirect(url_for("profile"))
            else:
                warning = "Пароль неверный"
        else:
            # Создание нового пользователя
            password_hash = generate_password_hash(password)
            new_user = User(login=username, password=password_hash)
            db.session.add(new_user)
            db.session.commit()

            # Создание профиля для нового пользователя
            new_profile = Profile(user_id=new_user.uid)
            db.session.add(new_profile)
            db.session.commit()

            just_session['auth'] = True
            just_session['login'] = username
            just_session['counter'] = 0
            just_session['uid'] = new_user.uid
            return redirect(url_for("profile"))


    return render_template("LoginPage.html", form=form, warning=warning)


def is_login():
    '''
    Добавляет количество входов (отображается в профиле)add *
    '''
    if 'counter' in just_session:
        just_session['counter'] += 1


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """
            Выход пользователя из системы, очищает сессию.
    """
    just_session.pop('auth')
    return redirect(url_for('film_list'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """
        Обрабатывает страницу профиля пользователя, показывает данные пользователя и форму для их редактирования.
    """
    warn = just_session.pop('warn', None)

    user = db.session.query(User).filter_by(uid=just_session['uid']).first()
    profile_obj = db.session.query(Profile).filter_by(user_id=just_session['uid']).first()
    if user:
        just_session['login'] = user.login
    form = ProfileForm()
    form.user_id = just_session['uid']
    form.email.data = profile_obj.email
    form.avatar.data = profile_obj.avatar
    form.bio.data = profile_obj.bio
    form.name.data = user.login
    return render_template("ProfilePage.html", profile_obj=profile_obj, user_data=user, warn=warn, form=form)


@app.route('/create_film', methods=['GET', 'POST'])
def create_film():
    """
        Обрабатывает страницу создания нового фильма, сохраняет информацию о фильме в базе данных.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        engname = request.form.get('engname')
        genres = request.form.get('genres')
        year_of_release = request.form.get('year_of_release')
        county = request.form.get('county')
        mpaa = request.form.get('mpaa')
        time_duration = request.form.get('time_duration')
        description = request.form.get('description')
        director = request.form.get('director')
        file = request.files['poster']

        if file:
            ext = file.filename.split('.')[-1]
            if ext in extensions:
                filename = f"poster_{just_session['uid']}.{ext}"
                relative_path = os.path.join('users_photos', filename)

                # Создаем новый фильм и добавляем его в базу данных
                new_film = Film(
                    name=name,
                    engname=engname,
                    poster=relative_path,
                    genres=genres,
                    year_of_release=year_of_release,
                    county=county,
                    mpaa=mpaa,
                    time_duration=time_duration,
                    description=description,
                    director=director
                )
                db.session.add(new_film)
                db.session.commit()

                # Сохраняем файл куда надо по фласку
                file.save(os.path.join(app.static_folder, relative_path))

        return redirect(url_for('film_list'))
    return render_template("FilmCreatePage.html")

@app.route('/update_profile', methods=['POST'])
def update_profile():
    """
        Обрабатывает страницу обновления профиля пользователя, обновляет информацию о профиле в базе данных.
    """
    if request.method == 'POST':
        just_session['warn'] = None
        new_name = request.form.get('name')
        new_email = request.form.get('email')
        new_bio = request.form.get('bio')

        if 'file_uploading' in request.files:
            file = request.files['file_uploading']
            if file:
                ext = file.filename.split('.')[-1]
                if ext in extensions:
                    filename = f"image_{just_session['uid']}.{ext}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    relative_path = os.path.join('users_photos', filename)

                    user_profile = db.session.query(Profile).filter_by(user_id=just_session['uid']).first()
                    user_profile.avatar = relative_path
                    db.session.commit()

                    file.save(file_path)

        if new_name:
            user = db.session.query(User).filter(User.login == new_name, User.uid != just_session['uid']).first()
            if user:
                warn = 'Пользователь с таким именем уже существует'
                just_session['warn'] = warn
                return redirect(url_for('profile'))
            else:
                # Обновление имени пользователя в базе данных
                user = db.session.query(User).filter_by(uid=just_session['uid']).first()
                user.login = new_name
                db.session.commit()

        if new_email:
            user_profile = db.session.query(Profile).filter_by(user_id=just_session['uid']).first()
            user_profile.email = new_email
            db.session.commit()

        if new_bio:
            user_profile = db.session.query(Profile).query.filter_by(user_id=just_session['uid']).first()
            user_profile.bio = new_bio
            db.session.commit()

    return redirect(url_for('profile'))

"""
Блок с роутингом к сериалам
Сериалы взяты из стороннего источника 
"""

@app.route('/series', methods=['GET'])
def series():
    serials = db.session.query(Serial).all()
    return render_template("SeriesPage.html", serials=serials)

@app.route('/serial/<int:serial_id>', methods=['GET', 'POST'])
def serial(serial_id):
    """
        Обрабатывает страницу сериала, отображает информацию о сериале и отзывы о нем.
    """
    serial = db.session.query(Serial).filter_by(sid=serial_id).first()
    if not serial:
        return redirect(url_for('main_page'))  # Если сериал не найден, перенаправляем на главную страницу

    reviews = db.session.query(SerialReview).filter_by(serial_id=serial_id).all()
    review_commentator_pairs = []
    for review in reviews:
        commentator = db.session.query(Profile, User).join(User).filter(Profile.pid == review.profile_id).first()
        review_commentator_pairs.append({"review": review, "commentator": commentator})

    form = SerialReviewFormCreate()
    form.serial_id.data = serial_id
    form.profile_id.data = just_session['uid']  # Убедитесь, что сессия содержит 'uid'
    if form.validate_on_submit() and request.method == 'POST':
        new_review = SerialReview(
            profile_id=form.profile_id.data,
            serial_id=form.serial_id.data,
            title=form.title.data,
            review_text=form.review_text.data,
            rating=form.rating.data
        )
        db.session.add(new_review)
        db.session.commit()

        # Обновляем информацию о сериале
        serial.amount_rating += 1
        serial.average_rating = db.session.query(db.func.avg(SerialReview.rating)).filter(SerialReview.serial_id == serial_id).scalar()
        serial.average_rating = round(serial.average_rating, 1)
        db.session.commit()
        return redirect(url_for('serial', serial_id=serial_id))

    return render_template("SeriesObjectPage.html", serial=serial, review_commentator_pairs=review_commentator_pairs, form=form)

'''
Блок со сменой полей в форме редактирования профиля
'''

@app.route('/update_name', methods=['POST'])
def update_name():
    """
        Обрабатывает обновление профиля пользователя, включая имя
        """
    new_name = request.form.get('name')
    if new_name:
        # Проверяем, не занято ли новое имя другим пользователем
        user_exists = db.session.query(User).filter(User.login == new_name, User.uid != just_session['uid']).first()
        if user_exists:
            # Если имя занято, ничего не делаем
            return redirect(url_for('profile'))
        else:
            # Обновляем имя пользователя в базе данных
            user = db.session.query(User).filter_by(uid=just_session['uid']).first()
            user.login = new_name
            db.session.commit()
            return redirect(url_for('profile'))
    return redirect(url_for('profile'))

@app.route('/update_bio', methods=['POST'])
def update_bio():
    """
        Обрабатывает обновление профиля пользователя, включая био
    """
    new_bio = request.form.get('bio')
    if new_bio:
        # Обновляем био в профиле пользователя
        user_profile = db.session.query(Profile).filter_by(user_id=just_session['uid']).first()
        user_profile.bio = new_bio
        db.session.commit()
        return redirect(url_for('profile'))
    return redirect(url_for('profile'))

@app.route('/confirm_email_page', methods=['GET'])
def confirm_email_page():
    '''
    Страница подтверждения email
    '''
    print("тут2")
    return render_template('ConfirmEmail.html')


@app.route('/change_email_request', methods=['POST'])
def change_email_request():
    '''
    Обрабатывает запрос на изменение email
    '''
    new_email = request.form.get('email').strip()  # Получаем новый email из формы
    if new_email:
        # Проверяем, существует ли уже такой email в базе данных
        existing_user = db.session.query(Profile).filter_by(email=new_email).first()
        if existing_user:
            # Если пользователь с таким email уже существует, возвращаем на страницу профиля с предупреждением
            flash('Этот email уже используется.', 'error')
            return redirect(url_for('profile'))

        # Если email уникален, продолжаем процесс подтверждения
        confirmation_code = generate_verification_code()
        send_confirmation_email(new_email, confirmation_code)
        just_session['new_email'] = new_email
        just_session['confirmation_code'] = confirmation_code
        return redirect(url_for('confirm_email_page'))

    return redirect(url_for('profile'))


@app.route('/confirm_email', methods=['POST'])
def confirm_email():
    '''
    Обрабатывает подтверждение email
    '''
    user_code = request.form.get('code')
    if user_code == just_session.get('confirmation_code'):
        # Если код подтверждения совпадает, обновляем email в базе данных
        user_profile = db.session.query(Profile).filter_by(user_id=just_session['uid']).first()
        user_profile.email = just_session['new_email']
        db.session.commit()
        return redirect(url_for('profile'))
    else:
        # Если код не совпадает, возвращаем на страницу ввода кода
        return redirect(url_for('ConfirmEmail.html'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extensions


@app.route('/update_avatar', methods=['POST'])
def update_avatar():
    """
        Обрабатывает обновление профиля пользователя, включая аватар
    """
    if 'avatar' in request.files:
        file = request.files['avatar']
        if file.filename != '':
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Путь для сохранения файла внутри директории static
                avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                # Полный путь для сохранения файла на диске
                full_path = os.path.join(app.static_folder, avatar_path)

                # Убедитесь, что директория существует, если нет, создайте её
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                file.save(full_path)

                user_profile = db.session.query(Profile).filter_by(user_id=just_session['uid']).first()
                if user_profile:
                    # Сохраняем относительный путь в базу данных
                    user_profile.avatar = avatar_path
                    db.session.commit()
                    return redirect(url_for('profile'))
                else:
                    flash('Профиль пользователя не найден.', 'error')
            else:
                flash('Недопустимый формат файла.', 'error')
        else:
            flash('Файл не выбран.', 'error')
    return redirect(url_for('profile'))

@app.route('/delete_profile', methods=['POST'])
def delete_profile():
    """
    Удаляет профиль пользователя и связанные с ним отзывы
    """
    user_id = just_session.get('uid')
    if user_id:
        # Удаление связанных отзывов
        db.session.query(FilmReview).filter_by(profile_id=user_id).delete()
        # Удаление профиля пользователя
        db.session.query(Profile).filter_by(user_id=user_id).delete()
        # Удаление пользователя
        user = db.session.query(User).get(user_id)
        db.session.delete(user)
        db.session.commit()
        just_session.clear()
        return redirect(url_for('film_list'))
    else:
        return 'Ошибка: Пользователь не найден', 404


'''
Блок с помощью (вебсокеты)
'''
@app.route('/support')
def support():
    return render_template("SupportPage.html")