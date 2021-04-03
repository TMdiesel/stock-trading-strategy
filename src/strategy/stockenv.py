"""
株式環境のクラス
 - gym.envを継承する
 - 一つの銘柄の売買のみに対応
"""
#%%
# default package
import math
import os
import sys
import typing as t
from datetime import datetime
import logging

# third package
import gym
from gym import spaces, logger
from gym.utils import seeding
import numpy as np

# my package
import src.backtest.simulator as sim

logger = logging.getLogger("__main__").getChild(__name__)


class StockEnv(gym.Env):

    metadata={}
    
    def __init__(self,info_num:int,action_num:int=3):
        """
        Args:
            action_num (int): number of actions per 1 stock
                とりあえず3としておく(buy,hold,sell)
            info_num (int): 用いる情報の数 per 1 stock
        """        

        self.action_space=spaces.Discrete(action_num)
        high=np.array([np.finfo(np.float32).max for _ in range(info_num)]
                        ,dtype=np.float32)
        self.observation_space=spaces.Box(-high,high,dtype=np.float32)

        self.state=None
        self.steps_beyond_done = None
        self.done = False

    def step(self,action:int,portfolio,code:int,date:datetime,stocks,used_days:int):
        """
        Args:
            action (int) : 売買行動
                0: buy
                1: hold
                2: sell
            portfolio : 所持金などを記録したクラス
            code : 銘柄
            date : 日付
            stocks: 単元株数と始値、終値、高値、低値、出来高を含む辞書を作成
            used_days:用いる情報の日数

        Returns:
            state,reward,done
        """        

        err_msg = "%r (%s) invalid" % (action, type(action))
        assert self.action_space.contains(action), err_msg

        def get_open_price_func(date, code):
            return stocks[code]['prices']['open'][str(date)]
        def execute_order(d, orders):
               # 本日(d)において注文(orders)をすべて執行する
               for order in orders:
                   order.execute(d, portfolio,
                                 lambda code: get_open_price_func(d, code))

        order_list=[]
        if action==2:  #sell
            s_all=portfolio.stocks[code].current_count # 売却前に保有している株数
            order_list.append(sim.SellMarketOrder(code,
                                    portfolio.stocks[code].current_count))
            execute_order(date,order_list)
            if s_all!=0:
                s_now=portfolio.stocks[code].current_count # 現在保有している株数
                p_buy=portfolio.stocks[code].average_cost  # 平均取得価額
                p_sell=get_open_price_func(date,code)
                s_sell=s_all-s_now #売却株数
                reward=(p_sell-p_buy)/p_buy*s_sell/s_all
            else:
                reward=0
        elif action==0:  #buy
            order_list.append(sim.BuyMarketOrderAsPossible(code,
                                    stocks[code]['unit']))
            execute_order(date,order_list)
            reward=0
        elif action==1:  #hold
            reward=0

        self.state =  calc_stock_state(portfolio,code,date,stocks,used_days)

        return np.array(self.state), reward, self.done, {}

    def reset(self,portfolio,code:int,start_date:datetime,stocks,used_days):
        self.state = calc_stock_state(portfolio,code,start_date,stocks,used_days)
        self.steps_beyond_done = None
        return np.array(self.state)


def calc_stock_state(portfolio,code:int,date:datetime,stocks,used_days:int):
    """
    状態を計算
    - 株価・テクニカル指標・出来高の時系列情報
    - 総資産、所持株数

    Args:
    stocks: 単元株数と始値、終値、高値、低値、出来高を含む辞書を作成
    used_days: 用いる情報の日数
    """
    stock_df=stocks[code]['prices']
    date=datetime(date.year,date.month,date.day) #convert to datetime

    try:
        time_series_array=stock_df[stock_df.index<=date][-used_days:].values
    except Exception as e:
        logger.error("datetime comparison error")
        logger.error(e)

    time_series_array=time_series_array/time_series_array[0]  #normalization
    time_series_list=list(time_series_array.flatten())

    s1=portfolio.initial_deposit
    s2=portfolio.stocks[code].total_cost    # 取得にかかったコスト（総額)
    s3=portfolio.stocks[code].current_count # 現在保有している株数
    s4=portfolio.stocks[code].average_cost  # 平均取得価額

    return time_series_list+[s1,s2,s3,s4]

