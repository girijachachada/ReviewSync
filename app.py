from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

app = Flask(__name__)
app.config["MONGO_URI_MOVIES"] = "mongodb+srv://review123:review123@cluster0.73f4jpp.mongodb.net/movie_reviews"
app.config["MONGO_URI_PHONES"] = "mongodb+srv://review123:review123@cluster0.73f4jpp.mongodb.net/phone_reviews"
app.secret_key = "supersecretkey"

mongo_movies = PyMongo(app, uri=app.config["MONGO_URI_MOVIES"])
mongo_phones = PyMongo(app, uri=app.config["MONGO_URI_PHONES"])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    # Retrieve user's first name from session
    first_name = session.get('first_name', 'Guest')
    movies = mongo_movies.db.movies.find()
    phones = mongo_phones.db.phones2.find()
    return render_template('home.html', first_name=first_name, movies=movies,phones=phones)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = mongo_movies.db.users.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            flash('Login successful!', 'success')
            session['first_name'] = user['first_name']  # Store first name in session
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        if mongo_movies.db.users.find_one({'email': email}):
            flash('Email already exists!', 'danger')
        else:
            mongo_movies.db.users.insert_one({'first_name': first_name, 'last_name': last_name, 'email': email, 'password': hashed_password})
            flash('Signup successful!', 'success')
            session['first_name'] = first_name
            return redirect(url_for('home'))

    return render_template('signup.html')

@app.route('/reviews/<movie_id>')
def show_reviews(movie_id):
    # Retrieve reviews for the selected movie from MongoDB
    reviews = []
    object_id = ObjectId(movie_id)
    
    # Query MongoDB collection for movie with specified _id
    movie = mongo_movies.db.movies.find_one({"_id": object_id})
    if movie:
        movie_name = movie.get('movie_name')
        # Also fetch reviews from another MongoDB collection based on movie name
        other_reviews = []
        other_movie = mongo_movies.db.letterboxd_movies.find_one({"title": movie_name})
        if other_movie:
            other_reviews = other_movie.get('popular_reviews', [])
        reviews = movie.get('reviews', [])
    
    return render_template('reviews.html', reviews=reviews, other_reviews=other_reviews)

@app.route('/phone_reviews/<phone_id>')
def show_reviews_phone(phone_id):
    # Retrieve reviews for the selected phone from MongoDB
    reviews = ""
    object_id = ObjectId(phone_id)
    
    # Query MongoDB collection for phone with specified _id
    phone = mongo_phones.db.phones2.find_one({"_id": object_id})
    if phone:
        phone_name = phone.get('phone_name') + " "  # Add one extra space
        other_reviews = ""
        other_phone = mongo_phones.db.phones.find_one({"phone_name": phone_name})
        if other_phone:
            other_reviews = other_phone.get('review', "")
        reviews = phone.get('review', "")
    
    # If other_reviews is empty, set it to "Review not available"
    if not other_reviews:
        other_reviews = "Review not available"
    
    return render_template('phone_reviews.html', reviews=reviews, other_reviews=other_reviews)



@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
