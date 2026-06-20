from flask import Flask, render_template, request
from database import db, SearchHistory
import requests

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weather.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

API_KEY = "75953d62d8e6e12d762d167595376aaa"


@app.route("/", methods=["GET", "POST"])
def home():

    weather = None
    history = SearchHistory.query.all()

    if request.method == "POST":

        city = request.form["city"]

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

        response = requests.get(url)
        print("Status Code:", response.status_code)
        print("Response:", response.text)

        if response.status_code == 200:

            data = response.json()

            weather = {
                "city": data["name"],
                "temp": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "wind": data["wind"]["speed"],
                "condition": data["weather"][0]["description"],
            }

            record = SearchHistory(city=data["name"], temperature=data["main"]["temp"])

            db.session.add(record)
            db.session.commit()

            history = SearchHistory.query.all()

    return render_template("index.html", weather=weather, history=history)


if __name__ == "__main__":
    app.run(debug=True)
