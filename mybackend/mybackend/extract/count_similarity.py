import pandas as pd
import string
from nltk.tokenize import word_tokenize
import re
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))


def count_similarity(df1, df2):


    def normalize_title(title):
        title = str(title).lower()
        title = title.translate(str.maketrans('', '', string.punctuation))
        words = word_tokenize(title)
        words = [word for word in words if word not in stop_words]
        normalized_title = ' , '.join(words)
        return normalized_title

    def are_titles_similar(title1, title2, similarity_threshold=1):
        words1 = set(title1.split(' , '))
        words2 = set(title2.split(' , '))
        intersection = words1.intersection(words2)
        similarity = len(intersection) / max(len(words1), len(words2))
        return similarity >= similarity_threshold

        
    df1['normalized_title'] = df1['title'].apply(normalize_title)
    df2['normalized_title'] = df2['title'].apply(normalize_title)
    

    # Find the matching titles between df1 and df2
    matching_titles = []
    for title1 in df1['normalized_title']:
        for title2 in df2['normalized_title']:
            if are_titles_similar(title1, title2):
                matching_titles.append(title1)

    # Count the number of matching titles
    num_matching_titles = len(set(matching_titles))

    print("Number of titles that appear in both df1 and df2:", num_matching_titles)
    #---------------------------------------------------------------------------------------------

    df1_counts = df1.groupby('auth_id').size().reset_index(name='df1_count')
    df2_counts = df2.groupby('auth_id').size().reset_index(name='df2_count')

    df1_none_counts = df1[df1['abstract'].isnull()].groupby('auth_id').size().reset_index(name='df1_none_count')
    df2_none_counts = df2[df2['abstract'].isnull()].groupby('auth_id').size().reset_index(name='df2_none_count')

    merged_counts = pd.merge(df1_counts, df2_counts, on='auth_id', how='outer').fillna(0)
    merged_counts = pd.merge(merged_counts, df1_none_counts, on='auth_id', how='outer').fillna(0)
    merged_counts = pd.merge(merged_counts, df2_none_counts, on='auth_id', how='outer').fillna(0)

    merged_counts['ratio_df1_to_df2'] = merged_counts['df1_count'] / merged_counts['df2_count']

    print(merged_counts.head(50))