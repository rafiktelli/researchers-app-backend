from parsel import Selector
from playwright.sync_api import sync_playwright
import json
import csv
from langdetect import detect
import pandas as pd

def get_pubs_rgate(auth_id, url):
    if url is None or url == "" or pd.isna(url):
        print("no data for: ", auth_id)
        return []


    with sync_playwright() as p:
        
        browser = p.chromium.launch(headless=True, slow_mo=50)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36")
        
        publications = []
        page_num = 1
        page.goto(url)
        selector = Selector(text=page.content())
        selector2 = Selector(text=page.content())
        
        
        for domaine in selector2.css(".nova-legacy-e-badge"):
            interest = domaine.css('a').xpath("string()").get()
            print("interest: ", interest)

        for publication in selector.css(".nova-legacy-v-publication-item__stack--gutter-m"):
            try:
                title = publication.css(".nova-legacy-v-publication-item__title .nova-legacy-e-link--theme-bare::text").get().title()
                title_link = f'{publication.css(".nova-legacy-v-publication-item__title .nova-legacy-e-link--theme-bare::attr(href)").get()}'
                publication_type = publication.css(".nova-legacy-v-publication-item__badge::text").get()
                
                publication_date = publication.css(".nova-legacy-v-publication-item__meta-data-item:nth-child(1) span::text").get()
                publication_isbn = publication.css(".nova-legacy-v-publication-item__meta-data-item:nth-child(3) span").xpath("normalize-space()").get()
                authors = publication.css(".nova-legacy-v-person-inline-item__fullname::text").getall()
                source_link = f'https://www.researchgate.net{publication.css(".nova-legacy-v-publication-item__preview-source .nova-legacy-e-link--theme-bare::attr(href)").get()}'
                
                page1 = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36")
                page1.goto(f"{title_link}")
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
                "doi": publication_doi,
                "journal/book": journal,
                #"publication_isbn": publication_isbn,
                "authors": authors,
                "auth_id": auth_id,
                "lang": lang
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
    