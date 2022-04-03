import unittest

fixtures = [
    {
        "id": 1,
        "text": "this is very neutral tweet"
    },
    {
        "id": 2,
        "text": "bad"
    },
    {
        "id": 3,
        "text": "jerk"
    }
]

from main import get_predictions


class MyTestCase(unittest.TestCase):
    def test_something(self):
        result = get_predictions(fixtures)
        self.assertEqual(True, False)  # add assertion here


# def filter_tweets(tweets, cache={}):
#     result = [None for i in tweets]
#     todo = []
#     for index, tweet in enumerate(tweets):
#         if tweet["id"] in cache:
#             result[index] = cache.get(tweet["id"])
#         else:
#             result[index] = tweet["id"]
#             todo.append(tweet)
#     return todo, result


if __name__ == '__main__':
    unittest.main()
