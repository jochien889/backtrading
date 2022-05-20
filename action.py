class pairTradeAction():
    def __init__(self, init, actionType):
        """_summary_

        Args:
            A_PriceList (list): A交易對價格變化歷程
            B_PriceList (list): B交易對價格變化歷程
            A_positionList (list): A交易對部位變化歷程
            B_positionList (list): B交易對部位變化歷程
            A_assetList (list): A交易對未實現損益變化歷程
            B_assetList (list): B交易對未實現損益變化歷程
            totalAssetList (list): portfolio未實現損益變化歷程
            availableList (list): 可用資金變化歷程
            A_EntryPrice (float): 紀錄A交易對進場價格
            B_EntryPrice (float): 紀錄B交易對進場價格
            init (float): 初始本金          
            AlongEntry (list): A交易對做多點位歷程
            AshortEntry (list): A交易對做空點位歷程
            AlongExit (list): A交易對平多點位歷程
            AshortExit (list): A交易對憑空點位歷程
        """
        self.A_PriceList = []
        self.B_PriceList = []
        self.A_positionList = []
        self.B_positionList = []
        self.A_assetList = [] 
        self.B_assetList = []
        self.totalAssetList = []
        self.availableList = []
        self.A_EntryPrice = 0
        self.B_EntryPrice = 0
        self.init = init

        self.AlongEntry = []
        self.AshortEntry = []
        self.AlongExit = []
        self.AshortExit = []
        # self.Alongstoploss = []
        # self.Ashortstoploss = []     

        self.actionType = actionType
        self.strategy = {(0,1): self._forwardEntry, 
                        (0,2): self._exitForwardStoploss,
                        (0,-1): self._backwardEntry,
                        (0,-2): self._exitBackwardStoploss,
                        (1,0): self._backwardExit,
                        (1,2): self._entryForwardStoploss, 
                        (1,-1): self._exitBackwardEntry, 
                        (1,-2): self._entryBackwardStoploss2, 
                        (2,0) : self._stoplossBackwardExit,
                        (2,1) : self._stoplossBackwardEntry, 
                        (2,-1) : self._stoplossBackwardEntry2, 
                        (2,-2) : self._stoplossBackward, 
                        (-1,0) : self._forwardExit, 
                        (-1,1) : self._exitForwardEntry, 
                        (-1,2) : self._entryForwardStoploss2, 
                        (-1,-2) : self._entryBackwardStoploss, 
                        (-2,0) : self._stoplossForwardExit, 
                        (-2,1) : self._stoplossForwardEntry2,
                        (-2,2) : self._stoplossForward, 
                        (-2,-1) : self._stoplossForwardEntry, }   

    def runAction(self, strategyKey, A_Price, B_Price, A_Side, B_Side):
        """
        Args:
            strategyKey (tuple): pair status code.
        """
        self.strategyKey = strategyKey
        self.A_Price = A_Price
        self.B_Price = B_Price
        self.A_Side = A_Side
        self.B_Side = B_Side

        ### self.B_positionList[-1] if len(self.B_positionList)>0 else 0
        if strategyKey not in self.strategy:
            self.AlongEntry.append(0)
            self.AshortEntry.append(0)
            self.AlongExit.append(0)
            self.AshortExit.append(0)
            # self.Alongstoploss.append(0)
            # self.Ashortstoploss.append(0)
            self.A_PriceList.append(self.A_Price)
            self.B_PriceList.append(self.B_Price)
            self.A_positionList.append(self.A_positionList[-1] if len(self.A_positionList)>0 else 0)
            self.B_positionList.append(self.B_positionList[-1] if len(self.B_positionList)>0 else 0)
            self.A_assetList.append(abs(self.A_positionList[-1]) * (self.A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - self.A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0)
            self.B_assetList.append(abs(self.B_positionList[-1]) * (B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0)
            self.totalAssetList.append( (self.A_assetList[-1] + self.B_assetList[-1]) if (self.A_assetList[-1] + self.B_assetList[-1]) != 0 else 0)
            if self.availableList:
                self.availableList.append(self.availableList[-1] if (self.A_assetList[-1] + self.B_assetList[-1]) == 0 else 0)
            else:
                self.availableList.append(self.init)
        else:
            self.strategy[strategyKey]()
        
    def _stoplossBackwardEntry2(self):
        """
        statusList = (2, -1)
        long B 
        short A  
        """
        self.AlongEntry.append(1)
        self.AshortEntry.append(0)
        self.AlongExit.append(0)
        self.AshortExit.append(0)
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        if self.actionType == 'amount':
            A_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            B_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset)
            self.A_positionList.append(A_asset * self.A_Side/self.A_Price)
            self.B_positionList.append(B_asset * self.B_Side/self.B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        elif self.actionType == 'unit':
            A_asset = self.availableList[-1]/(1+abs(self.B_Side)) if len(self.availableList) else self.init/(1+abs(self.B_Side))
            B_asset = A_asset * abs(self.B_Side)
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset) 
            self.A_positionList.append(A_asset * self.A_Side/self.A_Price)
            self.B_positionList.append(A_asset * self.B_Side/self.B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        self.A_EntryPrice = self.A_Price
        self.B_EntryPrice = self.B_Price
        
    def _stoplossForwardEntry2(self):
        """
        statusList = (-2, 1)
        long A 
        short B    
        """
        ### 出場
        self.AlongEntry.append(0)
        self.AshortEntry.append(1)
        self.AlongExit.append(0)
        self.AshortExit.append(0)
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        if self.actionType == 'amount':
            A_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            B_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset)
            self.A_positionList.append(A_asset * self.A_Side/self.A_Price)
            self.B_positionList.append(B_asset * self.B_Side/self.B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        elif self.actionType == 'unit':
            A_asset = self.availableList[-1]/(1+abs(self.B_Side)) if len(self.availableList) else self.init/(1+abs(self.B_Side))
            B_asset = A_asset * abs(self.B_Side)
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset) 
            self.A_positionList.append(A_asset * self.A_Side/self.A_Price)
            self.B_positionList.append(A_asset * self.B_Side/self.B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        self.A_EntryPrice = self.A_Price
        self.B_EntryPrice = self.B_Price

    def _stoplossBackwardEntry(self):
        """
        statusList = (2,1)
        long A 
        short B    
        """
        self.AlongEntry.append(0)
        self.AshortEntry.append(1)
        self.AlongExit.append(0)
        self.AshortExit.append(0)
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        if self.actionType == 'amount':
            A_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            B_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset)
            self.A_positionList.append(A_asset * self.A_Side/self.A_Price)
            self.B_positionList.append(B_asset * self.B_Side/self.B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        elif self.actionType == 'unit':
            A_asset = self.availableList[-1]/(1+abs(self.B_Side)) if len(self.availableList) else self.init/(1+abs(self.B_Side))
            B_asset = A_asset * abs(self.B_Side)
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset) 
            self.A_positionList.append(A_asset * self.A_Side/self.A_Price)
            self.B_positionList.append(A_asset * self.B_Side/self.B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        self.A_EntryPrice = self.A_Price
        self.B_EntryPrice = self.B_Price

    def _stoplossForwardEntry(self):
        """
        statusList = (-2,-1)
        long B 
        short A    
        """
        self.AlongEntry.append(1)
        self.AshortEntry.append(0)
        self.AlongExit.append(0)
        self.AshortExit.append(0)
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        if self.actionType == 'amount':
            A_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            B_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset)
            self.A_positionList.append(A_asset * self.A_Side/self.A_Price)
            self.B_positionList.append(B_asset * self.B_Side/self.B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        elif self.actionType == 'unit':
            A_asset = self.availableList[-1]/(1+abs(self.B_Side)) if len(self.availableList) else self.init/(1+abs(self.B_Side))
            B_asset = A_asset * abs(self.B_Side)
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset) 
            self.A_positionList.append(A_asset * self.A_Side/self.A_Price)
            self.B_positionList.append(A_asset * self.B_Side/self.B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        self.A_EntryPrice = self.A_Price
        self.B_EntryPrice = self.B_Price
        
    def _entryForwardStoploss(self):
        """
        statusList = (1, 2)
        long A 
        short B
        close the position
        """
        self.AlongEntry.append(0)
        self.AshortEntry.append(0)
        self.AlongExit.append(0)
        self.AshortExit.append(1)
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        ## 可用資金
        A_available = abs(self.A_positionList[-1]) * (self.A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - self.A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0
        B_available = abs(self.B_positionList[-1]) * (self.B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - self.B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0
        self.availableList.append(A_available + B_available)
        ## 部位資產
        self.A_assetList.append(0)
        self.B_assetList.append(0)
        self.totalAssetList.append(0)
        self.A_positionList.append(0)
        self.B_positionList.append(0)

    def _entryBackwardStoploss2(self):
        """
        statusList = (1, -2)
        long A 
        short B
        close the position
        """
        self.AlongEntry.append(0)
        self.AshortEntry.append(0)
        self.AlongExit.append(0)
        self.AshortExit.append(1)
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        ## 可用資金
        A_available = abs(self.A_positionList[-1]) * (self.A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - self.A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0
        B_available = abs(self.B_positionList[-1]) * (self.B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - self.B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0
        self.availableList.append(A_available + B_available)
        ## 部位資產
        self.A_assetList.append(0)
        self.B_assetList.append(0)
        self.totalAssetList.append(0)
        self.A_positionList.append(0)
        self.B_positionList.append(0)
        
    def _entryBackwardStoploss(self):
        """
        statusList = (-1,-2)
        long B 
        short A
        close the position  
        """
        self.AlongEntry.append(0)
        self.AshortEntry.append(0)
        self.AlongExit.append(1)
        self.AshortExit.append(0)
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        ## 可用資金
        A_available = abs(self.A_positionList[-1]) * (self.A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - self.A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0
        B_available = abs(self.B_positionList[-1]) * (self.B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - self.B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0
        self.availableList.append(A_available + B_available)
        ## 部位資產
        self.A_assetList.append(0)
        self.B_assetList.append(0)
        self.totalAssetList.append(0)
        self.A_positionList.append(0)
        self.B_positionList.append(0)
        
    def _entryForwardStoploss2(self):
        """
        statusList = (-1,2)
        long B 
        short A
        close the position  
        """
        self.AlongEntry.append(0)
        self.AshortEntry.append(0)
        self.AlongExit.append(1)
        self.AshortExit.append(0)
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        ## 可用資金
        A_available = abs(self.A_positionList[-1]) * (self.A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - self.A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0
        B_available = abs(self.B_positionList[-1]) * (self.B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - self.B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0
        self.availableList.append(A_available + B_available)
        ## 部位資產
        self.A_assetList.append(0)
        self.B_assetList.append(0)
        self.totalAssetList.append(0)
        self.A_positionList.append(0)
        self.B_positionList.append(0)

    def _forwardEntry(self):
        """
        statusList = (0,1)
        """
        self.AlongEntry.append(0)
        self.AshortEntry.append(1)
        self.AlongExit.append(0)
        self.AshortExit.append(0)
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        if self.actionType == 'amount':
            A_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            B_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset)
            self.A_positionList.append(A_asset * self.A_Side/self.A_Price)
            self.B_positionList.append(B_asset * self.B_Side/self.B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        elif self.actionType == 'unit':
            A_asset = self.availableList[-1]/(1+abs(self.B_Side)) if len(self.availableList) else self.init/(1+abs(self.B_Price))
            B_asset = A_asset * abs(self.B_Side)
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset) 
            self.A_positionList.append(A_asset * self.A_Side/self.A_Price)
            self.B_positionList.append(A_asset * self.B_Side/self.B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        self.A_EntryPrice = self.A_Price
        self.B_EntryPrice = self.B_Price
            
    def _backwardEntry(self):
        """
        statusList = (0,-1)
        A:long
        B:short
        """
        self.AlongEntry.append(1)
        self.AshortEntry.append(0)
        self.AlongExit.append(0)
        self.AshortExit.append(0)
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        if self.actionType == 'amount':
            A_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            B_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset)
            self.A_positionList.append(A_asset * self.A_Side/self.A_Price)
            self.B_positionList.append(B_asset * self.B_Side/self.B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        elif self.actionType == 'unit':
            A_asset = self.availableList[-1]/(1+abs(self.B_Side))  if len(self.availableList) else self.init/(1+abs(self.B_Side)) 
            B_asset = A_asset * abs(self.B_Side)
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset) 
            self.A_positionList.append(A_asset * self.A_Side/self.A_Price)
            self.B_positionList.append(A_asset * self.B_Side/self.B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        self.A_EntryPrice = self.A_Price
        self.B_EntryPrice = self.B_Price

    def _backwardExit(self):
        """
        statusList = (1,0)
        long A
        short B
        close the position
        """
        self.AlongEntry.append(0)
        self.AshortEntry.append(0)
        self.AlongExit.append(0)
        self.AshortExit.append(1)
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        ## 可用資金
        A_available = abs(self.A_positionList[-1]) * (self.A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - self.A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0
        B_available = abs(self.B_positionList[-1]) * (self.B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - self.B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0
        self.availableList.append(A_available + B_available)
        ## 部位資產
        self.A_assetList.append(0)
        self.B_assetList.append(0)
        self.totalAssetList.append(0)
        self.A_positionList.append(0)
        self.B_positionList.append(0)

        
    def _exitBackwardEntry(self):
        """
        statusList = (1,-1)
        long A
        short B
        close the position
        long B 
        short A
        """
        self.AlongEntry.append(1)
        self.AshortEntry.append(0)
        self.AlongExit.append(0)
        self.AshortExit.append(0)
        ### 出場
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        ## 可用資金
        A_available = abs(self.A_positionList[-1]) * (self.A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - self.A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0
        B_available = abs(self.B_positionList[-1]) * (self.B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - self.B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0
        available = A_available +B_available
        
        ### 進場
        if self.actionType == 'amount':
            A_asset = available/2
            B_asset = available/2
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset)
            self.A_positionList.append(A_asset * self.A_Side/self.A_Price)
            self.B_positionList.append(B_asset * self.B_Side/self.B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        elif self.actionType == 'unit':
            A_asset = self.availableList[-1]/(1+abs(self.B_Side)) 
            B_asset = A_asset * abs(self.B_Side)
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset) 
            self.A_positionList.append(A_asset * self.A_Side/self.A_Price)
            self.B_positionList.append(A_asset * self.B_Side/self.B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        self.A_EntryPrice = self.A_Price
        self.B_EntryPrice = self.B_Price
        
    def _forwardExit(self):
        """
        statusList = (-1,0)
        long B
        short A
        close the position
        """
        self.AlongEntry.append(0)
        self.AshortEntry.append(0)
        self.AlongExit.append(1)
        self.AshortExit.append(0)
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        ## 可用資金
        A_available = abs(self.A_positionList[-1]) * (self.A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - self.A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0
        B_available = abs(self.B_positionList[-1]) * (self.B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - self.B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0
        self.availableList.append(A_available + B_available)
        ## 部位資產
        self.A_assetList.append(0)
        self.B_assetList.append(0)
        self.totalAssetList.append(0)
        self.A_positionList.append(0)
        self.B_positionList.append(0)
        
    def _exitForwardEntry(self):
        """
        statusList = (-1,1)
        long B
        short A
        close the position
        long A
        short B
        """
        self.AlongEntry.append(0)
        self.AshortEntry.append(1)
        self.AlongExit.append(0)
        self.AshortExit.append(0)
        ### 出場
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        ## 可用資金
        A_available = abs(self.A_positionList[-1]) * (self.A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - self.A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0
        B_available = abs(self.B_positionList[-1]) * (self.B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - self.B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0
        available = A_available +B_available
        
        ### 進場
        if self.actionType == 'amount':
            A_asset = available/2
            B_asset = available/2
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset)
            self.A_positionList.append(A_asset * self.A_Side/self.A_Price)
            self.B_positionList.append(B_asset * self.B_Side/self.B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        elif self.actionType == 'unit':
            A_asset = self.availableList[-1]/(1+abs(self.B_Side)) 
            B_asset = A_asset * abs(self.B_Side)
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset) 
            self.A_positionList.append(A_asset * self.A_Side/self.A_Price)
            self.B_positionList.append(A_asset * self.B_Side/self.B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        self.A_EntryPrice = self.A_Price
        self.B_EntryPrice = self.B_Price
        
    def _exitForwardStoploss(self):
        """
        出場點 -> 正指損點 --不動作
        statusList = (0,2)
        """
        self.AlongEntry.append(0)
        self.AshortEntry.append(0)
        self.AlongExit.append(0)
        self.AshortExit.append(0)
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        self.A_positionList.append(self.A_positionList[-1] if len(self.A_positionList)>0 else 0)
        self.B_positionList.append(self.B_positionList[-1] if len(self.B_positionList)>0 else 0)
        self.A_assetList.append(abs(self.A_positionList[-1]) * (self.A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - self.A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0)
        self.B_assetList.append(abs(self.B_positionList[-1]) * (self.B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - self.B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0)
        self.totalAssetList.append( (self.A_assetList[-1] + self.B_assetList[-1]) if (self.A_assetList[-1] + self.B_assetList[-1]) != 0 else 0)
        if self.availableList:
            self.availableList.append(self.availableList[-1] if (self.A_assetList[-1] + self.B_assetList[-1]) == 0 else 0)
        else:
            self.availableList.append(self.init)

    def _exitBackwardStoploss(self):
        """
        出場點 -> 負指損點 --不動作
        statusList = (0,-2)
        """
        self.AlongEntry.append(0)
        self.AshortEntry.append(0)
        self.AlongExit.append(0)
        self.AshortExit.append(0)
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        self.A_positionList.append(self.A_positionList[-1] if len(self.A_positionList)>0 else 0)
        self.B_positionList.append(self.B_positionList[-1] if len(self.B_positionList)>0 else 0)
        self.A_assetList.append(abs(self.A_positionList[-1]) * (self.A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - self.A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0)
        self.B_assetList.append(abs(self.B_positionList[-1]) * (self.B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - self.B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0)
        self.totalAssetList.append( (self.A_assetList[-1] + self.B_assetList[-1]) if (self.A_assetList[-1] + self.B_assetList[-1]) != 0 else 0)
        if self.availableList:
            self.availableList.append(self.availableList[-1] if (self.A_assetList[-1] + self.B_assetList[-1]) == 0 else 0)
        else:
            self.availableList.append(self.init)
            
    def _stoplossBackwardExit(self):
        """
        正指損點 -> 出場點 --不動作
        statusList = (2, 0)
        """
        self.AlongEntry.append(0)
        self.AshortEntry.append(0)
        self.AlongExit.append(0)
        self.AshortExit.append(0)
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        self.A_positionList.append(self.A_positionList[-1] if len(self.A_positionList)>0 else 0)
        self.B_positionList.append(self.B_positionList[-1] if len(self.B_positionList)>0 else 0)
        self.A_assetList.append(abs(self.A_positionList[-1]) * (self.A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - self.A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0)
        self.B_assetList.append(abs(self.B_positionList[-1]) * (self.B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - self.B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0)
        self.totalAssetList.append( (self.A_assetList[-1] + self.B_assetList[-1]) if (self.A_assetList[-1] + self.B_assetList[-1]) != 0 else 0)
        if self.availableList:
            self.availableList.append(self.availableList[-1] if (self.A_assetList[-1] + self.B_assetList[-1]) == 0 else 0)
        else:
            self.availableList.append(self.init)

    def _stoplossForwardExit(self):
        """
        負指損點 -> 出場點 --不動作
        statusList = (-2, 0)
        """
        self.AlongEntry.append(0)
        self.AshortEntry.append(0)
        self.AlongExit.append(0)
        self.AshortExit.append(0)
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        self.A_positionList.append(self.A_positionList[-1] if len(self.A_positionList)>0 else 0)
        self.B_positionList.append(self.B_positionList[-1] if len(self.B_positionList)>0 else 0)
        self.A_assetList.append(abs(self.A_positionList[-1]) * (self.A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - self.A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0)
        self.B_assetList.append(abs(self.B_positionList[-1]) * (self.B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - self.B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0)
        self.totalAssetList.append( (self.A_assetList[-1] + self.B_assetList[-1]) if (self.A_assetList[-1] + self.B_assetList[-1]) != 0 else 0)
        if self.availableList:
            self.availableList.append(self.availableList[-1] if (self.A_assetList[-1] + self.B_assetList[-1]) == 0 else 0)
        else:
            self.availableList.append(self.init)

    def _stoplossForward(self):
        """
        負指損點 -> 正指損點 --不動作
        statusList = (-2, 2)
        """
        self.AlongEntry.append(0)
        self.AshortEntry.append(0)
        self.AlongExit.append(0)
        self.AshortExit.append(0)
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        self.A_positionList.append(self.A_positionList[-1] if len(self.A_positionList)>0 else 0)
        self.B_positionList.append(self.B_positionList[-1] if len(self.B_positionList)>0 else 0)
        self.A_assetList.append(abs(self.A_positionList[-1]) * (self.A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - self.A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0)
        self.B_assetList.append(abs(self.B_positionList[-1]) * (self.B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - self.B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0)
        self.totalAssetList.append( (self.A_assetList[-1] + self.B_assetList[-1]) if (self.A_assetList[-1] + self.B_assetList[-1]) != 0 else 0)
        if self.availableList:
            self.availableList.append(self.availableList[-1] if (self.A_assetList[-1] + self.B_assetList[-1]) == 0 else 0)
        else:
            self.availableList.append(self.init)

    def _stoplossBackward(self):
        """
        正指損點 -> 負指損點 --不動作
        statusList = (2, -2)
        """
        self.AlongEntry.append(0)
        self.AshortEntry.append(0)
        self.AlongExit.append(0)
        self.AshortExit.append(0)
        self.A_PriceList.append(self.A_Price)
        self.B_PriceList.append(self.B_Price)
        self.A_positionList.append(self.A_positionList[-1] if len(self.A_positionList)>0 else 0)
        self.B_positionList.append(self.B_positionList[-1] if len(self.B_positionList)>0 else 0)
        self.A_assetList.append(abs(self.A_positionList[-1]) * (self.A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - self.A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0)
        self.B_assetList.append(abs(self.B_positionList[-1]) * (self.B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - self.B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0)
        self.totalAssetList.append( (self.A_assetList[-1] + self.B_assetList[-1]) if (self.A_assetList[-1] + self.B_assetList[-1]) != 0 else 0)
        if self.availableList:
            self.availableList.append(self.availableList[-1] if (self.A_assetList[-1] + self.B_assetList[-1]) == 0 else 0)
        else:
            self.availableList.append(self.init)