from flask import Flask, render_template, redirect, url_for, request, session, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, CreateAccountForm
from credentials import check_user, add_user
from flask_talisman import Talisman
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from bleach import clean
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
Talisman(app, force_https=True, force_https_permanent=True, strict_transport_security_preload=True)
app.secret_key = 'chavinhaaaAA11!!'

users = {}

limiter = Limiter(
    app=app,
    key_func=get_remote_address
)

app.config['GOOGLE_CLIENT_ID'] = '396993958909-k5lq5irfo9h563gouibbt1bde2masu4l.apps.googleusercontent.com'
app.config['GOOGLE_CLIENT_SECRET'] = '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'
app.config['OAUTH_CREDENTIALS'] = {
    'google': {
        'id': app.config['GOOGLE_CLIENT_ID'],
        'secret': app.config['GOOGLE_CLIENT_SECRET']
    }
}

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
)


@app.route('/')
@limiter.limit("5 per minute")
def index():
    return render_template('index.html')


@app.route('/login/google')
def login_google():
    redirect_uri = url_for('authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/authorize')
def authorize_google():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    session['username'] = user_info['email']
    flash('Login successful!', 'success')
    return redirect(url_for('logged_in'))


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if check_user(username, password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('logged_in'))
        else:
            flash('Wrong credentials provided. Please try again.', 'error')
    return render_template('login.html', form=form)


@app.route('/create_account', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def create_account():
    form = CreateAccountForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if add_user(username, password):
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists.', 'error')
    return render_template('create_account.html', form=form)


@app.route('/logged_in')
@limiter.limit("5 per minute")
def logged_in():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('logged_in.html', username=session['username'])


@app.route('/logout')
@limiter.limit("5 per minute")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.context_processor
def inject_current_year():
    return {'current_year': datetime.utcnow().year}


@app.errorhandler(429)
def ratelimit_handler(e):
    return "Try again in 5 minutes", 429


@app.route('/set_cookie')
def set_cookie():
    response = make_response('Setting a cookie.')
    response.set_cookie('example', 'value', secure=True, httponly=True)
    return response


if __name__ == '__main__':
    app.run(debug=True)