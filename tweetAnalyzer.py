"""Functions to aid with sentiment analysis.

View documentation at http://textblob.readthedocs.io/en/dev/install.html
"""

from textblob import TextBlob


class TweetAnalyzer:
    """Class to analyse sentiment of text."""

    def __init__(self, raw_tweet):
        """Initialise new analysis."""
        self.raw_tweet = raw_tweet
        self.blob = TextBlob(raw_tweet["text"])

    def analyzeSentiment(self):
        """Return sentiment score as float with range of [-1.0, 1.0]."""
        return self.blob.sentiment.polarity

    def analyzeSubjectivity(self):
        """
        Return subjectivity score within range of [0.0, 1.0].

        0.0 is very objective and 1.0 is very subjective.
        """
        return self.blob.sentiment.subjectivity
