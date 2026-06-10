from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models import User, Role

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('books.index'))

    if request.method == 'POST':
        login_val = request.form.get('login', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(login=login_val).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('books.index'))

        flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('books.index'))

    if request.method == 'POST':
        login_val = request.form.get('login', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        last_name = request.form.get('last_name', '').strip()
        first_name = request.form.get('first_name', '').strip()
        middle_name = request.form.get('middle_name', '').strip() or None

        if not all([login_val, password, last_name, first_name]):
            flash('Заполните все обязательные поля.', 'danger')
            return render_template('auth/register.html', form_data=request.form)

        if password != password2:
            flash('Пароли не совпадают.', 'danger')
            return render_template('auth/register.html', form_data=request.form)

        if len(password) < 6:
            flash('Пароль должен содержать не менее 6 символов.', 'danger')
            return render_template('auth/register.html', form_data=request.form)

        if User.query.filter_by(login=login_val).first():
            flash('Пользователь с таким логином уже существует.', 'danger')
            return render_template('auth/register.html', form_data=request.form)

        user_role = Role.query.filter_by(name='Пользователь').first()
        user = User(
            login=login_val,
            password_hash=generate_password_hash(password),
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            role_id=user_role.id
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f'Добро пожаловать, {user.first_name}! Регистрация прошла успешно.', 'success')
        return redirect(url_for('books.index'))

    return render_template('auth/register.html', form_data={})


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(request.referrer or url_for('books.index'))
