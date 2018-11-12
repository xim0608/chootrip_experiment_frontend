from flask import Flask, render_template, request, session, redirect, url_for
import os

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
    return "hello! username: {}".format(session['username'])


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
