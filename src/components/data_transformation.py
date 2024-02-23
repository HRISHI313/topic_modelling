import os
import sys
import pandas as pd
import string
import re
from src.logger import logging
import pickle
import inflect
from src.exception import CustomException
from nltk.corpus import stopwords
from collections import Counter
from nltk.stem.porter import PorterStemmer
from nltk import pos_tag
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from spellchecker import SpellChecker
from sklearn.feature_extraction.text import CountVectorizer
from src.utils import create_directory



# CONVERTING THE TEXT INTO LOWERCASE
def lower_case(train_data: str, test_data: str):
    try:
        logging.info(f"opening the {train_data} and {test_data}")
        df1 = pd.read_csv(train_data)
        df2 = pd.read_csv(test_data)

        logging.info(f"Converting the text into lower")
        df1['articles'] = df1['articles'].str.lower()
        df2['articles'] = df2['articles'].str.lower()

        return df1, df2

    except CustomException as e:
        logging.info(f"Error in lower_case: {e}")



# REMOVAL OF PUNCTUATION
def removal_punctuation(df1: pd.DataFrame, df2: pd.DataFrame):
    try:
        logging.info(f"Removing punctuation")
        df1['articles'] = df1['articles'].str.replace('[^\w\s]','')
        df2['articles'] = df2['articles'].str.replace('[^\w\s]','')

        logging.info("Punctuation has been removed")
        return df1, df2

    except CustomException as e:
        logging.info(f"Error in removal_punctuation: {e}")



# REMOVAL OF STOPWORDS
def removal_stopwords(df1: pd.DataFrame, df2: pd.DataFrame):
    try:
        logging.info(f"Removing the stopwords")
        stop_words = set(stopwords.words('english'))
        df1['articles'] = df1['articles'].apply(lambda x: " ".join(word for word in x.split() if word not in stop_words))
        df2['articles'] = df2['articles'].apply(lambda x: " ".join(word for word in x.split() if word not in stop_words))

        logging.info("Stopwords have been removed")
        return df1, df2

    except CustomException as e:
        logging.info(f"Error in removal_stopwords: {e}")



# REMOVAL OF FREQURNT WORDS
def removal_frequent_words(df1: pd.DataFrame, df2: pd.DataFrame):
    try:
        word_count1 = Counter()
        for text1 in df1['articles']:
            for word1 in text1.split():
                word_count1[word1] += 1

        word_count2 = Counter()
        for text2 in df2['articles']:
            for word2 in text2.split():
                word_count2[word2] += 1

        # Determine frequent words for both dataframes
        frequent_words_df1 = set(word for (word, wc) in word_count1.most_common(3))
        frequent_words_df2 = set(word for (word, wc) in word_count2.most_common(3))

        # Remove frequent words from articles
        df1['articles'] = df1['articles'].apply(lambda x: " ".join(word for word in x.split() if word not in frequent_words_df1))
        df2['articles'] = df2['articles'].apply(lambda x: " ".join(word for word in x.split() if word not in frequent_words_df2))

        logging.info("Frequent words have been removed")
        return df1, df2

    except CustomException as e:
        logging.error(f"Error in removal_frequent_words: {e}")


# REMOVAL OF SPECIAL CHARACTER
def removal_special_characters(df1: pd.DataFrame, df2: pd.DataFrame):
    try:
        logging.info(f"Removing the special characters")
        df1['articles'] = df1['articles'].apply(lambda x: " ".join(word for word in x.split() if word not in string.punctuation))
        df2['articles'] = df2['articles'].apply(lambda x: " ".join(word for word in x.split() if word not in string.punctuation))

        logging.info("Special characters have been removed")
        return df1, df2

    except CustomException as e:
        logging.info(f"Error in removal_special_characters: {e}")



# STEMMING
def stemming(df1: pd.DataFrame, df2: pd.DataFrame):
    try:
        logging.info(f"Stemming the words")
        ps = PorterStemmer()
        df1['articles'] = df1['articles'].apply(lambda x: " ".join([ps.stem(word) for word in x.split()]))
        df2['articles'] = df2['articles'].apply(lambda x: " ".join([ps.stem(word) for word in x.split()]))

        logging.info("Stemming has been applied")
        return df1, df2

    except CustomException as e:
        logging.info(f"Error in stemming: {e}")



# LEMMATIZATION
def lemmatization(df1: pd.DataFrame, df2: pd.DataFrame):
    try:
        lemmatizer = WordNetLemmatizer()
        df1['articles'] = df1['articles'].apply(lambda x: " ".join([lemmatizer.lemmatize(word) for word in x.split()]))
        df2['articles'] = df2['articles'].apply(lambda x: " ".join([lemmatizer.lemmatize(word) for word in x.split()]))

        logging.info("Lemmatization has been applied")
        return df1, df2

    except CustomException as e:
        logging.info(f"Error in lemmatization: {e}")




# REMOVAL OF URLs
def removal_urls(df1: pd.DataFrame, df2: pd.DataFrame):
    try:
        logging.info("Removing the URLs")
        df1['articles'] = df1['articles'].apply(lambda x: " ".join([word for word in x.split() if not ('http' in word or '://' in word or 'www' in word)]))
        df2['articles'] = df2['articles'].apply(lambda x: " ".join([word for word in x.split() if not ('http' in word or '://' in word or 'www' in word)]))

        logging.info("URLs have been removed")
        return df1, df2
    except CustomException as e:
        logging.error(f"Error in removal_urls: {e}")


# REMOVAL OF NUMBER TO WORDS
def replace_numbers_with_words(text):
    p = inflect.engine()
    words = text.split()
    for i, word in enumerate(words):
        if word.isdigit():
            words[i] = p.number_to_words(word)
    modified_text = ' '.join(words)
    return modified_text



# DATA TRANSFORMATION
def data_transformation():
    try:
        logging.info(f"Data transformation has been started")
        train_data, test_data = "artifacts/train_set.csv", "artifacts/test_set.csv"
        l_c = lower_case(train_data, test_data)
        r_p = removal_punctuation(l_c[0], l_c[1])
        r_s = removal_stopwords(r_p[0], r_p[1])
        r_f = removal_frequent_words(r_s[0], r_s[1])
        r_sc = removal_special_characters(r_f[0], r_f[1])
        r_st = stemming(r_sc[0], r_sc[1])
        r_l = lemmatization(r_st[0], r_st[1])
        r_u = removal_urls(r_l[0], r_l[1])
        r_nw[0]['articles'] = r_u[0].apply(replace_numbers_with_words)
        r_nw[1]['articles'] = r_u[1].apply(replace_numbers_with_words)

        r_nw[0].to_csv(train_data, index=False)
        r_nw[0].to_csv(test_data, index=False)

        logging.info("Data transformation has been completed")
        logging.info("Converting them into pickle files")
        # train_data = "artifacts/pickle_file/data_cleaning.pkl"
        # create_directory("artifacts/pickle_file")
        # r_u[0].to_pickle(train_data)
        logging.info(f"Pickle files have been created {train_data}")
        return r_u[0], r_u[1]


    except CustomException as e:
        logging.error(f"Error in data_transformation: {e}")



















