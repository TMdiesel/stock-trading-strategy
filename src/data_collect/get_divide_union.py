import sqlite3
import os
import pathlib
import typing as t
import sqlalchemy
from sqlalchemy import MetaData,Column,Table,Float,Text,Integer
from dataclasses import dataclass


@dataclass
class Config():
    table_name:str='divide_union_data'
    db_name:str=str(os.environ.get("DB_PATH"))
    filelist =[pathlib.Path('./data/union.dat')
              ,pathlib.Path('./data/divide.dat')]


def dat_to_dict(filename:pathlib.Path) ->  t.Dict:
    """
    - ./data/divide.dat
    - ./data/union.dat
    を読み込んで辞書にする
    """
    with open(filename,'r',encoding='utf-8') as f:
        data_list=f.readlines()
    splited_data_list=[data.split('\t') for data in data_list]
    if filename.stem=='union':
        replaced_data_list=[[field.replace('\n','').replace('株→1株','') for field in data] for data in splited_data_list]
        data_dict=[{'date_of_right_allotment':data[4].replace('/','-'),'code':int(data[1]),'name':data[2],
        'before':float(data[3]),'after':1} for data in replaced_data_list]
    elif filename.stem=='divide':
        replaced_data_list=[[field.replace('\n','').replace('1：','') for field in data] for data in splited_data_list]
        data_dict=[{'date_of_right_allotment':data[6].replace('/','-'),'code':int(data[1]),'name':data[2],
        'before':1,'after':float(data[3])} for data in replaced_data_list]

    return data_dict


def create_engine(db_name:str)->sqlalchemy.engine:
    """
    engine作成
    """
    connect_name='sqlite:///%s'%(db_name)
    return sqlalchemy.create_engine(connect_name, echo=True)


def insert_data(table:sqlalchemy.Table,engine:sqlalchemy.engine,
                data_dict:t.Dict)->None:
    """dataをinsert"""
    with engine.connect() as conn:
        conn.execute(table.insert(),
        data_dict)


def create_table(meta:sqlalchemy.MetaData,engine:sqlalchemy.engine
                  ,table_name:str)->None:
    """table作成"""
    table=Table(table_name,meta,
    Column('date_of_right_allotment',Text, primary_key=True),
    Column('code',Integer, primary_key=True),
    Column('name',Text),
    Column('before',Float),
    Column('after',Float)
    )
    meta.create_all(engine)


def main():
    """"mainスクリプト"""
    meta=MetaData()
    engine=create_engine(Config.db_name)
    create_table(meta,engine,Config.table_name)
    table=Table(Config.table_name,meta,autoload=True)
    for filename in Config.filelist:
        data_dict=dat_to_dict(filename)
        insert_data(table,engine,data_dict)


if __name__=='__main__':
    main()

