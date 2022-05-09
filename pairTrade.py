import pandas as pd
import numpy as np
import statsmodels.formula.api as sm
from numpy_ext import rolling_apply
import warnings
warnings.filterwarnings('ignore')

class pairTrade():
    def __init__(self, df, entry, exit, stopLoss, init = 100000, rolling = 20):
        
        """
        Args:
            df (dataframe): input data, column = data, ASymbol, Bsymbol.
            strategyType (string): divergence convergence.
            A_Symbol (string): A symbol name.
            B_Symbol (string): B symbol name.
            entry (float): zscore entry point. 
            exit (float): zscore entry point. 
            stopLoss (float): stopLoss. 
            init (int, optional): initial amount. Defaults to 100000.
            rolling (int, optional): rolling window calculations. Defaults to 20.
            tradeTypeDict (dict): trade type setting.
        """        
        self.df = df
        self.A_Symbol = df.columns[0]
        self.B_Symbol = df.columns[1]
        self.entry = entry
        self.exit = exit
        self.stopLoss = stopLoss
        self.init = init
        self.rolling = rolling
        self.tradeTypeDict = {
            'spread': self._indicatorSpread, 
            'ratio': self._indicatorRatio, 
            'returnSpread': self._indicatorReturnSpread,
            'regression': self._indicatorRegression
        }
    
    def indicator(self, tradeType):
        """
        不同trade的Z-score
        Z-score大於entry, 空A交易對, 多B交易對;Z-score小於entry, 多A交易對, 空B交易對
        
        Args:
            tradeType (string): spread, ratio, returnSpread, regression.        
        """
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
        self.df['ASymbolSide'] = [-1 if i >= self.exit else 1 if i < -self.exit else 0 for i in self.df['zscore'].tolist()]
        
    def _indicatorRatio(self):
        """
        等金額下注
        """
        self.df['Ratio'] = self.df.loc[:,self.A_Symbol]/self.df.loc[:,self.B_Symbol]
        self.df['zscore'] = rolling_apply(self._zScore, self.rolling,self.df.loc[:,'Ratio'])
        self.df['ASymbolSide'] = [-1 if i >= self.exit else 1 if i < -self.exit else 0 for i in self.df['zscore'].tolist()]

    def _indicatorReturnSpread(self):
        """
        等金額下注
        """
        self.df['A_return'] = self.df.loc[:,self.A_Symbol].pct_change()
        self.df['B_return'] = self.df.loc[:,self.B_Symbol].pct_change()
        self.df['returnSpread'] = self.df.loc[:,'A_return'] - self.df.loc[:,'B_return']
        self.df['zscore'] = rolling_apply(self._zScore, self.rolling, self.df.loc[:,'returnSpread'])
        self.df['ASymbolSide'] = [-1 if i >= self.exit else 1 if i < -self.exit else 0 for i in self.df['zscore'].tolist()]

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
        self.df['ASymbolSide'] = [-1 if i >= self.exit else 1 if i < -self.exit else 0 for i in self.df['zscore'].tolist()]
        
    def strategy(self, strategyType):
        """
        Args:
            strategyType (string): divergence convergence.
        """
        self.strategyType = strategyType
        pastStatus = 0
        statusList = []
        if self.strategyType == "convergence":
            self.df['ASymbolSide'] = [-1 if i >= self.exit else 1 if i < -self.exit else 0 for i in self.df['zscore'].tolist()]
        elif self.strategyType == "divergence":
            self.df['ASymbolSide'] = [1 if i >= self.exit else -1 if i < -self.exit else 0 for i in self.df['zscore'].tolist()]
        else:
            raise Exception('strategyType must be divergence or convergence')
        self.df = self.df.dropna()
        for index, row in self.df.iterrows():
            currStatus = 0 if (pastStatus == 1 and row['zscore'] < -self.exit) or (pastStatus == -1 and row['zscore'] > self.exit) else 1 if (pastStatus == 1 and row['zscore'] > self.exit or row['zscore'] > self.entry) and row['zscore'] < self.stopLoss else 2 if row['zscore'] > self.stopLoss else -1 if (pastStatus == -1 and row['zscore'] < -self.exit or row['zscore'] < -self.entry) and row['zscore'] > -self.stopLoss else -2 if row['zscore'] < -self.stopLoss else 0
            statusList.append(currStatus)
        self.df['status'] = currStatus
        
        # $部位狀態完成
        # TODO 進出場操作、報表整理 