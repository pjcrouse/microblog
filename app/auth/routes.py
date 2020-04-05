from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse

from app import db
from app.auth import bp
from app.auth.email import send_password_reset_email
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm, AddAllowedUserForm, BlockAllowedUserForm
from app.models import User, AllowedUsers, Post


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        if user.blocked:
            flash('Your user account has been suspended. Please contact an admin for support.')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        allowed = AllowedUsers.query.filter_by(email=form.email.data).first()
        if not allowed:
            return render_template('errors/not_authorized.html')
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/admin', methods=['GET', 'POST'])
def allow_access():
    if current_user.is_authenticated and not current_user.is_admin:
        flash('Only admins are allowed to access the admin page.')
        return redirect(url_for('main.index'))
    allow_form = AddAllowedUserForm()
    revoke_form = BlockAllowedUserForm()
    if allow_form.validate_on_submit() or revoke_form.validate_on_submit():
        allowed_user = AllowedUsers(email=allow_form.email_allow.data)
        if allowed_user.email != '':
            db.session.add(allowed_user)
            db.session.commit()
            flash('{} has been granted access to register'.format(allow_form.email_allow.data))
            return redirect(url_for('main.index'))
        else:
            blocked_user = BlockAllowedUserForm(email=revoke_form.email_block.data)
            if blocked_user:
                user = User.query.filter_by(email=blocked_user.email_block.data).first()
                if not user:
                    user = User.query.filter_by(username=blocked_user.email_block.data).first()
                if user:
                    user.blocked = True
                    db.session.commit()
                    flash('Access for {} has been revoked'.format(revoke_form.email_block.data))
                    return redirect(url_for('main.index'))
                flash('Could not find that user to block.')
    return render_template('auth/allow_access.html', title='Grant Access', allow_form=allow_form, revoke_form=revoke_form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_popup.html', user=user)


@bp.route('/delete_post/<post_id>')
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post has been deleted.')
    return redirect(url_for('main.index'))
