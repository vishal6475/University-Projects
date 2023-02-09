import pandas as pd
import numpy as np
import sys
import csv
import re

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# load the data.csv file
training_data = np.array(pd.read_csv(sys.argv[1], sep='\t', header=None, quoting=csv.QUOTE_NONE).dropna())
testing_data = np.array(pd.read_csv(sys.argv[2], sep='\t', header=None, quoting=csv.QUOTE_NONE).dropna())

""" Removing URLs """
for i in range(training_data.shape[0]):
    URLs = re.findall(r'https?://\S+', training_data[i, 1])
    URLsWWW = re.findall(r'www.\S+', training_data[i, 1])
    for url in URLsWWW:
        URLs.append(url)
    
    for url in URLs:
        training_data[i, 1] = training_data[i, 1].replace(url, ' ')
    
for i in range(testing_data.shape[0]):
    URLs = re.findall(r'https?://\S+', testing_data[i, 1])
    URLsWWW = re.findall(r'www.\S+', testing_data[i, 1])
    for url in URLsWWW:
        URLs.append(url)
    
    for url in URLs:
        testing_data[i, 1] = testing_data[i, 1].replace(url, ' ')

allowed_characters = [' ', '#','@','_','$','%','0','1','2','3','4','5','6','7','8','9',
                      'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r',
                      's','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J',
                      'K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

""" Removing junk characters """
for i in range(training_data.shape[0]):
    for char in set(training_data[i, 1]):
        if char not in allowed_characters:
            training_data[i, 1] = training_data[i, 1].replace(char, '')
            
for i in range(testing_data.shape[0]):
    for char in set(testing_data[i, 1]):
        if char not in allowed_characters:
            testing_data[i, 1] = testing_data[i, 1].replace(char, '')


# split into train and test sets
X_train = training_data[:, 1]
Y_train = training_data[:, 2]

X_test = testing_data[:, 1]
# Y_test = testing_data[:, 2]

# pattern to extract word with minimum two letters
pattern = r'[a-zA-Z0-9@#$%_][a-zA-Z0-9@#$%_]+'

""" For whole vocabulary """
# create count vectorizer and fit it with training data
count = CountVectorizer(lowercase = False, analyzer= 'word', token_pattern= pattern)
X_train_BOW = count.fit_transform(X_train)
X_test_BOW = count.transform(X_test)

# applying model on the training data and predicting values for test data
MNB = MultinomialNB()
MNB.fit(X_train_BOW, Y_train)

Y_predicted = MNB.predict(X_test_BOW)

# printing the final output
length = len(Y_predicted)
for i in range(length):
    print(testing_data[i, 0], Y_predicted[i])
        