import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))  # Добавляем App в пути

from flask import Flask, render_template, url_for, redirect, request, flash, session
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
import os
from joblib import load
from sklearn.linear_model import LogisticRegressionCV , LogisticRegression
from database.models import Iris, User
from database.database import SyncSessionLocal


app = Flask(__name__)
Bootstrap(app)

app.config['SECRET_KEY'] = os.urandom(24)

def get_db_session():
    return SyncSessionLocal()


@app.route('/')
def index():
    with get_db_session() as db_session:
        all_irises = db_session.query(Iris).all()
        return render_template("index.html", all_irises=all_irises)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        user_name = request.form['user_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Пароли не совпадают! Попробуйте снова', 'danger')
            return render_template('register.html')

        with get_db_session() as db_session:
            if db_session.query(User).filter_by(user_name=user_name).first():
                flash('Такой логин уже занят!', 'danger')
                return render_template('register.html')

            if db_session.query(User).filter_by(email=email).first():
                flash('Почта уже занята!', 'danger')
                return render_template('register.html')

            new_user = User(
                first_name=first_name,
                last_name=last_name,
                user_name=user_name,
                email=email,
                password=generate_password_hash(password)  # Хеширование пароля
            )

            db_session.add(new_user)
            db_session.commit()

            flash('Registration success! Please login.', 'success')
            return redirect(url_for('login'))  # Предполагается, что есть маршрут 'login'

    return render_template('register.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user_name = request.form['user_name']
        password = request.form['password']
        
        with get_db_session() as db_session:
            user_db = db_session.query(User).filter_by(user_name=user_name).first()
            if not user_db:
                flash('Пользователь не найден!', 'danger')
                return render_template('login.html')
            else:
                if check_password_hash(user_db.password, password):
                    session['login'] = True
                    session['first_name'] = user_db.first_name
                    session['last_name'] = user_db.last_name
                    session['user_name'] = user_db.user_name
                    flash(f"Вы успешно авторизовались. Добро пожаловать, {session['first_name']} {session['last_name']}!", "success")
                else:
                    flash("Пароли не совпадают!", "danger")
                    return render_template('login.html')
        return redirect('/')
    return render_template('login.html')


@app.route('/logout/')
def logout():
    session.clear()
    flash('Вы вышли из своего профиля!', 'info')
    return redirect('/')


@app.route('/my_profil/')
def my_profil():
    with get_db_session() as db_session:
        user_db = db_session.query(Iris).filter_by(user_name=session['user_name']).all()
        if len(user_db) > 0:
            return render_template('my_profil.html',
                                   irises=user_db, name=session['first_name'] + ' ' + session['last_name'])
        return render_template('my_profil.html',
                               irises=None, name=session['first_name'] + ' ' + session['last_name'])


@app.route('/prediction_iris/', methods=['GET', 'POST'])
def prediction_price():
    if request.method == "POST":
        sepal_length = float(request.form['sepal_length'])
        sepal_width = float(request.form['sepal_width'])
        petal_length = float(request.form['petal_length'])
        petal_width = float(request.form['petal_width'])
        model = load('iris_model.joblib')
        scaler = load('scaler.joblib')
        X = scaler.transform([[sepal_length, sepal_width, petal_length, petal_width]])
        prediction = model.predict(X)
        
        with get_db_session() as db_session:
            new_iris = Iris(
                sepal_length=sepal_length,
                sepal_width=sepal_width,
                petal_length=petal_length,
                petal_width=petal_width,
                prediction=str(prediction[0]),
                user_name=session['user_name']
            )
            db_session.add(new_iris)
            db_session.commit()
            
        return render_template('prediction_iris.html', prediction=prediction[0])
    return render_template('prediction_iris.html', prediction=None)


@app.route('/prediction_true/<int:id>')
def prediction_true(id):
    with get_db_session() as db_session:
        iris = db_session.query(Iris).filter_by(id=id).first()
        iris.real = iris.prediction
        db_session.commit()
        return redirect('/my_profil/')


@app.route('/prediction_false/<int:id>', methods=['GET', 'POST'])
def prediction_false(id):
    if request.method == "POST":
        with get_db_session() as db_session:
            iris = db_session.query(Iris).filter_by(id=id).first()
            iris.real = str(request.form['true_sort'])
            db_session.commit()
            return redirect('/my_profil/')
    return render_template('prediction_false.html')


if __name__ == '__main__':
    app.run(debug=True)