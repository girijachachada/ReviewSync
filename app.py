from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://review123:review123@cluster0.73f4jpp.mongodb.net/movie_reviews"
app.secret_key = "supersecretkey"

mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    # Retrieve user's first name from session
    first_name = session.get('first_name', 'Guest')
    movies = mongo.db.movies.find()
    return render_template('home.html', first_name=first_name, movies=movies)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = mongo.db.users.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            flash('Login successful!', 'success')
            session['first_name'] = user['first_name']  # Store first name in session
            print("First name stored in session:", session['first_name'])  # Debug statement
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

        if mongo.db.users.find_one({'email': email}):
            flash('Email already exists!', 'danger')
        else:
            mongo.db.users.insert_one({'first_name': first_name, 'last_name': last_name, 'email': email, 'password': hashed_password})
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
    movie = mongo.db.movies.find_one({"_id": object_id})
    if movie:
        movie_name = movie.get('movie_name')
        # Also fetch reviews from another MongoDB collection based on movie name
        other_reviews = []
        other_movie = mongo.db.letterboxd_movies.find_one({"title": movie_name})
        if other_movie:
            other_reviews = other_movie.get('popular_reviews', [])
        reviews = movie.get('reviews', [])
    
    return render_template('reviews.html', reviews=reviews, other_reviews=other_reviews)


@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
