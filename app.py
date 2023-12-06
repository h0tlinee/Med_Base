import sqlite3
import time

from sqlalchemy import exc,update
from flask import Flask, render_template, request, flash, redirect, url_for, json, jsonify
from datetime import datetime
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)

app.config['SECRET_KEY'] = 'gfdgfdkgfdjfgd7fddjfd'
# Авторизация
login_manager = LoginManager(app)
login_manager.login_view='auth'


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

    def is_admin(self):
        return self.__user.adm_flag

    def get_id(self):
        return str(self.__user.id)



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
    adm_flag = db.Column(db.Boolean, nullable=True)

    def __repr__(self):
        return f"<users {self.id}>"

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    structure = db.Column(db.String(100), nullable=False)
    date_of_manufacture = db.Column(db.Date, nullable=False)
    storage_life = db.Column(db.Integer, nullable=False)
    pic_url = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<items {self.id}>"

class Basket(db.Model):
    
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    basket=db.Column(db.String(300))
    
upd=update(Basket)

# функций баз данных

def init_db():
    """
    Функция создания всех таблиц в базе данных
    :return:
    """
    with app.app_context():
        db.create_all()


def add_item(name, price, description, structure, date_of_manufacture, storage_life, pic_url):
    try:

        item = Item(name=name, price=price, description=description, structure=structure,
                    date_of_manufacture=date_of_manufacture, storage_life=storage_life, pic_url=pic_url)
        db.session.add(item)
        db.session.commit()
        return (1, True)
    except exc.SQLAlchemyError as e:
        db.session().rollback()
        print("Ошибка при добавлений пользователя в БД")
        print(e)
        print('error-code:', e.code)
        return (e.code, False)


def get_item_by_id(id):
    try:

        item = Item.query.filter_by(id=id).all()
        return item[0]
    except exc.SQLAlchemyError as e:

        db.session().rollback()
        print("Ошибка при Поиске товара в БД по id")
        print(e)
        print('error-code:', e.code)
        return False


def add_user(email, hash):
    try:
        u = Users(email=email, password=hash,adm_flag=False)
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
        return user[0]
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
        return user[0]


    except exc.SQLAlchemyError as e:

        db.session().rollback()
        print("Ошибка при Поиске пользователя в БД по email")
        print(e)
        print('error-code:', e.code)
        return False

def add_admin():
    try:
        u = Users(email="admin@mail.ru", password=generate_password_hash('123456'), adm_flag=True)
        db.session.add(u)
        db.session.commit()
        return (1, True)
    except exc.SQLAlchemyError as e:

        db.session().rollback()
        print("Ошибка при добавлений админа в БД")
        print(e)
        print('error-code:', e.code)
        return (e.code, False)
    
    
def add_user_basket(basket):
    try:
        if(db.session.query(Basket.user_id).filter_by(user_id=current_user.get_id()).first() is not None):
            print('TEST exist')
            i=db.session.query(Basket).get(current_user.get_id())
            i.basket=json.dumps(basket)
            db.session.add(i)
            db.session.commit()
            
            
        else:
            print('test not exist')
            user_id=current_user.get_id()
            u = Basket(user_id=user_id,basket=json.dumps(basket))
            db.session.add(u)
            db.session.commit()
            return (1, True)
    except exc.SQLAlchemyError as e:

        db.session().rollback()
        print("Ошибка при добавлений корзины в БД")
        print(e)
        print('error-code:', e.code)
        return (e.code, False)
    
#def get_basket_by_id(id):
        

# для работы с корзиной

basket = {}


# считает общее кол-во товаров в корзине
def sum_quantity(basket, items):
    sum = 0
    for key in basket.keys():
        for item in items:
            # print(item.id)
            # print(item.price)
            if key == item.id:
                # print('ok')
                sum = sum + basket.get(key)
    return sum


# считает сумму всех выбранных товаров, basket-словарь корзина, items-словарь всех товаров, просто перебираем)))
def sum_price(basket, items):
    sum = 0
    # print(items)
    for key in basket.keys():
        for item in items:
            # print(item.id)
            # print(item.price)
            if int(key) == item.id:
                # print('ok')
                sum = sum + basket.get(key) * item.price
    return sum


def delete_from_basket(item_code, basket):
    for i in basket:
        del basket[item_code]
    return basket


@app.route('/', methods=['POST', 'GET'])
def main():
    items = Item.query.all()  # получаем все товары
    
    # if (current_user.is_authenticated()):
    #     print("Это админ? ",current_user.is_admin())
    #add_item(5,"Гематоген",69,"Биологически активная добавка с добавлением железа","Сахар, молоко цельное сгущенное с сахаром, патока крахмальная, альбумин черный пищевой, мед, «Виролизин-С» (лизина гидрохлорид), ароматизатор натуральный «Ваниль», вода очищенная",date(2022,12,25),365,"/img/gematogen.jpeg")
    
    return render_template('main.html', items=items, basket=basket, sum_price=sum_price, sum_quantity=sum_quantity)


@app.route('/add_to_basket', methods=['POST', 'GET'])
@login_required
def add_to_basket():
    if (int(request.form['quantity']) < 1):
        flash(f"Вы пытаетесь добавить 0 либо отрицательное число товаров в корзину!")
        return redirect(url_for('main', basket=basket))
    id = int(request.form['item_code'])
    qu = int(request.form['quantity'])

    if (basket.get(id)):
        basket[id] = qu + basket.get(id)
    else:
        basket[id] = qu
    return redirect(url_for('main', basket=basket))


@app.route('/delete_from_basket', methods=['POST', 'GET'])
def delete_from_basket():

    id = int(request.form['item_code'])
    del basket[id]

    return redirect(url_for('main', basket=basket))



@app.route('/add_basket', methods=['POST', 'GET'])
@login_required
def to_basket():
    print(basket)
    add_user_basket(basket)
    
    return redirect(url_for('basket_', basket=basket, print=print))

@app.route('/to_basket',methods=['POST', 'GET'])
def basket_():
    bsk=Basket.query.filter_by(user_id=current_user.get_id()).all()
    items=Item.query.all()
    print(bsk[0].basket)
    bsk_=bsk[0].basket
    res=json.loads(bsk_)
    return render_template('basket.html',  print=print,res=res,int=int,Item=Item,str=str,items=items,sum_price=sum_price)

@app.route('/pay',methods=['POST', 'GET'])
def pay():
    return render_template('payment.html')


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

        if user and check_password_hash(user.password, request.form["password"]):
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            return redirect(url_for("main"))
        flash("Неверная пара логин/Пароль", 'error')
    return render_template('auth.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))

@app.route('/add_item', methods=['POST', 'GET'])
def add_item1():
    if request.method == 'POST':

        print(request.form['date_item'] , type(request.form['date_item']))
        date1=request.form['date_item'].split('-')
        print(date)
        add_item(name=request.form['name_item'],
                 price=int(request.form['price']),
                 description=request.form['description'],
                 structure=request.form['composition'],
                 date_of_manufacture=date(int(date1[0]),int(date1[1]),int(date1[2])),
                 storage_life=int(request.form['expiration_date']),
                 pic_url=request.form['img_file_path'])
        flash("Товар успешно добавлен")
    return render_template('add_item.html')


if __name__ == "__main__":
    app.run(debug=True)