'''
This is the final submission made on Kaggle.
'''

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from math import gcd
from fractions import Fraction
from scipy.sparse import hstack
import math

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

# import os
# for dirname, _, filenames in os.walk('/kaggle/input'):
#     for filename in filenames:
#         print(os.path.join(dirname, filename))

# You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session

##################
# Helper methods #
##################

def get_num_voters(fraction_sets):
    """
    Get LCM i.e. denominator/num_voters for each label.
    """
    denominators = []
    for f_set in fraction_sets:
        d = []
        for f in f_set:
            d.append(Fraction(f).limit_denominator().denominator)
        d_temp = lowest_common_multiple_of_list(d)
        denominators.append(d_temp)
    return denominators

def adjust_results(results_array, correcting_array):
    """
    Adjust results to be closer to real fractions (need to modify once the final
    output is sorted).
    Right now it just assumes one row of results is passed.
    """
    new_results = np.zeros_like(results_array)
    i = 0
    while i < np.size(results_array):
        temp_correcting_array = np.abs(correcting_array - results_array[i])
        min_index = np.argmin(temp_correcting_array)
        new_results[i] = correcting_array[min_index]
        i += 1
    return new_results

def get_final_sets(trainDF):
    """
    Get sets for each collumn of possible values.
    """
    data_y = trainDF.iloc[:, 11:]
    possible_y = []
    for k in range(len(data_y.columns)):
        temp_set = set()
        for i in range(len(data_y.index)):
            temp_set.add(data_y.iloc[i, k])
        possible_y.append(list(temp_set))
    return possible_y

def lowest_common_multiple_of_list(d):
    """
    Get LCM from list.
    """
    lcm = d[0]
    for i in range(1, len(d)):
        lcm = lcm * d[i] // gcd(lcm, d[i])
    return lcm

def farey(n, array_n, array_d):
    """
    Form farey sequence for our data to be tested against.
    """
    x1 = 0
    y1 = 1
    x2 = 1
    y2 = n
    # Add first two terms
    array_n.append(0)
    array_n.append(1)
    array_d.append(0)
    array_d.append(n)
    x = 0
    y = 0
    # Evaluate rest of the sequence
    while (y != 1):
        # Using recurrence relation to
        # find the next term
        x = math.floor((y1 + n) / y2) * x2 - x1
        y = math.floor((y1 + n) / y2) * y2 - y1
        array_n.append(x)
        array_d.append(y)
        # Update x1, y1, x2 and y2 for
        # next iteration
        x1 = x2
        x2 = x
        y1 = y2
        y2 = y
        
def farey_correcting_array(limit):
    """
    Function to return correcting array via farey sequences.
    This essentially allows us to explain why we chose a limit
    i.e. a specific farey sequence to minimise the error of our
    regressional output.
    """
    array_n = []
    array_d = []
    farey(limit, array_n, array_d)
    # Avoid zero division
    array_n.pop(0)
    array_d.pop(0)
    array_n = np.array(array_n)
    array_d = np.array(array_d)
    array_fractions = list(array_n / array_d)
    # Add back 0
    array_fractions.append(0)
    return array_fractions

def multiOutputR(X_train, X_test, y_train, final_predicted_values, allowed_sets, labels, num_voters, best_params, start_index):
    """
    # Method | Wrapper for regression on multiple labels
    # Input  | ML algorithm, X_train (2D np array), X_test (2D np array),
    #        | List of y_train ([1D np array]),
    #        | List of y labels ([string])
    # Output | Train model and make predictions on each label
    """
    
    # Loop through labels and train model for each
    i = 0
    while i < len(labels):
        # Train model and predict data
        rdg = Ridge(alpha = best_params[i])
        rdg.fit(X_train, y_train[i])
        pred = rdg.predict(X_test)
        
        # we only applied port processing for those features which were not causing spearman nan error
        # and which were giving a better score after applying the post processing
        if (start_index == 1 and i in (8, 12, 13, 14, 15)) or (start_index == 22 and i == 1):
            pred = adjust_results(pred, farey_correcting_array(num_voters[i]))
        final_predicted_values[:, start_index + i] = pred
        i += 1
    return final_predicted_values

if __name__ == "__main__":
    # Read the train.csv and test.csv files
    trainDf = pd.read_csv('/kaggle/input/google-quest-challenge/train.csv')
    testDf = pd.read_csv('/kaggle/input/google-quest-challenge/test.csv')

    # Extract feature dataframes
    question_title_train = trainDf['question_title']
    question_body_train = trainDf['question_body']
    answer_train = trainDf['answer']

    question_title_test = testDf['question_title']
    question_body_test = testDf['question_body']
    answer_test = testDf['answer']

    # Creating dictionary to extract features using TFIDF vectorizer method
    vectorizer_for_question_answer = TfidfVectorizer(ngram_range=(1, 2), use_idf= True, smooth_idf= True, sublinear_tf= True, lowercase=False)
    
    vectorizer_for_question_answer.fit(question_title_train)
    vectorizer_for_question_answer.fit(question_body_train)
    vectorizer_for_question_answer.fit(answer_train)

    # creating vectors for each feature using transform function of the vectorizer
    question_title_vector_train = vectorizer_for_question_answer.transform(question_title_train)
    question_body_vector_train = vectorizer_for_question_answer.transform(question_body_train)
    X_answer_train = vectorizer_for_question_answer.transform(answer_train)

    question_title_vector_test = vectorizer_for_question_answer.transform(question_title_test)
    question_body_vector_test = vectorizer_for_question_answer.transform(question_body_test)
    X_answer_test = vectorizer_for_question_answer.transform(answer_test)
    
    # combining two questions title and body vectors into one input vector
    X_question_train = hstack((question_title_vector_train, question_body_vector_train))
    X_question_test = hstack((question_title_vector_test, question_body_vector_test))
    
    y_train = []

    # Extract label dataframes
    for label in trainDf.columns[11:]:
        y_train.append(trainDf[label])

    question_labels = [label for label in trainDf.columns[11:] if "question_" in label]
    answer_labels = [label for label in trainDf.columns[11:] if 'answer_' in label]

    # to extract final sets which contains the discrete values allowed for each feature
    final_sets = get_final_sets(trainDf)
    question_final_values = final_sets[:21]
    answer_final_values = final_sets[21:]
    
    # created the np array to store final submission values and the stored the first column with row instances
    final_predicted_values = np.zeros((len(testDf), 31))    
    final_predicted_values[:, 0] = testDf['qa_id']
    all_labels = np.array(['qa_id'] + question_labels + answer_labels)
    
    # Give optimised hyper-paramaters
    best_params = [
        {'alpha': 8.0}, 
        {'alpha': 1.5}, 
        {'alpha': 3.0}, 
        {'alpha': 9.5}, 
        {'alpha': 4.0}, 
        {'alpha': 3.0}, 
        {'alpha': 7.5}, 
        {'alpha': 4.5}, 
        {'alpha': 2.0}, 
        {'alpha': 10.0}, 
        {'alpha': 3.5}, 
        {'alpha': 1.5}, 
        {'alpha': 2.0}, 
        {'alpha': 6.5}, 
        {'alpha': 2.0}, 
        {'alpha': 1.5}, 
        {'alpha': 1.5}, 
        {'alpha': 8.5}, 
        {'alpha': 2.0}, 
        {'alpha': 2.0}, 
        {'alpha': 3.0}, 
        {'alpha': 10.0}, 
        {'alpha': 10.0}, 
        {'alpha': 10.0}, 
        {'alpha': 10.0}, 
        {'alpha': 10.0}, 
        {'alpha': 2.5}, 
        {'alpha': 10.0}, 
        {'alpha': 3.5}, 
        {'alpha': 10.0}
    ]
    
    best_params = [best_params[k]['alpha'] for k in range(len(best_params))]
    num_voters = get_num_voters(get_final_sets(trainDf))
    
    # Run Multioutput regression on all all question and answer features
    final_predicted_values = multiOutputR(X_question_train, X_question_test, y_train[0:21], final_predicted_values, question_final_values, question_labels, num_voters[0:21], best_params[0:21], 1)
    final_predicted_values = multiOutputR(X_answer_train, X_answer_test, y_train[21:], final_predicted_values, answer_final_values, answer_labels, num_voters[21:], best_params[21:], 22)
    
    # Kaggle was giving error for values 0 and 1, so had to normalise the data to remove such values
    for row in range(final_predicted_values.shape[0]):
        for col in range(1, final_predicted_values.shape[1]):
            if final_predicted_values[row, col] <= 0:
                final_predicted_values[row, col] = 0.001
            elif final_predicted_values[row, col] >= 1:
                final_predicted_values[row, col] = 0.999
                
    # convert the numpy array to dataframe and store as per Kaggle required format
    df = pd.DataFrame(final_predicted_values,columns=all_labels, index=None)
    # getting the sample file format from kaggle and storing the submission file as per that
    # storing with any other way throws error during submission
    sample = pd.read_csv('/kaggle/input/google-quest-challenge/sample_submission.csv')
    format = "{:.5f}"
    for row in range(final_predicted_values.shape[0]):
        for col in range(1, final_predicted_values.shape[1]):
            sample.iloc[row, col] = float(format.format(final_predicted_values[row, col]))
    
    sample.to_csv('submission.csv', index=False)