from flask import request, jsonify, Flask
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

# download required nltk assets
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

app = Flask(__name__)

cache = {}


@app.route('/prediction', methods=["POST"])
def prediction_endpoint():
    print(request.json)
    if len(request.json) == 0:
        return {'error': "Empty request body"}

    return jsonify(get_predictions(request.json))


def get_predictions(tweets):
    results = {}
    openai_queue = []
    for index, tweet in enumerate(tweets):
        tweet["is_negative"] = None

        # check if prediction is already computed in cache
        if tweet["id"] in cache:
            results[tweet["id"]] = cache.get(tweet["id"])
            continue
        is_negative = nltk_is_negative(tweet["text"])

        # sentiment can't be determined using nltk
        # add it to openai gpt3 queue
        if is_negative is None:
            openai_queue.append(tweet)
        else:
            # sentiment was successfully determined using nltk
            tweet["is_negative"] = is_negative
            cache[tweet["id"]] = tweet
        results[tweet["id"]] = tweet

    openai_results = openai_is_negative(openai_queue)

    for key in openai_results.keys():
        if results[key]["is_negative"] is None:
            results[key] = openai_results[key]

    # join the two dictionaries
    z = openai_results.copy()
    z.update(results)
    return results


def nltk_is_negative(text):
    # compound property = aggregated score
    result = sid.polarity_scores(text)
    print(result)

    # can't determine in case of neutral prediction
    if result["neu"] >= result["pos"] and result["neu"] >= result["neg"]:
        return None

    return result["pos"] <= result["neg"]


def openai_is_negative(tweets):
    if len(tweets) == 0:
        return {}

    tweet_list = '\n'.join(list(map(lambda x: f"{x[0] + 1}. {x[1]['text']}", enumerate(tweets))))
    prompt = f"""Classify the sentiment in these tweets:

{tweet_list}

Tweet sentiment ratings:"""

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

    sentiments = result.choices[0].text.strip().split("\n")
    results = dict()
    for index, result in enumerate(sentiments):
        tweets[index]["is_negative"] = get_gpt3_is_negative(result)
        results[tweets[index]["id"]] = tweets[index]
    return results


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
    app.run(port=os.getenv("PORT", 3000), debug=True)
