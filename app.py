import sqlite3
import time

from sqlalchemy import exc
from flask import Flask, render_template, request, flash, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gfdgfdkgfdjfgd7fddjfd'
# Авторизация
login_manager = LoginManager(app)


class UserLogin():
    def fromDB(self, user_id):
        self.__user = get_user_by_id(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user[0].id)


@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return UserLogin().fromDB(user_id)


# База данных
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///pharmacy.db"
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(500), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<users {self.id}>"


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(500), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<users {self.id}>"


# функций баз данных

def init_db():
    """
    Функция создания всех таблиц в базе данных
    :return:
    """
    with app.app_context():
        db.create_all()


def add_user(email, hash):
    try:
        u = Users(email=email, password=hash)
        db.session.add(u)
        db.session.commit()
        return (1, True)
    except exc.SQLAlchemyError as e:

        db.session().rollback()
        print("Ошибка при добавлений пользователя в БД")
        print(e)
        print('error-code:', e.code)
        return (e.code, False)


def get_user_by_id(id):
    try:

        user = Users.query.filter_by(id=id).all()
        return user
    except exc.SQLAlchemyError as e:

        db.session().rollback()
        print("Ошибка при Поиске пользователя в БД по id")
        print(e)
        print('error-code:', e.code)
        return False


def get_user_by_email(email):
    """
    Функция поиска по еmail администратора или юзера
    если найден администратор возвращается запись администратора и флаг 1
    если найден юзер возвращается запись администратора и флаг 1
    :param email:
    :return:
    """
    try:
        user = Users.query.filter_by(email=email).all()
        return user


    except exc.SQLAlchemyError as e:

        db.session().rollback()
        print("Ошибка при Поиске пользователя в БД по email")
        print(e)
        print('error-code:', e.code)
        return False


# роуты
@app.route('/')
def main():
    return render_template('main.html')


@app.route('/reg', methods=['POST', 'GET'])
def reg():
    if request.method == 'POST':
        if len(request.form['email']) > 4 and request.form['password'] == request.form['repeat_password'] and len(
                request.form['password']) > 5:
            error_code, res_operation = add_user(request.form['email'],
                                                 generate_password_hash(request.form['password']))
            if (res_operation):
                return redirect('auth')
            else:
                if (error_code == 'gkpj'):
                    user = Users.query.filter_by(email=request.form['email']).all()
                    date = user[0].date.date()
                    flash(f"Вы уже были зарегистрированы\n дата регистраций:\n{date}")
                    return redirect('auth')
        elif len(request.form['email']) <= 4:
            flash(f'Email должен содержать больше 4 символов.Длинна вашего email: {len(request.form["email"])}')
        elif request.form['password'] != request.form['repeat_password']:
            flash('Пароли не совпадают')
        elif len(request.form['password']) <= 5:
            flash(f'Пароль должен содержать больше 5 символов.Длинна вашего Пароля: {len(request.form["password"])}')
        else:
            flash(f'Что-то пошло нет так..Может вы уже зарегистрированы?')
    return render_template('reg.html')


@app.route('/auth', methods=['POST', 'GET'])
def auth():
    # todo:Продумать авторизацию администратора
    if request.method == "POST":
        user = get_user_by_email(request.form['email'])

        if user and check_password_hash(user[0].password, request.form["password"]):
            userlogin = UserLogin().create(user)

            login_user(userlogin)
            return redirect(url_for("main"))
        flash("Неверная пара логин/Пароль", 'error')
    return render_template('auth.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main'))


if __name__ == "__main__":
    app.run(debug=True)
