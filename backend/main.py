from flask import request, Flask
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# download required nltk assets
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

app = Flask(__name__)


@app.route('/', methods=["POST"])
def example():
    return {
        'prediction': predict(request.json['text'])
    }


def predict(text):
    return sid.polarity_scores(text)


if __name__ == "__main__":
    app.run(debug=True)
