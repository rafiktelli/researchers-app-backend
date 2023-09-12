import sys 
import csv
import pandas as pd
from .dblp import get_pubs_dblp, get_pubs_rgate, get_pubs_scholar



def extract_publications(auth_id, gs, rg, dblp):
    data = []
    
    dblpData = get_pubs_dblp(auth_id, dblp)
    gsData = get_pubs_scholar(auth_id, gs)
    #rgData = get_pubs_rgate(auth_id, rg)
    
    data.extend(gsData)
    #data.extend(rgData)
    data.extend(dblpData)
    
    fieldnames = ['auth_id', 'doi', 'title', 'abstract', 'authors', 'date', 'journal/book', 'lang']
    df1 = pd.DataFrame(gsData)
    #df2 = pd.DataFrame(rgData)
    df3 = pd.DataFrame(dblpData)
    return df1, df3

    '''
    with open('outputs/extracted_data.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    '''