from flask import request, Flask
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

# download required nltk assets
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

app = Flask(__name__)


@app.route('/prediction', methods=["POST"])
def get_prediction():
    tweet_text = request.json["text"]
    result = nltk_is_negative(tweet_text)

    # can't detect reliable prediction result
    # try evaluating with openai gpt3 model
    if result is None:
        result = openai_is_negative(tweet_text)

    return {
        'is_negative': result
    }


def nltk_is_negative(text):
    # compound property = aggregated score
    result = sid.polarity_scores(text)
    print(result)

    # can't determine in case of neutral prediction
    if result["neu"] >= result["pos"] and result["neu"] >= result["neg"]:
        return None

    return result["pos"] <= result["neg"]


def openai_is_negative(text):
    result = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Decide whether a Tweet's sentiment is positive, neutral, or negative.\n\nTweet: \"{text}\"\nSentiment:",
        temperature=0,
        max_tokens=60,
        top_p=1,
        frequency_penalty=0.5,
        presence_penalty=0
    )
    print(result)
    # can't determine if no choices were returned
    if len(result.choices) == 0:
        return None

    prediction = result.choices[0].text.strip()
    if prediction == "Negative":
        return True
    elif prediction == "Positive":
        return False
    else:
        # can't determine if predictor equals "Neutral" or some other possible value
        return None


if __name__ == "__main__":
    app.run(debug=True)
