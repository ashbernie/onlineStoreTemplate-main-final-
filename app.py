#!/usr/bin/env python3

from authentication.authTools import login_pipeline, update_passwords, hash_password
from database.db import Database
from flask import Flask, render_template, request, redirect, url_for
from core.session import Sessions

app = Flask(__name__)
HOST, PORT = 'localhost', 8080
global username, products, db, sessions
username = 'default'
db = Database('database/storeRecords.db')
products = db.get_full_inventory()
sessions = Sessions()
sessions.add_new_session(username, db)


@app.route('/')
def index_page():
    """
    Renders the index page when the user is at the `/` endpoint, passing along default flask variables.

    args:
        - None

    returns:
        - None
    """
    #return render_template('index.html', username=username, products=products, sessions=sessions)
    return redirect(url_for('home'))


@app.route('/login')
def login_page():
    """
    Renders the login page when the user is at the `/login` endpoint.

    args:
        - None

    returns:
        - None
    """
    return render_template('login.html')


@app.route('/home', methods=['POST', 'GET'])
def home():
    """
    Renders the home page when the user is at the `/home` endpoint with a POST request.

    args:
        - None

    returns:
        - None

    modifies:
        - sessions: adds a new session to the sessions object

    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if login_pipeline(username, password):
            sessions.add_new_session(username, db)
            return render_template('home.html', products=products, sessions=sessions)
        else:
            print(f"Incorrect username ({username}) or password ({password}).")
            return render_template('index.html')
    else:
        return render_template('home.html', products=products)



@app.route('/register')
def register_page():
    """
    Renders the register page when the user is at the `/register` endpoint.

    args:
        - None

    returns:
        - None
    """
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register():
    """
    Renders the index page when the user is at the `/register` endpoint with a POST request.

    args:
        - None

    returns:
        - None

    modifies:
        - passwords.txt: adds a new username and password combination to the file
        - database/storeRecords.db: adds a new user to the database
    """
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    salt, key = hash_password(password)
    update_passwords(username, key, salt)
    db.insert_user(username, key, email, first_name, last_name)
    return render_template('index.html')


@app.route('/checkout', methods=['POST'])
def checkout():
    """
    Renders the checkout page when the user is at the `/checkout` endpoint with a POST request.

    args:
        - None

    returns:
        - None

    modifies:
        - sessions: adds items to the user's cart
    """
    order = {}
    user_session = sessions.get_session(username)
    for item in products:
        print(f"item ID: {item['id']}")
        if request.form[str(item['id'])] > '0':
            count = request.form[str(item['id'])]
            order[item['item_name']] = count
            user_session.add_new_item(
                item['id'], item['item_name'], item['price'], count)

    user_session.submit_cart()

    return render_template('checkout.html', order=order, sessions=sessions, total_cost=user_session.total_cost)


@app.route('/about', methods=['POST', 'GET'])
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    message_form = request.form['message']
    db.insert_new_contact_submission(first_name, last_name, email, message_form)

    return render_template('submit_contact.html')

@app.route('/shop', methods=['POST', 'GET'])
def shop():
    return render_template('shop.html')

@app.route('/privacy_policy', methods=['POST', 'GET'])
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/terms_conditions', methods=['POST', 'GET'])
def terms_conditions():
    return render_template('terms_conditions.html')

@app.route('/shipping_returns', methods=['POST', 'GET'])
def shipping_returns():
    return render_template('shipping_returns.html')


if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=PORT)
