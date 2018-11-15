from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import os
from chootrip_api import ChootripApi
# from google.cloud import datastore

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')
prefectures = ChootripApi.get_prefectures()


@app.context_processor
def inject_pref():
    return dict(prefectures=prefectures)


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
    session.pop('cart', None)
    return redirect(url_for('login'))


@app.route('/')
def top():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('top.html', prefectures=prefectures)


@app.route('/prefectures/<prefecture_id>')
def select_city(prefecture_id=None):
    cities = ChootripApi.get_cities(prefecture_id)
    cities = list(filter(lambda city: city['spot_count'] != 0, cities))
    chunked_cities = [cities[n:n + 3] for n in range(0, len(cities), 3)]
    return render_template('select_city.html', cities=chunked_cities)


@app.route('/cities/<city_id>')
def list_city(city_id=None):
    spots = ChootripApi.get_city_spots(city_id=int(city_id))['results']
    for spot in spots:
        if spot['id'] in session['cart']:
            spot['added'] = True
    return render_template('list_city.html', spots=spots)


@app.route('/api/cart/add/<spot_id>')
def add_cart(spot_id=None):
    session.modified = True

    if spot_id is None:
        return jsonify(status='error')
    if 'username' not in session:
        return redirect(url_for('login'))
    if 'cart' not in session:
        session['cart'] = []
    spot_id = int(spot_id)
    if spot_id in session['cart']:
        session['cart'].remove(spot_id)
        return jsonify(status='removed')
    else:
        session['cart'].append(spot_id)
        return jsonify(status='added')


@app.route('/api/cart/count')
def cart_count():
    if 'username' not in session:
        return jsonify(login=False)
    if 'cart' not in session:
        session['cart'] = []
    return jsonify(count=len(session['cart']))


@app.route('/api/cart/')
def list_cart_api():
    # return only spot id
    return jsonify(spots=session['cart'])


@app.route('/cart')
def list_cart():
    spots = map(lambda spot_id: ChootripApi.get_spot(spot_id), session['cart'])
    return render_template('list_cart.html', spots=spots)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
