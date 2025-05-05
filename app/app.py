import os
import time
import redis
import pandas as pd
from flask import Flask, render_template
from dotenv import load_dotenv

# .env-Variablen laden
load_dotenv()

# Redis-Verbindung
cache = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=6379,
    password=os.getenv('REDIS_PASSWORD')
)

# Flask App
app = Flask(__name__)

# Seitenbesuche zählen
def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

# Home-Route
@app.route('/')
def hello():
    count = get_hit_count()
    return render_template('hello.html', name="BIPM", count=count)

# Titanic-Route
@app.route('/titanic')
def titanic():
    # Titanic-Dataset laden (Datei muss im app-Verzeichnis liegen)
    csv_path = os.path.join(os.path.dirname(__file__), "titanic.csv")
    df = pd.read_csv(csv_path)

    # Tabelle generieren (erste 5 Zeilen)
    table_html = df.head().to_html(classes="data", index=False)

    # Anzahl der Überlebenden nach Geschlecht
    survived_gender = df[df["Survived"] == 1]["Sex"].value_counts()

    return render_template(
        "titanic.html",
        table=table_html,
        survived=survived_gender.to_dict()
    )

# App starten
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
