from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os

api_key = "c6e8fdab8f6057a5f89a0972858aad0d"
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///movies.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False, unique=False)
    description = db.Column(db.String(500), nullable=False, unique=False)
    rating = db.Column(db.Integer, nullable=True, unique=False)
    ranking = db.Column(db.Integer, nullable=True, unique=True)
    review = db.Column(db.String(120), nullable=True, unique=False)
    img_url = db.Column(db.String(), nullable=False, unique=False)


class MyForm(FlaskForm):
    rating = StringField(label="Rating", validators=[DataRequired()])
    review = StringField(label="Review", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


class Search(FlaskForm):
    name = StringField(label="Movie Name", validators=[DataRequired()])
    submit = SubmitField(label="Search")
db.create_all()

@app.route("/")
def home():
    try:
        all_movies = Movie.query.order_by(Movie.rating).all()
        for i in range(len(all_movies)):
            all_movies[i].ranking = len(all_movies) - i
        db.session.commit()
        return render_template("index.html", movies=all_movies)
    except:
        return render_template('index2.html')


@app.route("/edit<id>", methods=['POST', 'GET'])
def edit(id):
    form = MyForm()
    movie_to_update = Movie.query.get(id)
    if form.validate_on_submit():
        movie_to_update.rating = form.rating.data
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form, movie=movie_to_update)


@app.route("/delete<id>", methods=['POST', 'GET'])
def delete(id):
    movie_to_delete = Movie.query.get(id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/search", methods=['POST', 'GET'])
def search():
    form = Search()
    if form.validate_on_submit():
        response = requests.get(
            f"https://api.themoviedb.org/3/search/movie?api_key=c6e8fdab8f6057a5f89a0972858aad0d&query={form.name.data}&include_adult=false")
        data = response.json()["results"]
        return render_template("select.html", movies=data)

    return render_template("add.html", form=form)


@app.route("/add<movie_id>", methods=['POST', 'GET'])
def add(movie_id):
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}")
    data = response.json()
    new_movie = Movie(
        title=data["original_title"],
        year=data["release_date"].split('-')[0],
        description=data["overview"],
        img_url=f"https://image.tmdb.org/t/p/w500{data['poster_path']}",

    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
