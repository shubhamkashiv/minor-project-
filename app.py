from flask import Flask, render_template, request
import pickle
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

# Load trained model
model = pickle.load(open('model.pkl', 'rb'))

def is_valid_url(url):
    return url.startswith("http://") or url.startswith("https://")


def extract_features(url):
    features = []

    try:
        response = requests.get(url, timeout=5)
        html = response.text
    except:
        html = ""

    soup = BeautifulSoup(html, 'html.parser') if html else None

    # -------- URL FEATURES --------
    features.append(len(url))
    features.append(url.count('.'))
    features.append(url.count('-'))
    features.append(url.count('@'))
    features.append(1 if "https" in url else 0)

    # -------- TEXT FEATURES --------
    features.append(len(html))
    features.append(html.count("form"))
    features.append(html.count("input"))
    features.append(html.count("script"))

    # -------- HTML FEATURES --------
    features.append(len(soup.find_all('a')) if soup else 0)
    features.append(len(soup.find_all('img')) if soup else 0)
    features.append(len(soup.find_all('iframe')) if soup else 0)

    # -------- FILL TO MATCH MODEL (IMPORTANT FIX) --------
    while len(features) < 50:
        features.append(0)

    return features[:50]


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    url = request.form.get('url')

    if not is_valid_url(url):
        return render_template('index.html', error="Enter valid URL (http/https required)")

    features = extract_features(url)
    prediction = model.predict([features])[0]

    # 🔥 DEFAULT RESULT
    if prediction == 1:
        result = "Phishing"
        color = "#d63031"
        bg = "phishing.jpeg"
    else:
        result = "Safe"
        color = "#00b894"
        bg = "safe.jpeg"

    # 🔥 STRONG RULE OVERRIDE (IMPORTANT)
    risky_words = ['login','secure','bank','verify','update','account','password','paypal']

    if any(word in url.lower() for word in risky_words):
        result = "Phishing (High Risk)"
        color = "#d63031"
        bg = "phishing.jpeg"

    # 🔥 SUSPICIOUS DOMAIN
    if any(tld in url for tld in ['.xyz','.tk','.ml','.ga']):
        result = "Phishing (Suspicious Domain)"
        color = "#d63031"
        bg = "phishing.jpeg"

    return render_template('result.html',
                           result=result,
                           color=color,
                           bg=bg,
                           url=url)

if __name__ == "__main__":
    app.run(debug=True)