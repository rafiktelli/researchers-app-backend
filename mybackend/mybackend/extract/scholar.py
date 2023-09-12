from pprint import pprint
from scholarly import scholarly, ProxyGenerator
import csv
from langdetect import detect
import re
import pandas as pd


def get_pubs_scholar(auth_id, url):
    #VERIFY URL COMPTABILITY
    if url is None or url == "" or pd.isna(url):
        print("no data for: ", auth_id)
        return []
    #EXTRACT USER ID 
    pattern = r'user=([^&]+)'
    match = re.search(pattern, url)
    if match:
        user_id = match.group(1)
    else: 
        return []
    print("user ID: ", user_id)
    author = scholarly.search_author_id(user_id)
    scholar = scholarly.fill(author, 
                            sections=['basics', 'publications'],
                            sortby="year",
                            publication_limit=106
                            )

    scholar_publications = []

    print(scholar['interests'])
    return []

    for pub in scholar['publications']:
        pub_filled = scholarly.fill(pub)
        title = pub_filled['bib'].get('title','').encode('utf-8').decode('utf-8')
        print(title)
        abstract = pub_filled['bib'].get('abstract','').encode('utf-8').decode('utf-8').replace(',', ' ').replace('\n', ' ').replace('\r', ' ').replace(';',' ')
        authors = pub_filled['bib'].get('author', [])
        date = pub_filled['bib'].get('pub_year','')
        doi = pub_filled.get('pub_url', '')
        lang =""
        if title is not None: 
            try: 
                lang = detect(title)
            except Exception:
                print("Error occurred while detecting language:")
        
        journal = pub_filled['bib'].get('journal', '')    
        conference = pub_filled['bib'].get('conference','')
        if journal == "":
            journal = conference
    
        
        pattern = r"\b(?:and|,|;)\b"
        authors = re.split(pattern, authors)
        authors = [name.strip() for name in authors if name.strip()]

        scholar_publications.append({
                "title": title,
                "abstract": abstract,
                "date": date,
                "doi": doi,
                "journal/book": journal,
                "authors": authors,
                "auth_id": auth_id,
                "lang": lang
            })



    return scholar_publications




