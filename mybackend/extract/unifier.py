import pandas as pd
import string
from nltk.tokenize import word_tokenize
import re
import csv
from nltk.corpus import stopwords
from .count_similarity import count_similarity
from tabulate import tabulate



def unify_publications(df1, df2, df3):
    
    stop_words = set(stopwords.words('english'))
    print("start unification")


    df1['source'] = "gs"
    df2['source'] = "rg"
    df3['source'] = "dblp"
    
    if df1.empty:
        if not df2.empty:
            df1 = df2.copy()
        else: 
            df1 = df3.copy()
    if df2.empty:
        if not df1.empty:
            df2 = df1.copy()
        else: 
            df2 = df3.copy()
    
    print("step1 ended")


    def normalize_title(title):
        if pd.isna(title): return ""
        title = str(title).lower()
        title = title.replace("'", "")
        title = title.translate(str.maketrans('', '', string.punctuation))
        words = word_tokenize(title)
        words = [word for word in words if word not in stop_words]
        normalized_title = ' '.join(words)
        return normalized_title
    if not (df1.shape[0]==0 or df1.empty):
        df1['normalized_title'] = df1['title'].apply(normalize_title)
        df1['normalized_abstract'] = df1['abstract'].apply(normalize_title)
        df1 = df1.drop_duplicates(subset=['auth_id', 'normalized_title'])
    
    if not (df2.shape[0]==0 or df2.empty):    
        df2['normalized_title'] = df2['title'].apply(normalize_title)
        df2['normalized_abstract'] = df2['abstract'].apply(normalize_title)
        df2 = df2.drop_duplicates(subset=['auth_id', 'normalized_title'])
    
    if not (df3.shape[0]==0 or df3.empty):        
        df3['normalized_abstract'] = df3['abstract'].apply(normalize_title)
        df3['normalized_title'] = df3['title'].apply(normalize_title)
        df3 = df3.drop_duplicates(subset=['auth_id', 'normalized_title'])
    print("step2 ended")
    
    
    df2Secours = df2.copy()
    cpt = 0
    rg_to_drop = []
    abs_list = []
    df_final =pd.DataFrame()
    for index, row in df1.iterrows():
        desired_row = df2[(df2['normalized_title'] == row['normalized_title']) & (df2['auth_id'] == row['auth_id'])]
        if len(desired_row)>0:

            df2_row = desired_row.iloc[0].copy()
            index_of_desired_row = desired_row.index[0]

            rg_to_drop.append(index_of_desired_row)
            if row['normalized_abstract'] == df2_row['normalized_abstract']:
                final_abstract = row['normalized_abstract']
                source = "gs"
            else: 
                if df2_row['normalized_abstract'] == "":
                    final_abstract = row['normalized_abstract']
                    source = "gs"
                elif row['normalized_abstract'] == "":
                    cpt+=1
                    final_abstract = df2_row['normalized_abstract']
                    source = "rg"
                else: 
                    if len(row['normalized_abstract'])>=len(df2_row['normalized_abstract']):
                        final_abstract = row['normalized_abstract']
                        source = "gs"
                    else: 
                        final_abstract = df2_row['normalized_abstract']
                        source = "rg"
            
            if len(str(row['date'])) == 0: 
                date = df2_row['date']
            else:
                date = row['date']
            
            if len(str(row['journal/book']))<len(str(df2_row['journal/book'])):
                journal = df2_row['journal/book']
            else:
                journal = row['journal/book']
            
            if len(str(row['authors']))<len(str(df2_row['journal/book'])):
                authors = df2_row['authors']
            else:
                authors = row['authors']
            
            if len(str(row['doi']))==0:
                doi = df2_row['doi']
            else:
                doi = row['doi']
            
            

                        
        else:
            final_abstract = row['normalized_abstract']
            source = "gs"
            date = row['date']
            authors = row['authors']
            journal = row['journal/book']
            doi = row['doi']

            if row['normalized_abstract'] == "":
                cpt+=1
        
        if source == "gs":
            f_title = row['title']
            f_abstract = row['abstract']
        elif source == "rg":
            f_title = df2_row['title']
            f_abstract = df2_row['abstract']
        
        abs_list.append((index, source, row["auth_id"], f_title, f_abstract, authors, date, journal, doi, row['normalized_title'] , final_abstract ))

    print("step3 ended")
    
    print(len(abs_list))
    count_empty_strings = sum(1 for item in abs_list if item[1] == "")

    #count_empty_strings = abs_list[1].count("")
    print(count_empty_strings)

    #DELETE RESEARCHGATE
    df2.drop(rg_to_drop, inplace=True)
    print("len of indexes : ", len(df2), " it was : ", len(df2Secours))

    print("number of indexes to delete in rg : ", len(rg_to_drop))
    print("nb nan abstract in gs: ", cpt)
    print("length of df2: ", len(df2), ", it was : ", len(df2Secours))
    filename = 'final_data.csv'
    header = ['index', 'source', 'auth_id', 'title', 'abstract', 'authors', 'date', 'journal', 'doi', 'norm_title', 'norm_abstract']
    '''
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile,  delimiter=';')
        writer.writerow(header)
        writer.writerows(abs_list)
    '''
    df_merged = pd.DataFrame(abs_list, columns=header)
    print(df_merged.head(5))

    # df3.to_csv('dblp_after.csv', encoding='utf-8-sig', sep=";")

    df2_after_gs = df2.copy()


    dblp_to_drop = []
    cpt = 0
    for index, row in df3.iterrows():
        desired_row = df_merged[ ( (df_merged['norm_title'] == row['normalized_title']) | (df_merged['doi'] == row['doi']) ) & (df_merged['auth_id'] == row['auth_id'])]
        if len(desired_row)>0:
            index_of_desired_row = index

            dblp_to_drop.append(index_of_desired_row)
            cpt+=1


    print("here is cpt: ", cpt)


    cpt=0
    for index, row in df2.iterrows():
        desired_row = df3[ ( (df3['normalized_title'] == row['normalized_title']) | (df3['doi'] == row['doi']) ) & (df3['auth_id'] == row['auth_id'])]
        if len(desired_row)>0:
            cpt+=1
            index_of_desired_row = desired_row.index[0]

            dblp_to_drop.append(index_of_desired_row)

    df3.drop(dblp_to_drop, inplace=True)


    print("length of dblp : ", len(df3))
    print("length of rg : ", len(df2))

    df2['source'] = "rg"
    df3['source'] = "dblp"

    result_df = df2.append(df3, ignore_index=True)

    result_df = result_df.reset_index()

    result_df.rename(columns={'journal/book': 'journal'}, inplace=True)
    result_df.rename(columns={'normalized_title': 'norm_title'}, inplace=True)
    result_df.rename(columns={'normalized_abstract': 'norm_abstract'}, inplace=True)

    desired_order = ['index', 'source', 'auth_id', 'title', 'abstract', 'authors', 'date', 'journal', 'doi', 'norm_title', 'norm_abstract']

    result_df = result_df[desired_order] 
    #result_df.to_csv('additional_data.csv', encoding='utf-8-sig', sep=";")
    last_df = df_merged.append(result_df,  ignore_index=True)

    import ast
    def safe_eval(authors_str):
        try:
            return ast.literal_eval(authors_str)
        except (ValueError, SyntaxError):
            return authors_str

    def find_order(authors_list, name):
        print(authors_list)
        print(name)
        if not isinstance(authors_list, list):
            return 'nothing'
        
        name_lower = str(name).lower()
        for i, author in enumerate(authors_list, 1):
            print(name_lower, author)
            if name_lower in str(author).lower():
                return f'({i}/{len(authors_list)})'
        return 'nothing'

    last_df['authors'] = last_df['authors'].apply(safe_eval)
    last_df['name'] = last_df['auth_id'].str.extract(r'_([^@]+)@')
    last_df['order'] = last_df.apply(lambda row: find_order(row['authors'], row['name']), axis=1)
    last_df.drop(columns=['name'], inplace=True)


    #last_df.to_csv('very_final_data.csv', encoding='utf-8-sig', sep=";")


    #df5 = pd.read_csv("fin_data.csv", encoding='utf-8-sig', sep=";")

    #print(df5.head(0))
    df5 = last_df
    grouped_df = df5.groupby('auth_id')

    # Step 3: Calculate the required statistics for each 'auth_id'
    result_data = []
    for auth_id, group in grouped_df:
        num_rows_with_auth_id = len(group)
        num_rows_with_empty_abstract = len(group[pd.isna(group['norm_abstract'])])
        mean_length_norm_abstract = group['norm_abstract'].apply(lambda x: len(str(x))).mean()
        num_rows_source_rg = len(group[group['source'] == "rg"])
        num_rows_source_gs = len(group[group['source'] == "gs"])
        num_rows_source_dblp = len(group[group['source'] == "dblp"])

        result_data.append([auth_id, num_rows_with_auth_id, num_rows_with_empty_abstract, int(mean_length_norm_abstract),
                            num_rows_source_rg, num_rows_source_gs, num_rows_source_dblp])

    # Step 4: Create a new DataFrame with the result data
    result_df = pd.DataFrame(result_data, columns=['auth_id', 'num_rows_with_auth_id', 'num_rows_with_empty_abstract',
                                                   'mean_length_norm_abstract', 'num_rows_source_rg',
                                                   'num_rows_source_gs', 'num_rows_source_dblp'])
    print(last_df.columns.tolist())
    return last_df 

    #result_df.to_csv("final_results.csv", index=False)
    # Convert the DataFrame to tabulated format
    tabulated_result = tabulate(result_df, headers='keys', tablefmt='grid')

    # Save the tabulated result to a text file
    with open("result.txt", "w") as file:
        file.write(tabulated_result)