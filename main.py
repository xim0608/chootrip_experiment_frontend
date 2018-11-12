from flask import Flask, render_template, request, session, redirect, url_for
import os
from chootrip_api import ChootripApi

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/session', methods=['POST'])
def new_session():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('top'))
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def delete_session():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/')
def top():
    if 'username' not in session:
        return redirect(url_for('login'))
    prefectures = ChootripApi.get_prefectures()
    return render_template('top.html', prefectures=prefectures)


@app.route('/prefectures/<prefecture_id>')
def select_city(prefecture_id=None):
    cities = ChootripApi.get_cities(prefecture_id)
    chunked_cities = [cities[n:n + 3] for n in range(0, len(cities), 3)]
    return render_template('select_city.html', cities=chunked_cities)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
