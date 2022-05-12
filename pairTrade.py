import pandas as pd
import numpy as np
import statsmodels.formula.api as sm
from numpy_ext import rolling_apply
import warnings
from action import pairTradeAction
warnings.filterwarnings('ignore')

class pairTrade():
    def __init__(self, df):
        
        """
        Args:
            df (dataframe): input data, column = data, ASymbol, Bsymbol. 
            A_Symbol (string): A symbol name.
            B_Symbol (string): B symbol name.
            tradeTypeDict (dict): trade type setting.
            tradeType (string): spread, ratio, returnSpread, regression.  
        """        
        self.df = df
        self.A_Symbol = df.columns[0]
        self.B_Symbol = df.columns[1]
        self.tradeTypeDict = {
            'spread': self._indicatorSpread, 
            'ratio': self._indicatorRatio, 
            'returnSpread': self._indicatorReturnSpread,
            'regression': self._indicatorRegression
        }
    
    def indicator(self, tradeType, rolling = 20):
        """
        不同trade的Z-score
        Z-score大於entry, 空A交易對, 多B交易對;Z-score小於entry, 多A交易對, 空B交易對
        
        Args:
            tradeType (string): spread, ratio, returnSpread, regression.        
        """
        self.rolling = rolling
        self.tradeType = tradeType
        self.tradeTypeDict[self.tradeType]()
        
        
    def _zScore(self, yport):
        zscore = (yport[-1]  - yport.mean()) / yport.std()
        return zscore
    
    def _indicatorSpread(self):
        """
        等金額下注
        """
        self.df['spread'] = self.df.loc[:,self.A_Symbol] - self.df.loc[:,self.B_Symbol]
        self.df['zscore'] = rolling_apply(self._zScore, self.rolling, self.df['spread'])
        # self.df['ASymbolSide'] = [-1 if i >= self.exit else 1 if i < -self.exit else 0 for i in self.df['zscore'].tolist()]
        
    def _indicatorRatio(self):
        """
        等金額下注
        """
        self.df['Ratio'] = self.df.loc[:,self.A_Symbol]/self.df.loc[:,self.B_Symbol]
        self.df['zscore'] = rolling_apply(self._zScore, self.rolling,self.df.loc[:,'Ratio'])
        # self.df['ASymbolSide'] = [-1 if i >= self.exit else 1 if i < -self.exit else 0 for i in self.df['zscore'].tolist()]

    def _indicatorReturnSpread(self):
        """
        等金額下注
        """
        self.df['A_return'] = self.df.loc[:,self.A_Symbol].pct_change()
        self.df['B_return'] = self.df.loc[:,self.B_Symbol].pct_change()
        self.df['returnSpread'] = self.df.loc[:,'A_return'] - self.df.loc[:,'B_return']
        self.df['zscore'] = rolling_apply(self._zScore, self.rolling, self.df.loc[:,'returnSpread'])
        # self.df['ASymbolSide'] = [-1 if i >= self.exit else 1 if i < -self.exit else 0 for i in self.df['zscore'].tolist()]

    def _indicatorRegression(self):
        """
        比例下注
        """
        hedgeRatio=np.full(self.df.shape[0], 0.0)
        for t in np.arange(self.rolling, len(hedgeRatio)):
            regress_results=sm.ols(formula="{} ~ {}".format(self.A_Symbol, self.B_Symbol), data=self.df[(t-self.rolling):t]).fit() # Note this can deal with NaN in top row
            hedgeRatio[t-1]=regress_results.params[1] ## beta1
        self.df['hedgeRatio'] = hedgeRatio 
        self.df['y_hat'] = self.df.loc[:,self.A_Symbol] - self.df.loc[:,'hedgeRatio'] * self.df.loc[:,self.B_Symbol]
        self.df['zscore'] = rolling_apply(self._zScore, self.rolling, self.df.loc[:,'y_hat'])
        # self.df['ASymbolSide'] = [-1 if i >= self.exit else 1 if i < -self.exit else 0 for i in self.df['zscore'].tolist()]
        
    def strategy(self, strategyType, actionType, entry, exit, stopLoss, init = 100000):
        """
        Args:
            strategyType (string): divergence convergence.
            actionType (string): amount unit.
            entry (float): zscore entry point. 
            exit (float): zscore entry point. 
            stopLoss (float): stopLoss. 
            init (int, optional): initial amount. Defaults to 100000.
            rolling (int, optional): rolling window calculations. Defaults to 20.
        """
        self.strategyType = strategyType
        self.actionType = actionType
        self.entry = entry
        self.exit = exit
        self.stopLoss = stopLoss
        self.init = init
        actionObject = pairTradeAction(self.init, self.actionType)
        
        pastStatus = 0
        date, statusList =  [], []
        
        if self.strategyType == "convergence":
            self.df['ASymbolSide'] = [-1 if i >= self.exit else 1 if i < -self.exit else 0 for i in self.df['zscore'].tolist()]
            self.df['BSymbolSide'] = self.df['hedgeRatio'] * self.df['ASymbolSide'] * -1 if 'hedgeRatio' in self.df.columns else self.df['ASymbolSide'] * -1
        elif self.strategyType == "divergence":
            self.df['ASymbolSide'] = [1 if i >= self.exit else -1 if i < -self.exit else 0 for i in self.df['zscore'].tolist()]
            self.df['BSymbolSide'] = self.df['hedgeRatio'] * self.df['ASymbolSide'] * -1 if 'hedgeRatio' in self.df.columns else self.df['ASymbolSide'] * -1
        else:
            raise Exception('strategyType must be divergence or convergence')

        for index, row in self.df.iterrows():
            currStatus = 0 if (pastStatus == 1 and row['zscore'] < -self.exit) or (pastStatus == -1 and row['zscore'] > self.exit) else 1 if (pastStatus == 1 and row['zscore'] > self.exit or row['zscore'] > self.entry) and row['zscore'] < self.stopLoss else 2 if row['zscore'] > self.stopLoss else -1 if (pastStatus == -1 and row['zscore'] < -self.exit or row['zscore'] < -self.entry) and row['zscore'] > -self.stopLoss else -2 if row['zscore'] < -self.stopLoss else 0
            conStatus = (pastStatus, currStatus)
            pastStatus = currStatus
            actionObject.runAction(conStatus, row[self.A_Symbol],  row[self.B_Symbol], row['ASymbolSide'], row['BSymbolSide'])
            date.append(index)
            statusList.append(currStatus)
            
        self.df['status'] = statusList
        self.df['A_position'] = actionObject.A_positionList
        self.df['B_position'] = actionObject.B_positionList
        self.df['A_asset'] = actionObject.A_assetList
        self.df['B_asset'] = actionObject.B_assetList
        self.df['totalAsset'] = actionObject.totalAssetList
        self.df['available'] = actionObject.availableList
        self.df['PNL'] = self.df['totalAsset'] + self.df['available'] - self.init
        # $部位狀態完成
        # TODO chart、KPI報表整理 