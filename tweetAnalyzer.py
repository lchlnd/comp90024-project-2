from textblob import TextBlob
#http://textblob.readthedocs.io/en/dev/install.html

class tweetAnalyzer:
    def __init__(self, raw_tweet):
        self.raw_tweet = raw_tweet
        self.blob = TextBlob(raw_tweet["text"])
    #The polarity score is a float within the range [-1.0, 1.0]
    def analyzeSentiment(self):
        return self.blob.sentiment.polarity

    #The subjectivity is a float within the range [0.0, 1.0] where 0.0 is very objective and 1.0 is very subjective.
    def analyzeSubjectivity(self):
        return self.blob.sentiment.subjectivity
