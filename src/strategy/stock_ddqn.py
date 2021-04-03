"""
DDQNを使って株の売買を決定する
"""
#%%
#default package
import os
import sys
import datetime
from collections import defaultdict
from datetime import datetime
import logging

#third package
import pfrl
import torch
import torch.nn
import gym
import numpy

#my package
import src.strategy.stockenv as stockenv
from src.strategy.golden_core30 import *
import src.backtest.simulator as sim


logger = logging.getLogger("__main__").getChild(__name__)


class QFunction(torch.nn.Module):
    def __init__(self, obs_size, n_actions):
        super().__init__()
        self.l1 = torch.nn.Linear(obs_size, 50)
        self.l2 = torch.nn.Linear(50, 50)
        self.l2_2 = torch.nn.Linear(50, 50)
        self.l3 = torch.nn.Linear(50, n_actions)

    def forward(self, x):
        h = x
        h = torch.nn.functional.relu(self.l1(h))
        h = torch.nn.functional.relu(self.l2(h))
        h = torch.nn.functional.relu(self.l2_2(h))
        h = self.l3(h)
        return pfrl.action_value.DiscreteActionValue(h)


class simulator_ddqn:
    def __init__(self,db_file_name:str,deposit:int,code_list,
                    info_num:int,action_num:int,used_days:int):
        self.db_file_name=db_file_name
        self.deposit=deposit
        self.code_list=code_list
        self.info_num=info_num
        self.action_num=action_num
        self.used_days = used_days

    def _create_agent(self,q_func):
        optimizer = torch.optim.Adam(q_func.parameters(), eps=1e-2)
        # Set the discount factor that discounts future rewards.
        gamma = 0.9

        # Use epsilon-greedy for exploration
        explorer = pfrl.explorers.ConstantEpsilonGreedy(
            epsilon=0.3, random_action_func=self.env.action_space.sample)

        # DQN uses Experience Replay.
        # Specify a replay buffer and its capacity.
        replay_buffer = pfrl.replay_buffers.ReplayBuffer(capacity=10 ** 6)

        # Since observations from CartPole-v0 is numpy.float64 while
        # As PyTorch only accepts numpy.float32 by default, specify
        # a converter as a feature extractor function phi.
        phi = lambda x: x.astype(numpy.float32, copy=False)

        # Set the device id to use GPU. To use CPU only, set it to -1.
        gpu = -1

        self.agent = pfrl.agents.DoubleDQN(
            q_func,
            optimizer,
            replay_buffer,
            gamma,
            explorer,
            replay_start_size=500,
            update_interval=1,
            target_update_interval=100,
            phi=phi,
            gpu=gpu,
        )

    def _iteration_learn(self,start_date:datetime,end_date:datetime):
        date_range = [pdate.to_pydatetime().date()
                     for pdate in sim.tse_date_range(start_date, end_date)]
        for i in range(1, self.n_episodes + 1):
            logger.info(f"start episode: {i}")
            for code in self.code_list:
                stocks = create_stock_full_data(self.db_file_name, [code], 
                        start_date-datetime.timedelta(days=self.used_days+10), end_date)
                portfolio = sim.Portfolio(self.deposit)
                obs = self.env.reset(portfolio,code,start_date,stocks,self.used_days)
                R = 0  # return (sum of rewards)
                logger.info(f"episode{i}:start learning of code {code}")
                for date in date_range[:-1]:
                    action = self.agent.act(obs)
                    obs, reward, done, _ = self.env.step(action,portfolio,code,date,stocks,self.used_days)
                    R += reward
                    self.agent.observe(obs, reward, done, reset=False)


    def train(self,start_date:datetime,end_date:datetime,n_episodes:int):
        """
        手数料と税金を考慮して報酬を設定する
        """

        self.n_episodes = n_episodes
        self.env=stockenv.StockEnv(self.info_num,self.action_num)
        obs_size = self.env.observation_space.low.size
        n_actions = self.env.action_space.n
        q_func = QFunction(obs_size, n_actions)
        logger.info(f"obs_size:{obs_size},n_actions:{n_actions}")

        self._create_agent(q_func)
        logger.info("succesfully agent created")
        self._iteration_learn(start_date,end_date)

        return self

    def save(self,dir_name:str='agent'):
        """
        save an agent to the "agent" directory
        """
        self.agent.save(dir_name)


    def _record(self,date:datetime.date,portfolio,stocks,code:int):
        """ 
        本日(d)の損益などを記録
        1つの銘柄のみに対応
        """
        date=datetime.datetime(date.year,date.month,date.day) #convert to datetim
        #logger.info(f"{portfolio.stocks[code].current_count}")
        #logger.info(f"{type(portfolio.stocks[code].current_count)}")

        current_total_price =int(stocks[code]['prices']['close'][date])*portfolio.stocks[code].current_count
        current_total_price+=portfolio.deposit 
        self.total_price_list.append(current_total_price)
        self.profit_or_loss_list.append(current_total_price
                                   - portfolio.amount_of_investment)

    def test(self,start_date:datetime,end_date:datetime):
        """
        ある期間で銘柄を一つ買う→次の期間で… 
        """
        date_range = [pdate.to_pydatetime().date()
                     for pdate in sim.tse_date_range(start_date, end_date)]

        with self.agent.eval_mode():
            logger.info(f"start transaction test")
            for code in self.code_list:
                stocks = create_stock_full_data(self.db_file_name, [code], 
                        start_date-datetime.timedelta(days=self.used_days+10), end_date)
                portfolio = sim.Portfolio(self.deposit)
                obs = self.env.reset(portfolio,code,start_date,stocks,self.used_days)
                R = 0  # return (sum of rewards)
                self.total_price_list = []
                self.profit_or_loss_list = []
                logger.info(f"start transaction of code: {code}")

                for date in date_range[:-1]:
                    action = self.agent.act(obs)
                    obs, reward, done, _ = self.env.step(action,portfolio,code,date,stocks,self.used_days)
                    R += reward
                    self.agent.observe(obs, reward, done, reset=False)
                    self._record(date,portfolio,stocks,code)

                yield portfolio,pd.DataFrame(data={'price': self.total_price_list,
                              'profit': self.profit_or_loss_list},
                                index=pd.DatetimeIndex(date_range[:-1]))

    def evaluate(self):
        pass


def main():
    """テスト"""
    pass


if __name__=='__main__':
    main()

