import sys 
import csv
import pandas as pd
from .dblp import get_pubs_dblp, get_pubs_rgate, get_pubs_scholar



def extract_publications(auth_id, gs, rg, dblp):
    data = []
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    df3 = pd.DataFrame()
    if len(gs)>8:
        gsData = get_pubs_scholar(auth_id, gs)
        data.extend(gsData)
        df1 = pd.DataFrame(gsData)
    if 0>8:
        rgData = get_pubs_rgate(auth_id, rg)
        data.extend(rgData)
        df2 = pd.DataFrame(rgData)
    if len(dblp)>8:
        dblpData = get_pubs_dblp(auth_id, dblp)
        data.extend(dblpData)
        df3 = pd.DataFrame(dblpData)
    print('extraction ended')
    return df1, df2, df3

    '''
    #fieldnames = ['auth_id', 'doi', 'title', 'abstract', 'authors', 'date', 'journal/book', 'lang']
    with open('outputs/extracted_data.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    '''