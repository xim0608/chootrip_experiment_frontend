from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
import os
from chootrip_api import ChootripApi
from experiment_db import SpreadSheet

# from google.cloud import datastore

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')
prefectures = ChootripApi.get_prefectures()


@app.context_processor
def inject_pref():
    return dict(prefectures=prefectures)


@app.context_processor
def inject_cart_count():
    if 'cart' in session:
        return dict(count=len(session['cart']))
    else:
        return dict(count=0)


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/session', methods=['POST'])
def new_session():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['cart'] = []
        session['topic_answered'] = False
        return redirect(url_for('topic_survey'))
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def delete_session():
    session.pop('username', None)
    session.pop('cart', None)
    session.pop('confirm', None)
    session.pop('topic_answered', None)
    return redirect(url_for('login'))


@app.route('/topic_survey', methods=['GET', 'POST'])
def topic_survey():
    if session['username'] or not session['topic_answered']:
        topics = get_topics()
        topics_with_words = get_topics_with_words()
        if request.method == 'GET':
            return render_template('topic_survey.html', topics=topics_with_words)
        else:
            if len(topics_with_words) != len(request.form):
                flash('入力漏れがあったようです．', 'danger')
                return redirect(url_for('topic_survey'))
            user_answer = []
            for i in range(len(topics)):
                user_answer.append(int(request.form[str(i)]))
            s = SpreadSheet()
            s.update_topic_survey(session['username'], user_answer)
            flash('登録完了しました．下の説明の指示に従ってください．', 'info')
            session['topic_answered'] = True
            return redirect(url_for('top'))
    else:
        return redirect(url_for('login'))


@app.route('/')
def top():
    if 'username' not in session:
        return redirect(url_for('login'))
    if not session.get('topic_answered'):
        return redirect(url_for('topic_survey'))
    return render_template('top.html', prefectures=prefectures)


@app.route('/prefectures/<prefecture_id>')
def select_city(prefecture_id=None):
    cities = ChootripApi.get_cities(prefecture_id)
    cities = list(filter(lambda city: city['spot_count'] != 0, cities))
    chunked_cities = [cities[n:n + 3] for n in range(0, len(cities), 3)]
    return render_template('select_city.html', cities=chunked_cities)


@app.route('/cities/<city_id>')
def list_city(city_id=None):
    spots = ChootripApi.get_city_spots(city_id=int(city_id))
    city = ChootripApi.get_city(city_id)
    spots = set_cart_added(spots)
    spots = set_one_image(spots)

    return render_template('list_spots.html', segment_name=city['name'], spots=spots)


@app.route('/spots/search')
def search_result():
    q = request.args.get('q')
    q = q.strip()
    if q:
        spots = ChootripApi.get_spots_by_title_search(q)
    else:
        spots = []
    spots = set_cart_added(spots)
    spots = set_one_image(spots)
    return render_template('search_result.html', search_word=q, spots=spots)


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
    spots = list(map(lambda spot_id: ChootripApi.get_spot(spot_id), session['cart']))
    spots = set_cart_added(spots)
    spots = set_one_image(spots)
    return render_template('list_cart.html', spots=spots)


@app.route('/cart/confirm')
def confirm_cart():
    if len(session['cart']) != 10:
        flash('10件選択してください', 'danger')
        return redirect(url_for('list_cart'))
    session['confirm'] = True
    # spots = list(map(lambda spot_id: ChootripApi.get_spot(spot_id), session['cart']))
    spots = ChootripApi.get_spots(session['cart'])
    spots = set_cart_added(spots)
    spots = set_one_image(spots)
    return render_template('confirm_cart.html', spots=spots)


@app.route('/recommend')
def show_recommend():
    if len(session['cart']) != 10:
        flash('不正な入力です', 'danger')
        return redirect(url_for('top'))
    # TODO: もうすでにこの学籍番号のデータが登録されている場合は，ここで弾く
    session.pop('confirm', None)

    # GET: RECOMMEND_SPOTS
    # keys: ['similarities', 'user_vec']
    recommend_data = ChootripApi.get_recommend(session['cart'])
    recommend_spots = extract_10_recommend_spots(similarities_dict=recommend_data['similarities'])

    topics_with_words = get_topics_with_words()

    # GET: PREFERENCE
    s = SpreadSheet()
    normalized_user_vec = recommend_data['normalized_user_vec']
    s.update_normalized_topic_result(session['username'], normalized_user_vec)
    user_vec = recommend_data['user_vec']
    s.update_topic_result(session['username'], user_vec)

    selected_spots = ChootripApi.get_spots(session['cart'])
    selected_spots_name = []
    for selected_spot in selected_spots:
        selected_spots_name.append(selected_spot['title'])
    s.update_selected_spots(session['username'], selected_spots_name)

    recommend_spots_name = []
    for recommend_spot in recommend_spots:
        recommend_spots_name.append(recommend_spot['title'])
    s.update_recommend_result(session['username'], recommend_spots_name)

    return render_template(
        'recommends.html', recommend_spots=recommend_spots, topics=zip(topics_with_words, normalized_user_vec))


@app.route('/recommend_survey', methods=['POST'])
def recommend_survey():
    if request.method == 'POST':
        if len(request.form) == (10 * 2):
            user_answer_new = []
            user_answer_interest = []
            for num in range(0, 10):
                user_answer_new.append(int(request.form["n{}".format(str(num))]))
                user_answer_interest.append(int(request.form["i{}".format(str(num))]))
            s = SpreadSheet()
            s.update_recommend_survey_of_new(session['username'], user_answer_new)
            s.update_recommend_survey_of_interest(session['username'], user_answer_interest)
            flash('これで全ての質問が終了しました．ご協力ありがとうございました．')
            return redirect(url_for('login'))
        else:
            flash('全ての欄に回答してください', 'danger')
            return redirect(url_for('show_recommend'))


def extract_10_recommend_spots(similarities_dict):
    similarities_sorted = sorted(similarities_dict.items(), key=lambda x: -x[1])
    # chunk_size件ずつ条件にあったスポットを取り出す
    chunk_size = 50
    chunked_similarities = [similarities_sorted[n:n + chunk_size] for n in
                            range(0, len(similarities_sorted), chunk_size)]
    recommend_spots = []
    for similarities_by_chunk_size in chunked_similarities:
        spot_ids = []
        for spot_similarity_info in similarities_by_chunk_size:
            spot_id = spot_similarity_info[0]
            _similarity = spot_similarity_info[1]
            spot_ids.append(spot_id)
        spots = ChootripApi.get_spots(spot_ids)
        recommend_spots.extend(spots)

        # exclude selected spots
        recommend_spots = list(filter(lambda s: s['id'] not in session['cart'], recommend_spots))

        # extract by counts
        recommend_spots = list(filter(lambda s: s['count'] >= 153, recommend_spots))

        # set similarity
        for spot in recommend_spots:
            spot['similarity'] = similarities_dict[str(spot['id'])]

        # sort
        recommend_spots = list(sorted(recommend_spots, key=lambda s: -s['similarity']))

        if len(recommend_spots) > 10:
            break
    return recommend_spots[:10]


def set_cart_added(spots):
    for spot in spots:
        if spot['id'] in session['cart']:
            spot['added'] = True
    return spots


def set_one_image(spots):
    for spot in spots:
        if len(spot['spotimage_set']) > 0:
            spot['image_url'] = spot['spotimage_set'][0]["url"]
        else:
            spot['image_url'] = url_for('static', filename='no_image.png')
    return spots


@app.route('/reset_topic')
def reset_topic():
    if session['username'] == os.environ.get('ADMIN_USERNAME'):

        return redirect(url_for('top'))
    else:
        flash('Forbidden', 'danger')
        return redirect(url_for('top'))


def get_topics():
    topics = ChootripApi.get_topics()['topics']
    return topics


def get_topics_with_words():
    topics = get_topics()
    topics_with_words = []
    for i in range(len(topics)):
        topic_term_top_5 = []
        for topic_term in topics[str(i)][:5]:
            word = topic_term[0]
            _word_score = topic_term[1]
            topic_term_top_5.append(word)
        topics_with_words.append(','.join(topic_term_top_5))
    return topics_with_words


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
