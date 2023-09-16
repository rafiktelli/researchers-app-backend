import requests
import xml.etree.ElementTree as ET
import json
import csv 
import re
from langdetect import detect
import pandas as pd
from pprint import pprint
from scholarly import scholarly, ProxyGenerator
import csv
from langdetect import detect
import re
import pandas as pd
from parsel import Selector
from playwright.sync_api import sync_playwright
import json
import csv
from langdetect import detect
import pandas as pd

def get_pubs_dblp(auth_id, url):
    print("url: ", url)

    
    if url is None or url == "" or pd.isna(url):
        print("no data for: ", auth_id)
        return []
    if re.search(r"\.xml/?$", url):
        url = url
    elif re.search(r"\.html/?$", url):

        url = re.sub(r"\.html/?$", ".xml", url)
    else:
        url = url + ".xml"

    response = requests.get(url)
    xml_content = response.text

    root = ET.fromstring(xml_content)

    data = []

    for article in root.findall('.//article') + root.findall('.//inproceedings'):
        title = article.find('title').text
        authors = [author.text for author in article.findall('author')]
        year = article.find('year').text
        journal = article.find('journal')
        doi_num = article.find('ee')
        if doi_num is not None: doi_num=doi_num.text
        if journal is not None:
            journal = journal.text
        else:
            book = article.find('booktitle')
            if book is not None:
                journal = book.text
            else: 
                journal = ""
        lang = ""
        if title is not None:
            lang = detect(title)
        else: 
            print("doi: ", doi_num)

        article_data = {
            'title': title,
            'authors': authors,
            'year': year,
            'journal/book': journal,
            "doi": doi_num,
            "auth_id": auth_id,
            "lang": lang,
            "abstract": "",
            "source": "dblp"
        }

        data.append(article_data)

    #json_data = json.dumps(data, indent=4)


    #with open('extracted_data.json', 'w') as f:
    #    f.write(json_data)

    print(data)
    return data
    fieldnames = ['auth_id', 'doi', 'title', 'abstract', 'authors', 'date', 'journal/book', 'lang']

    # Open the CSV file in write mode
    with open('extracted_data.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()

        # Write the data rows
        writer.writerows(data)






def get_pubs_rgate(auth_id, url):

    if url is None or url == "" or pd.isna(url):
        print("no data for: ", auth_id)
        return []


    with sync_playwright() as p:
        
        browser = p.chromium.launch(headless=True, slow_mo=100)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36")
        
        publications = []
        page_num = 1
        page.goto(url, timeout=100000)
        selector = Selector(text=page.content())
        selector2 = Selector(text=page.content())
        
        
        for domaine in selector2.css(".nova-legacy-e-badge"):
            interest = domaine.css('a').xpath("string()").get()
            print("interest: ", interest)

        for publication in selector.css(".nova-legacy-v-publication-item__stack--gutter-m")[:2]:
            
            try:
                title = publication.css(".nova-legacy-v-publication-item__title .nova-legacy-e-link--theme-bare::text").get().title()
                title_link = f'{publication.css(".nova-legacy-v-publication-item__title .nova-legacy-e-link--theme-bare::attr(href)").get()}'
                publication_type = publication.css(".nova-legacy-v-publication-item__badge::text").get()
                
                publication_date = publication.css(".nova-legacy-v-publication-item__meta-data-item:nth-child(1) span::text").get()
                publication_isbn = publication.css(".nova-legacy-v-publication-item__meta-data-item:nth-child(3) span").xpath("normalize-space()").get()
                authors = publication.css(".nova-legacy-v-person-inline-item__fullname::text").getall()
                source_link = f'https://www.researchgate.net{publication.css(".nova-legacy-v-publication-item__preview-source .nova-legacy-e-link--theme-bare::attr(href)").get()}'
                
                page1 = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36")
                page1.goto(f"{title_link}", timeout=100000)
                selector1 = Selector(text=page1.content())
                abstract = selector1.css(".research-detail-middle-section__abstract::text").get()
                publication_date = selector1.xpath('//meta[@property="citation_publication_date"]').xpath('@content').get()
                publication_doi = selector1.xpath('//meta[@property="citation_doi"]').xpath('@content').get()
                journal = selector1.xpath('//meta[@property="citation_journal_title"]').xpath('@content').get()
                book = selector1.xpath('//meta[@property="citation_inbook_title"]').xpath('@content').get()
                conference = selector1.xpath('//meta[@property="citation_conference_title"]').xpath('@content').get()
            except Exception:
                continue
            if journal is None: journal = book
            if journal is None: journal = conference
            if abstract is None: 
                abstract = ""
            else: 
                abstract = abstract
            lang = ""
            if title is not None: 
                title
                try: 
                    lang = detect(title)
                except Exception:
                    print("Error occurred while detecting language:")
            
            print(auth_id, ": ", title)

            try: 
                title = title.encode('latin-1').decode('utf-8')
            except Exception :
                pass
            
            try: 
                abstract = abstract.encode('latin-1').decode('utf-8')
            except Exception:
                pass
            

            publications.append({
                "title": title,
                "abstract": abstract.replace(',', ' ').replace('\n', ' ').replace('\r', ' ').replace(';',' '),
                #"link": title_link,
                #"source_link": source_link,
                #"publication_type": publication_type,
                "date": publication_date,
                "doi": "https://doi.org/" + publication_doi,
                "journal/book": journal,
                #"publication_isbn": publication_isbn,
                "authors": authors,
                "auth_id": auth_id,
                "lang": lang,
                "source" : "rg"
            })
        
        #with open("output.json", "w", encoding="utf-8") as file:
        #    json.dump(publications, file, indent=2, ensure_ascii=False)

        fieldnames = ['auth_id', 'doi', 'title', 'abstract', 'authors', 'date', 'journal/book', 'lang']
        
        

        #with open('output.csv', 'w', newline='') as f:
        #    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=",")
        #    writer.writeheader()
        #    writer.writerows(publications)



        browser.close()
        return publications
    
    
    






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
                "lang": lang,
                "source": "gs"
            })



    return scholar_publications




