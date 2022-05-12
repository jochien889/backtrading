class pairTradeAction():
    def __init__(self, init, actionType):
        """_summary_

        Args:
            init (float): initial amount
            actionType (string): amount unit.
        ! 需紀錄
        價格(X2)
        可用資金(X1)
        進場部位(X2)
        為實現損益(X2)
        """
        self.A_PriceList = []
        self.B_PriceList = []
        self.A_positionList = []
        self.B_positionList = []
        # ! 投入資產變化
        self.A_assetList = [] 
        self.B_assetList = []
        self.totalAssetList = []
        # ! 初期未投入資產變化
        self.availableList = []
        # ! 過去進場價格
        self.A_EntryPrice = 0
        self.B_EntryPrice = 0
        self.init = init
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
    def runAction(self, strategyKey, A_Price, B_Price, A_Side, B_side):
        """
        Args:
            strategyKey (tuple): pair status code.
        """
        ### self.B_positionList[-1] if len(self.B_positionList)>0 else 0
        if strategyKey not in self.strategy:
            self.A_PriceList.append(A_Price)
            self.B_PriceList.append(B_Price)
            self.A_positionList.append(self.A_positionList[-1] if len(self.A_positionList)>0 else 0)
            self.B_positionList.append(self.B_positionList[-1] if len(self.B_positionList)>0 else 0)
            self.A_assetList.append(abs(self.A_positionList[-1]) * (A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0)
            self.B_assetList.append(abs(self.B_positionList[-1]) * (B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0)
            self.totalAssetList.append( (self.A_assetList[-1] + self.B_assetList[-1]) if (self.A_assetList[-1] + self.B_assetList[-1]) != 0 else 0)
            if self.availableList:
                self.availableList.append(self.availableList[-1] if (self.A_assetList[-1] + self.B_assetList[-1]) == 0 else 0)
            else:
                self.availableList.append(self.init)
        else:
            self.strategy[strategyKey](A_Price, B_Price, A_Side, B_side)
        
    def _stoplossBackwardEntry2(self, A_Price, B_Price, A_Side, B_side):
        """
        statusList = (2, -1)
        long B 
        short A  
        """
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        if self.actionType == 'amount':
            A_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            B_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset)
            self.A_positionList.append(A_asset * A_Side/A_Price)
            self.B_positionList.append(B_asset * B_side/B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        elif self.actionType == 'unit':
            A_position = self.availableList[-1]/(1+abs(B_side)) * A_Side if len(self.availableList) else self.init/(1+abs(B_side)) * A_Side
            B_position = A_position * B_side
            self.A_assetList.append(A_position * A_Price)
            self.B_assetList.append(B_position * B_Price) 
            self.A_positionList.append(A_position * A_Side)
            self.B_positionList.append(B_position * B_side)
            self.totalAssetList.append(self.A_assetList[-1] + self.B_assetList[-1])
            self.availableList.append(0)
        self.A_EntryPrice = A_Price
        self.B_EntryPrice = B_Price
        
    def _stoplossForwardEntry2(self, A_Price, B_Price, A_Side, B_side):
        """
        statusList = (-2, 1)
        long A 
        short B    
        """
        ### 出場
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        if self.actionType == 'amount':
            A_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            B_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset)
            self.A_positionList.append(A_asset * A_Side/A_Price)
            self.B_positionList.append(B_asset * B_side/B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        elif self.actionType == 'unit':
            A_position = self.availableList[-1]/(1+abs(B_side)) * A_Side if len(self.availableList) else self.init/(1+abs(B_side)) * A_Side
            B_position = A_position * B_side
            self.A_assetList.append(A_position * A_Price)
            self.B_assetList.append(B_position * B_Price) 
            self.A_positionList.append(A_position * A_Side)
            self.B_positionList.append(B_position * B_side)
            self.totalAssetList.append(self.A_assetList[-1] + self.B_assetList[-1])
            self.availableList.append(0)
        self.A_EntryPrice = A_Price
        self.B_EntryPrice = B_Price

    def _stoplossBackwardEntry(self, A_Price, B_Price, A_Side, B_side):
        """
        statusList = (2,1)
        long A 
        short B    
        """
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        if self.actionType == 'amount':
            A_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            B_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset)
            self.A_positionList.append(A_asset * A_Side/A_Price)
            self.B_positionList.append(B_asset * B_side/B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        elif self.actionType == 'unit':
            A_position = self.availableList[-1]/(1+abs(B_side)) * A_Side if len(self.availableList) else self.init/(1+abs(B_side)) * A_Side
            B_position = A_position * B_side
            self.A_assetList.append(A_position * A_Price)
            self.B_assetList.append(B_position * B_Price) 
            self.A_positionList.append(A_position * A_Side)
            self.B_positionList.append(B_position * B_side)
            self.totalAssetList.append(self.A_assetList[-1] + self.B_assetList[-1])
            self.availableList.append(0)
        self.A_EntryPrice = A_Price
        self.B_EntryPrice = B_Price

    def _stoplossForwardEntry(self, A_Price, B_Price, A_Side, B_side):
        """
        statusList = (-2,-1)
        long B 
        short A    
        """
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        if self.actionType == 'amount':
            A_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            B_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset)
            self.A_positionList.append(A_asset * A_Side/A_Price)
            self.B_positionList.append(B_asset * B_side/B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        elif self.actionType == 'unit':
            A_position = self.availableList[-1]/(1+abs(B_side)) * A_Side if len(self.availableList) else self.init/(1+abs(B_side)) * A_Side
            B_position = A_position * B_side
            self.A_assetList.append(A_position * A_Price)
            self.B_assetList.append(B_position * B_Price) 
            self.A_positionList.append(A_position * A_Side)
            self.B_positionList.append(B_position * B_side)
            self.totalAssetList.append(self.A_assetList[-1] + self.B_assetList[-1])
            self.availableList.append(0)
        self.A_EntryPrice = A_Price
        self.B_EntryPrice = B_Price
        
    def _entryForwardStoploss(self, A_Price, B_Price, A_Side, B_side):
        """
        statusList = (1, 2)
        long A 
        short B
        close the position
        """
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        ## 可用資金
        A_available = abs(self.A_positionList[-1]) * (A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0
        B_available = abs(self.B_positionList[-1]) * (B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0
        self.availableList.append(A_available + B_available)
        ## 部位資產
        self.A_assetList.append(0)
        self.B_assetList.append(0)
        self.totalAssetList.append(0)
        self.A_positionList.append(0)
        self.B_positionList.append(0)

    def _entryBackwardStoploss2(self, A_Price, B_Price, A_Side, B_side):
        """
        statusList = (1, -2)
        long A 
        short B
        close the position
        """
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        ## 可用資金
        A_available = abs(self.A_positionList[-1]) * (A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0
        B_available = abs(self.B_positionList[-1]) * (B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0
        self.availableList.append(A_available + B_available)
        ## 部位資產
        self.A_assetList.append(0)
        self.B_assetList.append(0)
        self.totalAssetList.append(0)
        self.A_positionList.append(0)
        self.B_positionList.append(0)
        
    def _entryBackwardStoploss(self, A_Price, B_Price, A_Side, B_side):
        """
        statusList = (-1,-2)
        long B 
        short A
        close the position  
        """
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        ## 可用資金
        A_available = abs(self.A_positionList[-1]) * (A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0
        B_available = abs(self.B_positionList[-1]) * (B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0
        self.availableList.append(A_available + B_available)
        ## 部位資產
        self.A_assetList.append(0)
        self.B_assetList.append(0)
        self.totalAssetList.append(0)
        self.A_positionList.append(0)
        self.B_positionList.append(0)
        
    def _entryForwardStoploss2(self, A_Price, B_Price, A_Side, B_side):
        """
        statusList = (-1,2)
        long B 
        short A
        close the position  
        """
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        ## 可用資金
        A_available = abs(self.A_positionList[-1]) * (A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0
        B_available = abs(self.B_positionList[-1]) * (B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0
        self.availableList.append(A_available + B_available)
        ## 部位資產
        self.A_assetList.append(0)
        self.B_assetList.append(0)
        self.totalAssetList.append(0)
        self.A_positionList.append(0)
        self.B_positionList.append(0)

    def _forwardEntry(self, A_Price, B_Price, A_Side, B_side):
        """
        statusList = (0,1)
        """
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        if self.actionType == 'amount':
            A_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            B_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset)
            self.A_positionList.append(A_asset * A_Side/A_Price)
            self.B_positionList.append(B_asset * B_side/B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        elif self.actionType == 'unit':
            A_position = self.availableList[-1]/(1+abs(B_side)) * A_Side if len(self.availableList) else self.init/(1+abs(B_side)) * A_Side
            B_position = A_position * B_side
            self.A_assetList.append(A_position * A_Price)
            self.B_assetList.append(B_position * B_Price) 
            self.A_positionList.append(A_position * A_Side)
            self.B_positionList.append(B_position * B_side)
            self.totalAssetList.append(self.A_assetList[-1] + self.B_assetList[-1])
            self.availableList.append(0)
        self.A_EntryPrice = A_Price
        self.B_EntryPrice = B_Price
            
    def _backwardEntry(self, A_Price, B_Price, A_Side, B_side):
        """
        statusList = (0,-1)
        A:long
        B:short
        """
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        if self.actionType == 'amount':
            A_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            B_asset = self.availableList[-1]/2 if len(self.availableList) else self.init/2
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset)
            self.A_positionList.append(A_asset * A_Side/A_Price)
            self.B_positionList.append(B_asset * B_side/B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        elif self.actionType == 'unit':
            A_position = self.availableList[-1]/(1+abs(B_side)) * A_Side if len(self.availableList) else self.init/(1+abs(B_side)) * A_Side
            B_position = A_position * B_side
            self.A_assetList.append(A_position * A_Price)
            self.B_assetList.append(B_position * B_Price) 
            self.A_positionList.append(A_position * A_Side)
            self.B_positionList.append(B_position * B_side)
            self.totalAssetList.append(self.A_assetList[-1] + self.B_assetList[-1])
            self.availableList.append(0)
        self.A_EntryPrice = A_Price
        self.B_EntryPrice = B_Price

    def _backwardExit(self, A_Price, B_Price, A_Side, B_side):
        """
        statusList = (1,0)
        long A
        short B
        close the position
        """

        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        ## 可用資金
        A_available = abs(self.A_positionList[-1]) * (A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0
        B_available = abs(self.B_positionList[-1]) * (B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0
        self.availableList.append(A_available + B_available)
        ## 部位資產
        self.A_assetList.append(0)
        self.B_assetList.append(0)
        self.totalAssetList.append(0)
        self.A_positionList.append(0)
        self.B_positionList.append(0)

        
    def _exitBackwardEntry(self, A_Price, B_Price, A_Side, B_side):
        """
        statusList = (1,-1)
        long A
        short B
        close the position
        long B 
        short A
        """
        ### 出場
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        ## 可用資金
        A_available = abs(self.A_positionList[-1]) * (A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0
        B_available = abs(self.B_positionList[-1]) * (B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0
        available = A_available +B_available
        
        ### 進場
        if self.actionType == 'amount':
            A_asset = available/2
            B_asset = available/2
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset)
            self.A_positionList.append(A_asset * A_Side/A_Price)
            self.B_positionList.append(B_asset * B_side/B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        elif self.actionType == 'unit':
            A_position = self.availableList[-1]/(1+abs(B_side)) * A_Side
            B_position = A_position * B_side
            self.A_assetList.append(A_position * A_Price)
            self.B_assetList.append(B_position * B_Price) 
            self.A_positionList.append(A_position * A_Side)
            self.B_positionList.append(B_position * B_side)
            self.totalAssetList.append(self.A_assetList[-1] + self.B_assetList[-1])
            self.availableList.append(0)
        self.A_EntryPrice = A_Price
        self.B_EntryPrice = B_Price
        
    def _forwardExit(self, A_Price, B_Price, A_Side, B_side):
        """
        statusList = (-1,0)
        long B
        short A
        close the position
        """
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        ## 可用資金
        A_available = abs(self.A_positionList[-1]) * (A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0
        B_available = abs(self.B_positionList[-1]) * (B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0
        self.availableList.append(A_available + B_available)
        ## 部位資產
        self.A_assetList.append(0)
        self.B_assetList.append(0)
        self.totalAssetList.append(0)
        self.A_positionList.append(0)
        self.B_positionList.append(0)
        
    def _exitForwardEntry(self, A_Price, B_Price, A_Side, B_side):
        """
        statusList = (-1,1)
        long B
        short A
        close the position
        long A
        short B
        """
        ### 出場
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        ## 可用資金
        A_available = abs(self.A_positionList[-1]) * (A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0
        B_available = abs(self.B_positionList[-1]) * (B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0
        available = A_available +B_available
        
        ### 進場
        if self.actionType == 'amount':
            A_asset = available/2
            B_asset = available/2
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset)
            self.A_positionList.append(A_asset * A_Side/A_Price)
            self.B_positionList.append(B_asset * B_side/B_Price)
            self.totalAssetList.append(A_asset + B_asset)
            self.availableList.append(0)
        elif self.actionType == 'unit':
            A_position = self.availableList[-1]/(1+abs(B_side)) * A_Side
            B_position = A_position * B_side
            self.A_assetList.append(A_position * A_Price)
            self.B_assetList.append(B_position * B_Price) 
            self.A_positionList.append(A_position * A_Side)
            self.B_positionList.append(B_position * B_side)
            self.totalAssetList.append(self.A_assetList[-1] + self.B_assetList[-1])
            self.availableList.append(0)
        self.A_EntryPrice = A_Price
        self.B_EntryPrice = B_Price
        
    def _exitForwardStoploss(self, A_Price, B_Price, A_Side, B_side):
        """
        出場點 -> 正指損點 --不動作
        statusList = (0,2)
        """
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        self.A_positionList.append(self.A_positionList[-1] if len(self.A_positionList)>0 else 0)
        self.B_positionList.append(self.B_positionList[-1] if len(self.B_positionList)>0 else 0)
        self.A_assetList.append(abs(self.A_positionList[-1]) * (A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0)
        self.B_assetList.append(abs(self.B_positionList[-1]) * (B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0)
        self.totalAssetList.append( (self.A_assetList[-1] + self.B_assetList[-1]) if (self.A_assetList[-1] + self.B_assetList[-1]) != 0 else 0)
        if self.availableList:
            self.availableList.append(self.availableList[-1] if (self.A_assetList[-1] + self.B_assetList[-1]) == 0 else 0)
        else:
            self.availableList.append(self.init)

    def _exitBackwardStoploss(self, A_Price, B_Price, A_Side, B_side):
        """
        出場點 -> 負指損點 --不動作
        statusList = (0,-2)
        """
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        self.A_positionList.append(self.A_positionList[-1] if len(self.A_positionList)>0 else 0)
        self.B_positionList.append(self.B_positionList[-1] if len(self.B_positionList)>0 else 0)
        self.A_assetList.append(abs(self.A_positionList[-1]) * (A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0)
        self.B_assetList.append(abs(self.B_positionList[-1]) * (B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0)
        self.totalAssetList.append( (self.A_assetList[-1] + self.B_assetList[-1]) if (self.A_assetList[-1] + self.B_assetList[-1]) != 0 else 0)
        if self.availableList:
            self.availableList.append(self.availableList[-1] if (self.A_assetList[-1] + self.B_assetList[-1]) == 0 else 0)
        else:
            self.availableList.append(self.init)
            
    def _stoplossBackwardExit(self, A_Price, B_Price, A_Side, B_side):
        """
        正指損點 -> 出場點 --不動作
        statusList = (2, 0)
        """
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        self.A_positionList.append(self.A_positionList[-1] if len(self.A_positionList)>0 else 0)
        self.B_positionList.append(self.B_positionList[-1] if len(self.B_positionList)>0 else 0)
        self.A_assetList.append(abs(self.A_positionList[-1]) * (A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0)
        self.B_assetList.append(abs(self.B_positionList[-1]) * (B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0)
        self.totalAssetList.append( (self.A_assetList[-1] + self.B_assetList[-1]) if (self.A_assetList[-1] + self.B_assetList[-1]) != 0 else 0)
        if self.availableList:
            self.availableList.append(self.availableList[-1] if (self.A_assetList[-1] + self.B_assetList[-1]) == 0 else 0)
        else:
            self.availableList.append(self.init)

    def _stoplossForwardExit(self, A_Price, B_Price, A_Side, B_side):
        """
        負指損點 -> 出場點 --不動作
        statusList = (-2, 0)
        """
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        self.A_positionList.append(self.A_positionList[-1] if len(self.A_positionList)>0 else 0)
        self.B_positionList.append(self.B_positionList[-1] if len(self.B_positionList)>0 else 0)
        self.A_assetList.append(abs(self.A_positionList[-1]) * (A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0)
        self.B_assetList.append(abs(self.B_positionList[-1]) * (B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0)
        self.totalAssetList.append( (self.A_assetList[-1] + self.B_assetList[-1]) if (self.A_assetList[-1] + self.B_assetList[-1]) != 0 else 0)
        if self.availableList:
            self.availableList.append(self.availableList[-1] if (self.A_assetList[-1] + self.B_assetList[-1]) == 0 else 0)
        else:
            self.availableList.append(self.init)

    def _stoplossForward(self, A_Price, B_Price, A_Side, B_side):
        """
        負指損點 -> 正指損點 --不動作
        statusList = (-2, 2)
        """
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        self.A_positionList.append(self.A_positionList[-1] if len(self.A_positionList)>0 else 0)
        self.B_positionList.append(self.B_positionList[-1] if len(self.B_positionList)>0 else 0)
        self.A_assetList.append(abs(self.A_positionList[-1]) * (A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0)
        self.B_assetList.append(abs(self.B_positionList[-1]) * (B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0)
        self.totalAssetList.append( (self.A_assetList[-1] + self.B_assetList[-1]) if (self.A_assetList[-1] + self.B_assetList[-1]) != 0 else 0)
        if self.availableList:
            self.availableList.append(self.availableList[-1] if (self.A_assetList[-1] + self.B_assetList[-1]) == 0 else 0)
        else:
            self.availableList.append(self.init)

    def _stoplossBackward(self, A_Price, B_Price, A_Side, B_side):
        """
        正指損點 -> 負指損點 --不動作
        statusList = (2, -2)
        """
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        self.A_positionList.append(self.A_positionList[-1] if len(self.A_positionList)>0 else 0)
        self.B_positionList.append(self.B_positionList[-1] if len(self.B_positionList)>0 else 0)
        self.A_assetList.append(abs(self.A_positionList[-1]) * (A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else abs(self.A_positionList[-1]) * (self.A_EntryPrice - A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0)
        self.B_assetList.append(abs(self.B_positionList[-1]) * (B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else abs(self.B_positionList[-1]) * (self.B_EntryPrice - B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0)
        self.totalAssetList.append( (self.A_assetList[-1] + self.B_assetList[-1]) if (self.A_assetList[-1] + self.B_assetList[-1]) != 0 else 0)
        if self.availableList:
            self.availableList.append(self.availableList[-1] if (self.A_assetList[-1] + self.B_assetList[-1]) == 0 else 0)
        else:
            self.availableList.append(self.init)