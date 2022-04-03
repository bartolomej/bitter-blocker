from flask import request, jsonify, Flask
from flask_cors import CORS
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os
import openai
import json

openai.api_key = os.getenv("GPT_ACCESS_TOKEN")

# download required nltk assets
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

cache = {}
try:
    with open("cache.json") as cache_file:
        cache = json.load(cache_file)
except:
    pass

print(cache)


def save_cache():
    global cache
    print(cache)
    with open("cache.json", "w") as cache_file:
        json.dump(cache, cache_file)


request_count = 0


@app.route('/ping')
def ping_endpoint():
    return "Pong"


@app.route('/cache')
def cache_endpoint():
    save_cache()
    return cache


@app.route('/stats')
def stats_endpoint():
    return {
        'request_count': request_count
    }


@app.route('/prediction', methods=["POST"])
def prediction_endpoint():
    global request_count
    print(request.json)
    if len(request.json) == 0:
        return {'error': "Empty request body"}

    request_count += 1
    return jsonify(get_predictions(request.json))


def get_predictions(tweets):
    global cache
    results = {}
    for index, tweet in enumerate(tweets):
        tweet["is_negative"] = None

        # check if prediction is already computed in cache
        if tweet["id"] in cache:
            results[tweet["id"]] = cache.get(tweet["id"])
            continue
        is_negative = nltk_is_negative(tweet["text"])

        # sentiment was successfully determined using nltk
        tweet["is_negative"] = is_negative
        cache[tweet["id"]] = tweet
        results[tweet["id"]] = tweet

        # sentiment can't be determined using nltk
        # add it to openai gpt3 queue
        if results[tweet["id"]]["is_negative"] is None:
            results[tweet["id"]]["is_negative"] = openai_is_negative(tweet)
            cache[tweet["id"]] = tweet

    return results


def nltk_is_negative(text):
    # compound property = aggregated score
    result = sid.polarity_scores(text)
    print(result)

    # can't determine in case of neutral prediction
    if result["neu"] >= result["pos"] and result["neu"] >= result["neg"]:
        return None

    return result["pos"] <= result["neg"]


def openai_is_negative(tweet):
    prompt = f"Decide whether a Tweet's sentiment is positive, neutral, or negative.\n\nTweet: \"{tweet['text']}\"\nSentiment:",

    result = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0,
        max_tokens=60,
        top_p=1,
        frequency_penalty=0.5,
        presence_penalty=0
    )
    # can't determine if no choices were returned
    if len(result.choices) == 0:
        return None

    print(result)

    prediction = result.choices[0].text.strip()
    if prediction == "Negative":
        return True
    elif prediction == "Positive":
        return False
    else:
        # can't determine if predictor equals "Neutral" or some other possible value
        return None


def get_gpt3_is_negative(value):
    value = re.sub(r'[0-9]+\.', '', value).strip()
    if value == "Negative":
        return True
    elif value == "Positive":
        return False
    else:
        # can't determine if predictor equals "Neutral" or some other possible value
        return None


if __name__ == "__main__":
    app.run(port=os.getenv("PORT", 8080), debug=True)
