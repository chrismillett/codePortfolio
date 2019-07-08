# This next section of code reads the scraped csv data into a pandas cleanSentimentDF.
# This is so it is a bit more organised and can be read easily with values
# clearly separated

import pandas as pd
import pickle
import re
import nltk
from collections import Counter
import string
from string import punctuation
import csv
import matplotlib.pyplot as plt
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

#read data from csv into program with the corresponding headings
columns = ['sentiment','id','date','query_string','user','text']
uncleanedData = pd.read_csv('sentimentData.csv',
                   error_bad_lines=False,
                   encoding="utf-8-sig",
                   header=None, names=columns)
#display head of data to see how it looks
print(uncleanedData.head())

'''
# drop columns of data that aren't needed
# the selected columns offer no benefits to sentiment analysis
uncleanedData = uncleanedData.drop(['id','date','query_string','user'],axis=1)
print(uncleanedData.head(10))


# check all tweets, group between positive and negative tags
# positive = 4, negative = 0
positives = uncleanedData['sentiment'][uncleanedData.sentiment == 4]
negatives = uncleanedData['sentiment'][uncleanedData.sentiment == 0]

print('Number of positive tweets:    {}'.format(len(positives)))
print('Number of negative tweets:    {}'.format(len(negatives)))
print('Total number of tweets:       {}'.format(uncleanedData.shape[0]))

# use above data to count unique tweets for each group
#print(uncleanedData.groupby('sentiment').describe())

# get a count of the words in each tweet
def wordCount(sentence):
    return len(sentence.split())

uncleanedData['word count'] = uncleanedData['text'].apply(wordCount)
print(uncleanedData.head(3))


# plot tweets on a graph
# x axis is amount of words in a tweet
# y axis is amount of tweets of that length
# green is positive
# red is negative

pos = uncleanedData['word count'][uncleanedData.sentiment == 4]
neg = uncleanedData['word count'][uncleanedData.sentiment == 0]
plt.figure(figsize=(12,6))
plt.xlim(0,45)
plt.xlabel('word count')
plt.ylabel('frequency')
g = plt.hist([pos, neg], color=['g','r'], alpha=0.5, label=['positive','negative'])
plt.legend(loc='upper right')

# print list of 10 most common words and how many times they appear
totalWords = []
for line in list(uncleanedData['text']):
    words = line.split()
    for word in words:
        totalWords.append(word.lower())
print(Counter(totalWords).most_common(10))

# plot number of occurences of first 30 words on a line graph
plt.figure(figsize=(10,5))
plt.title('Top 30 most common words')
plt.xticks(fontsize=10)
freqDist = nltk.FreqDist(totalWords)
freqDist.plot(23,cumulative=False)
plt.show()
'''

# create the labels for the column of scraped data
columnLabels=['dateTime','textBody','country','countryCode','coordinates',]
print('Reading CSV into cleanSentimentDF:')

# read csv into a pandas dataframe for analysis
cleanSentimentDF = pd.read_csv('sentimentData.csv', names=columnLabels, encoding='latin-1')

#sort cleanSentimentDF by newest first according to dateTime column
cleanSentimentDF['dateTime'] = pd.to_datetime(cleanSentimentDF['dateTime'])
cleanSentimentDF = cleanSentimentDF.sort_values(by='dateTime',ascending=False)
cleanSentimentDF = cleanSentimentDF.reset_index().drop('index',axis=1)

# check head of cleanSentimentDF to see how it looks
print(cleanSentimentDF.head())

print('Saving cleanSentimentDF to pickle:')
cleanSentimentDF.to_pickle('cleanSentimentDF.p') # save dframe to pickle

cleanSentimentDF = pd.read_pickle('cleanSentimentDF.p')  # load from pickle

# This section removes a lot of junk data from what has been collected.
# This makes it easier to analyse the sentiment, as a lot of the data is
# irrelevant and can affect the model.
def cleanTweetData(tweet):

    # remove HTML artefacts
    print('Removing HTML artefacts:')
    tweet = re.sub(r'\&\w*;', '', tweet)

    # convert @username to AT_USER - removing the @
    print('Removing @s:')
    tweet = re.sub('@[^\s]+','',tweet)

    # put all text in a tweet to lowercose
    print('Setting to lowercase:')
    tweet = tweet.lower()

    # remove URLs from tweets
    print('Removing URLs:')
    tweet = re.sub(r'https?:\/\/.*\/\w*', '', tweet)

    # remove hashtags - leave following text
    print('Removing #s:')
    tweet = re.sub(r'#\w*', '', tweet)

    # remove Punctuation and split 's, 't, 've with a space for filter
    print('Removing punctuation:')
    tweet = re.sub(r'[' + punctuation.replace('@', '') + ']+', ' ', tweet)

    # remove tickers
    print('Removing tickers:')
    tweet = re.sub(r'\$\w*', '', tweet)

    # Remove words with 2 or fewer letters - often don't really mean anything
    print('Removing words shorter than 3 letters:')
    tweet = re.sub(r'\b\w{1,2}\b', '', tweet)

    # remove any whitespace - including newlines
    print('Removing whitespace:')
    tweet = re.sub(r'\s\s+', ' ', tweet)

    # remove the final space at the end of each message
    print('Removing final space:')
    tweet = tweet.lstrip(' ')

    # remove characters that aren't part of basic unicode
    print('Removing non-unicode:')
    tweet = ''.join(c for c in tweet if c <= '\ufffd')
 
    cleanedTweet = 0
    cleanedTweet += 1
    print('Tweet: ',cleanedTweet,'please wait.')

    return tweet

# ______________________________________________________________

# cleans all the above data out of the text body of the tweet
print('Cleaning Dataset:')

cleanSentimentDF['textBody'] = cleanSentimentDF['textBody'].apply(cleanTweetData)
# preview some cleaned tweets
print(cleanSentimentDF['textBody'].head())



print('Preparing strings for tokenisation: ')
# this is a function to help tokenise the string by preparing it
def processText(raw_text):
    """
    Takes the tweets in as strings, then:
    removes all punctuation
    removes all stop words
    returns cleaned text
    """
    # check characters to determine if alphanumerical or punctuation
    print('Removing punctuation:')
    nopunc = [char for char in list(raw_text) if char not in string.punctuation]

    # rejoin characters into string
    print('Reforming string:')
    nopunc = ''.join(nopunc)

    # remove stopwords as defined by the nltk
    print('Removing stop words:')
    return [word for word in nopunc.lower().split() if word.lower() not in stopwords.words('english')]


# -------------------------------------------

# tokenize message column and create a column for tokens
cleanSentimentDF = cleanSentimentDF.copy()
cleanSentimentDF['tokens'] = cleanSentimentDF['textBody'].apply(processText)
cleanSentimentDF.head()



# This section of code extracts features from the tweets.
# This is how the model will determine the sentiment of the tweets.

# vectorise the tweets - represent them as a list of numbers that correspond to
# the word in that sentence
bowTransformer = CountVectorizer(analyzer=processText).fit(cleanSentimentDF['textBody'])
# print total number of vocab words
print('Total number of words in dataset vocabulary: ')
print(len(bowTransformer.vocabulary_))

# transform the entire cleanSentimentDF of messages
textBOW = bowTransformer.transform(cleanSentimentDF['textBody'])

# check out the bag-of-words counts for the entire corpus as a large sparse matrix
print('Shape of Sparse Matrix: ', textBOW.shape)
print('Amount of Non-Zero occurences: ', textBOW.nnz)


# to transform the entire bag-of-words corpus
tfidfTransformer = TfidfTransformer().fit(textBOW)
textTfidf = tfidfTransformer.transform(textBOW)
print('Shape of bag of words:', textTfidf.shape)



print('Writing data to CSV file ready for use:')
exportCSV = cleanSentimentDF.to_csv('cleanSentimentData.csv', encoding='utf-8')