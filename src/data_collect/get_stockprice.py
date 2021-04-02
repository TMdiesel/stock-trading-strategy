import os
import time
import sqlite3
import logging
import pickle
from datetime import datetime
import requests
from pyquery import PyQuery
from bs4 import BeautifulSoup
import pandas as pd 


logger=logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_price(code_number,headers):
    """
    年でループ
    """
    dfs = []
    year = range(2000,2021)
    for y in year:
        try:
             url = 'https://kabuoji3.com/stock/{}/{}/'.format(code_number,y)
             soup = BeautifulSoup(requests.get(url,headers=headers).content,'html.parser')
             tag_tr = soup.find_all('tr')
             head = [h.text for h in tag_tr[0].find_all('th')]
             data = []
             for i in range(1,len(tag_tr)):
                 data.append([d.text for d in tag_tr[i].find_all('td')])
             df = pd.DataFrame(data, columns = head)

             col = ['始値','高値','安値','終値','出来高','終値調整']
             for c in col:
                 df[c] = df[c].astype(float)
             dfs.append(df)
        except IndexError:
            pass
    data = pd.concat(dfs,axis=0)
    data = data.reset_index(drop=True)

    return data


def price_generator(code_range):
    """
    銘柄番号でループ
    """
    for code_number in code_range:
        logger.info(code_number)
        data = get_price(code_number,headers)
        tuples = [(code_number,)+tuple(data.iloc[i]) for i in range(len(data))]
        yield tuples
        time.sleep(1)


def insert_prices_to_db(db_file_name,code_range):
    """
    DBに登録
    """
    conn = sqlite3.connect(db_file_name)
    with conn:
        for tuples in price_generator(code_range):
            try:
                sql = """
                INSERT INTO raw_prices(code,date,open,high,low,close,volume,adjust)
                VALUES(?,?,?,?,?,?,?,?)
                """
                conn.executemany(sql,tuples)
            except Exception as e:
                logger.info(e)
   

if __name__=='__main__':
    db_file_name=str(os.environ.get("DB_PATH"))
    headers={
   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }
    with open("./data/codelist_core26.pkl", "rb") as f:
        code_list_core26 = pickle.load(f) 

    insert_prices_to_db(db_file_name,code_list_core26)
