import sys 
import csv
import pandas as pd
import re
from pprint import pprint
from scholarly import scholarly, ProxyGenerator
import csv
from langdetect import detect
import re
import pandas as pd
from playwright.sync_api import sync_playwright
from parsel import Selector


def get_interests_scholar(auth_id, url):
    print("start interests_scholar : ")
    #VERIFY URL COMPTABILITY
    if url is None or url == "" or pd.isna(url):
        print("no data for: ", auth_id)
        interests = []
        interests.append({
                    "auth_id": auth_id,
                    "interests": " '' ",
                    })
        print("ended with interests: ")
        print("here are : ", interests)
        return interests


    #EXTRACT USER ID 
    pattern = r'user=([^&]+)'
    match = re.search(pattern, url)
    print("here is the url: ", url)
    
    if match:
        user_id = match.group(1)
        print("there is a match !!!!")
    else: 
        print("ended with interests: ")
        print("here are : nothing" )
        interests = []
        interests.append({
                    "auth_id": auth_id,
                    "interests": " '' ",
                    })
        return interests
    print("user ID: ", user_id)
    author = scholarly.search_author_id(user_id)
    scholar = scholarly.fill(author, 
                            sections=['basics', 'publications'],
                            sortby="year",
                            publication_limit=106
                            )

    interests = []

    interests.append({
                "auth_id": auth_id,
                "interests": scholar['interests'],
                })
    print("scholar skills: ")
    print(scholar['interests'])
    return interests

def get_interests_rgate(auth_id, url):
    if url is None or url == "" or pd.isna(url):
        print("no data for: ", auth_id)
        interests = []
        interests.append({
                    "auth_id": auth_id,
                    "interests": " '' ",
                    })

        return interests
        

    with sync_playwright() as p:
        
        browser = p.chromium.launch(headless=True, slow_mo=50)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36")
        publications = []
        page_num = 1
        page.goto(url)
        selector = Selector(text=page.content())
        skills = []
        for domaine in selector.css(".nova-legacy-e-badge"):
            skill = domaine.css('a').xpath("string()").get()
            if skill is not None:
                skills.append(skill)
    
    
    interests = []
    interests.append({ "auth_id": auth_id, "interests": skills})
    print("rgate skills: ")
    print(skills)
    return interests
