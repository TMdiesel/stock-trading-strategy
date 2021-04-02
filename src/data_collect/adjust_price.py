"""core26に入っている銘柄だけ修正"""
import os
import datetime
import sqlite3
from dataclasses import dataclass
import pickle


@dataclass
class Config():
    db_name:str = str(os.environ.get("DB_PATH"))
    date_of_right_allotment='2020-08-25'


def get_divide_union_data(db_file_name:str, date_of_right_allotment:str
                           )->tuple:
    """
    date_of_right_allotmentかつdata_now 以前の
    分割・併合データで未適用のものを取得する
    """
    conn = sqlite3.connect(db_file_name)

    sql = """
    SELECT 
        d.code, d.date_of_right_allotment, d.before, d.after
    FROM 
        divide_union_data AS d
    WHERE
        d.date_of_right_allotment < ?
        AND NOT EXISTS (
            SELECT 
                * 
            FROM 
                applied_divide_union_data AS a
            WHERE 
                d.code = a.code
                AND d.date_of_right_allotment = a.date_of_right_allotment
            ) 
    ORDER BY 
        d.date_of_right_allotment
    """
    with conn:
        cur = conn.execute(sql, (date_of_right_allotment,))
    divide_union_data = cur.fetchall()

    return divide_union_data


def apply_divide_union_data(db_file_name:str, date_of_right_allotment:str,
                            divide_union_data)->None:
    conn = sqlite3.connect(db_file_name)
    with conn:
        conn.execute('BEGIN TRANSACTION')
        i=0 #
        print(len(divide_union_data)) #
        for code, date_of_right_allotment, before, after in divide_union_data:
            i+=1 #
            print(i) #
            
            rate = before / after
            inv_rate = 1 / rate
            
            if rate>1: #union
                conn.execute(
                  'UPDATE prices SET '
                  ' open = open * :rate, '
                  ' high = high * :rate, '
                  ' low = low  * :rate, '
                  ' close = close * :rate, '
                  ' volume = volume * :inv_rate '
                  'WHERE code = :code '
                  '  AND date <= :date_of_right_allotment',
                  {'code' : code,
                   'date_of_right_allotment' : date_of_right_allotment,
                   'rate' : rate,
                   'inv_rate' : inv_rate})
            elif rate<1: #divide
                conn.execute(
                  'UPDATE prices SET '
                  ' open = open * :rate, '
                  ' high = high * :rate, '
                  ' low = low  * :rate, '
                  ' close = close * :rate, '
                  ' volume = volume * :inv_rate '
                  'WHERE code = :code '
                  '  AND date < :date_of_right_allotment',
                  {'code' : code,
                   'date_of_right_allotment' : date_of_right_allotment,
                   'rate' : rate,
                   'inv_rate' : inv_rate})

                          
            conn.execute(
              'INSERT INTO '
              'applied_divide_union_data(code, date_of_right_allotment) '
              'VALUES(?,?)',
              (code, date_of_right_allotment))


if __name__=='__main__':
    divide_union_data=get_divide_union_data(Config.db_name,
                        Config.date_of_right_allotment)
    with open('./data/codelist_core26.pkl','rb') as f:
        codelist26=pickle.load(f)
    divide_union_data=[data for data in divide_union_data if data[0] in codelist26]
    apply_divide_union_data(Config.db_name,Config.date_of_right_allotment,
                             divide_union_data)

