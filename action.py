class pairTradeAction():
    def __init__(self, init, actionType):
        """_summary_

        Args:
            init (float): initial amount
            actionType (string): amount unit.
        """
        self.A_PriceList = []
        self.B_PriceList = []
        self.A_positionList = [0]
        self.B_positionList = [0]
        # ! 投入資產變化
        self.A_assetList = [0] 
        self.B_assetList = [0]
        # ! 初期未投入資產變化
        self.totalAsset = [init]
        self.availableList = [0]
        # ! 過去進場價格
        self.A_EntryPrice = 0
        self.B_EntryPrice = 0
        
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
        if strategyKey not in self.strategy:
            self.A_PriceList.append(A_Price)
            self.B_PriceList.append(B_Price)
            self.A_assetList.append(self.A_positionList[-1] * (A_Price - self.A_EntryPrice + self.A_EntryPrice) if self.A_positionList[-1] > 0 else self.A_positionList[-1] * (self.A_EntryPrice - A_Price + self.A_EntryPrice) if self.A_positionList[-1] < 0 else 0)
            self.B_assetList.append(self.B_positionList[-1] * (B_Price - self.B_EntryPrice + self.B_EntryPrice) if self.B_positionList[-1] > 0 else self.B_positionList[-1] * (self.B_EntryPrice - B_Price + self.B_EntryPrice) if self.B_positionList[-1] < 0 else 0)
            self.totalAsset.append( (self.A_assetList[-1] + self.B_assetList[-1]) if (self.A_assetList[-1] + self.B_assetList[-1]) != 0 else 0)
            self.availableList.append(self.availableList[-1] if (self.A_assetList[-1] + self.B_assetList[-1]) == 0 else 0)
            self.A_positionList.append(self.A_positionList[-1])
            self.B_positionList.append(self.B_positionList[-1])
        else:
            self.strategy[strategyKey](A_Price, B_Price, A_Side, B_side)
        
    def _stoplossBackwardEntry2(self, ANewPrice, BNewPrice, aPos, bPos):
        """
        statusList = (2, -1)
        long B 
        short A  
        """
        entryDate.append(index)
        aTotal, bTotal = init/2, init/2
        init -=(aTotal + bTotal) 
        AEntryPrice.append(ANewPrice)
        BEntryPrice.append(BNewPrice)
        AEntryPosition.append(aTotal/ANewPrice)
        BEntryPosition.append(-bTotal/BNewPrice)
        AEntry.append(aTotal)
        BEntry.append(bTotal)
        totalEntry.append(aTotal + bTotal)
        
    def _stoplossForwardEntry2(self, ANewPrice, BNewPrice, aPos, bPos):
        """
        statusList = (-2, 1)
        long A 
        short B    
        """
        entryDate.append(index)
        aTotal, bTotal = init/2, init/2
        AEntryPrice.append(ANewPrice)
        BEntryPrice.append(BNewPrice)
        AEntryPosition.append(-aTotal/ANewPrice)
        BEntryPosition.append(bTotal/BNewPrice)
        AEntry.append(aTotal)
        BEntry.append(bTotal)
        totalEntry.append(aTotal + bTotal)
        init -=(aTotal + bTotal) 

    def _stoplossBackwardEntry(self, ANewPrice, BNewPrice, aPos, bPos):
        """
        statusList = (2,1)
        long A 
        short B    
        """
        entryDate.append(index)
        aTotal, bTotal = init/2, init/2
        AEntryPrice.append(ANewPrice)
        BEntryPrice.append(BNewPrice)
        AEntryPosition.append(-aTotal/ANewPrice)
        BEntryPosition.append(bTotal/BNewPrice)
        AEntry.append(aTotal)
        BEntry.append(bTotal)
        totalEntry.append(aTotal + bTotal)
        init -=(aTotal + bTotal) 

    def _stoplossForwardEntry(self, ANewPrice, BNewPrice, aPos, bPos):
        """
        statusList = (-2,-1)
        long B 
        short A    
        """
        entryDate.append(index)
        aTotal, bTotal = init/2, init/2
        init -=(aTotal + bTotal) 
        AEntryPrice.append(ANewPrice)
        BEntryPrice.append(BNewPrice)
        AEntryPosition.append(aTotal/ANewPrice)
        BEntryPosition.append(-bTotal/BNewPrice)
        AEntry.append(aTotal)
        BEntry.append(bTotal)
        totalEntry.append(aTotal + bTotal)
        
    def _entryForwardStoploss(self, ANewPrice, BNewPrice, aPos, bPos):
        """
        statusList = (1, 2)
        long A 
        short B
        close the position
        """
        exitDate.append(index)
        AExitPrice.append(ANewPrice)
        BExitPrice.append(BNewPrice)
        AExitPosition.append(AEntryPosition[-1])
        BExitPosition.append(BEntryPosition[-1])
        AExit.append(AEntryPosition[-1] * (ANewPrice - AEntryPrice[-1] + AEntryPrice[-1]))
        BExit.append(BEntryPosition[-1] * (BEntryPrice[-1] - BNewPrice + BEntryPrice[-1]))
        init = AEntryPosition[-1] * (ANewPrice - AEntryPrice[-1] + AEntryPrice[-1]) + BEntryPosition[-1] * (BEntryPrice[-1] - BNewPrice + BEntryPrice[-1])
        totalExit.append(init) 

    def _entryBackwardStoploss2(self, ANewPrice, BNewPrice, aPos, bPos):
        """
        statusList = (1, -2)
        long A 
        short B
        close the position
        """
        exitDate.append(index)
        AExitPrice.append(ANewPrice)
        BExitPrice.append(BNewPrice)
        AExitPosition.append(AEntryPosition[-1])
        BExitPosition.append(BEntryPosition[-1])
        AExit.append(AEntryPosition[-1] * (ANewPrice - AEntryPrice[-1] + AEntryPrice[-1]))
        BExit.append(BEntryPosition[-1] * (BEntryPrice[-1] - BNewPrice + BEntryPrice[-1]))
        init = AEntryPosition[-1] * (ANewPrice - AEntryPrice[-1] + AEntryPrice[-1]) + BEntryPosition[-1] * (BEntryPrice[-1] - BNewPrice + BEntryPrice[-1])
        totalExit.append(init)
        
    def _entryBackwardStoploss(self, ANewPrice, BNewPrice, aPos, bPos):
        """
        statusList = (-1,-2)
        long B 
        short A
        close the position  
        """
        exitDate.append(index)
        AExitPrice.append(ANewPrice)
        BExitPrice.append(BNewPrice)
        AExitPosition.append(AEntryPosition[-1])
        BExitPosition.append(BEntryPosition[-1])
        AExit.append(AEntryPosition[-1] * (AEntryPrice[-1] - ANewPrice + AEntryPrice[-1]))
        BExit.append(BEntryPosition[-1] * (BNewPrice - BEntryPrice[-1] + BEntryPrice[-1]))
        init = AEntryPosition[-1] * (AEntryPrice[-1] - ANewPrice + AEntryPrice[-1]) + BEntryPosition[-1] * (BNewPrice - BEntryPrice[-1] + BEntryPrice[-1])
        totalExit.append(init)
        
    def _entryForwardStoploss2(self, ANewPrice, BNewPrice, aPos, bPos):
        """
        statusList = (-1,2)
        long B 
        short A
        close the position  
        """
        exitDate.append(index)
        AExitPrice.append(ANewPrice)
        BExitPrice.append(BNewPrice)
        AExitPosition.append(AEntryPosition[-1])
        BExitPosition.append(BEntryPosition[-1])
        AExit.append(AEntryPosition[-1] * (AEntryPrice[-1] - ANewPrice + AEntryPrice[-1]))
        BExit.append(BEntryPosition[-1] * (BNewPrice - BEntryPrice[-1] + BEntryPrice[-1]))
        init = AEntryPosition[-1] * (AEntryPrice[-1] - ANewPrice + AEntryPrice[-1]) + BEntryPosition[-1] * (BNewPrice - BEntryPrice[-1] + BEntryPrice[-1])
        totalExit.append(init)

    def _forwardEntry(self, A_Price, B_Price, A_Side, B_side):
        """
        statusList = (0,1)
        """
        self.A_PriceList.append(A_Price)
        self.B_PriceList.append(B_Price)
        if self.actionType == 'amount':
            A_asset = self.availableList[-1]/2
            B_asset = self.availableList[-1]/2
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset)
            self.A_positionList.append(A_asset * A_Side/A_Price)
            self.B_positionList.append(B_asset * B_side/B_Price)
            self.totalAsset.append(A_asset + B_asset)
            self.availableList.append(0)
        elif self.actionType == 'unit':
            A_position = self.availableList[-1]/(1+abs(B_side)) * A_Side
            B_position = A_position * B_side
            self.A_assetList.append(A_position * A_Price)
            self.B_assetList.append(B_position * B_Price) 
            self.A_positionList.append(A_position * A_Side)
            self.B_positionList.append(B_position * B_side)
            self.totalAsset.append(self.A_assetList[-1] + self.B_assetList[-1])
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
            A_asset = self.availableList[-1]/2
            B_asset = self.availableList[-1]/2
            self.A_assetList.append(A_asset)
            self.B_assetList.append(B_asset)
            self.A_positionList.append(A_asset * A_Side/A_Price)
            self.B_positionList.append(B_asset * B_side/B_Price)
            self.totalAsset.append(A_asset + B_asset)
            self.availableList.append(0)
        elif self.actionType == 'unit':
            A_position = self.availableList[-1]/(1+abs(B_side)) * A_Side
            B_position = A_position * B_side
            self.A_assetList.append(A_position * A_Price)
            self.B_assetList.append(B_position * B_Price) 
            self.A_positionList.append(A_position * A_Side)
            self.B_positionList.append(B_position * B_side)
            self.totalAsset.append(self.A_assetList[-1] + self.B_assetList[-1])
            self.availableList.append(0)

    def _backwardExit(self, ANewPrice, BNewPrice, aPositionRatio, bPositionRatio):
        """
        statusList = (1,0)
        long A
        short B
        close the position
        """

        AExitPrice.append(ANewPrice)
        BExitPrice.append(BNewPrice)
        AExitPosition.append(AEntryPosition[-1])
        BExitPosition.append(BEntryPosition[-1])
        AExit.append(AEntryPosition[-1] * (ANewPrice - AEntryPrice[-1] + AEntryPrice[-1]))
        BExit.append(BEntryPosition[-1] * (BEntryPrice[-1] - BNewPrice + BEntryPrice[-1]))
        init = AEntryPosition[-1] * (ANewPrice - AEntryPrice[-1] + AEntryPrice[-1]) + BEntryPosition[-1] * (BEntryPrice[-1] - BNewPrice + BEntryPrice[-1])
        totalExit.append(init)
        
    def _exitBackwardEntry(self, ANewPrice, BNewPrice, aPositionRatio, bPositionRatio):
        """
        statusList = (1,-1)
        long A
        short B
        close the position
        long B 
        short A
        """
        exitDate.append(index)
        AExitPrice.append(ANewPrice)
        BExitPrice.append(BNewPrice)
        AExitPosition.append(AEntryPosition[-1])
        BExitPosition.append(BEntryPosition[-1])
        AExit.append(AEntryPosition[-1] * (ANewPrice - AEntryPrice[-1] + AEntryPrice[-1]))
        BExit.append(BEntryPosition[-1] * (BEntryPrice[-1] - BNewPrice + BEntryPrice[-1]))
        init = AEntryPosition[-1] * (ANewPrice - AEntryPrice[-1] + AEntryPrice[-1]) + BEntryPosition[-1] * (BEntryPrice[-1] - BNewPrice + BEntryPrice[-1])
        totalExit.append(init) 
        
        entryDate.append(index)
        aTotal, bTotal = init/2, init/2
        init -=(aTotal + bTotal) 
        AEntryPrice.append(ANewPrice)
        BEntryPrice.append(BNewPrice)
        AEntryPosition.append(aTotal/ANewPrice)
        BEntryPosition.append(-bTotal/BNewPrice)
        AEntry.append(aTotal)
        BEntry.append(bTotal)
        totalEntry.append(aTotal + bTotal)
        
    def _forwardExit(self, ANewPrice, BNewPrice, aPositionRatio, bPositionRatio):
        """
        statusList = (-1,0)
        long B
        short A
        close the position
        """
        AExitPrice.append(ANewPrice)
        BExitPrice.append(BNewPrice)
        AExitPosition.append(AEntryPosition[-1])
        BExitPosition.append(BEntryPosition[-1])
        AExit.append(AEntryPosition[-1] * (AEntryPrice[-1] - ANewPrice + AEntryPrice[-1]))
        BExit.append(BEntryPosition[-1] * (BNewPrice - BEntryPrice[-1] + BEntryPrice[-1]))
        init = AEntryPosition[-1] * (AEntryPrice[-1] - ANewPrice + AEntryPrice[-1]) + BEntryPosition[-1] * (BNewPrice - BEntryPrice[-1] + BEntryPrice[-1])
        totalExit.append(init)
        
    def _exitForwardEntry(self, ANewPrice, BNewPrice, aPositionRatio, bPositionRatio):
        """
        statusList = (-1,1)
        long B
        short A
        close the position
        long A
        short B
        """
        AExitPrice.append(ANewPrice)
        BExitPrice.append(BNewPrice)
        AExitPosition.append(AEntryPosition[-1])
        BExitPosition.append(BEntryPosition[-1])
        AExit.append(AEntryPosition[-1] * (AEntryPrice[-1] - ANewPrice + AEntryPrice[-1]))
        BExit.append(BEntryPosition[-1] * (BNewPrice - BEntryPrice[-1] + BEntryPrice[-1]))
        init = AEntryPosition[-1] * (AEntryPrice[-1] - ANewPrice + AEntryPrice[-1]) + BEntryPosition[-1] * (BNewPrice - BEntryPrice[-1] + BEntryPrice[-1])
        totalExit.append(init)
        
        aTotal, bTotal = init/2, init/2
        AEntryPrice.append(ANewPrice)
        BEntryPrice.append(BNewPrice)
        AEntryPosition.append(-aTotal/ANewPrice)
        BEntryPosition.append(bTotal/BNewPrice)
        AEntry.append(aTotal)
        BEntry.append(bTotal)
        totalEntry.append(aTotal + bTotal)
        init -=(aTotal + bTotal) 
        
    def _exitForwardStoploss(self, ANewPrice, BNewPrice, aPos, bPos):
        """
        出場點 -> 正指損點 --不動作
        statusList = (0,2)
        """
        pass

    def _exitBackwardStoploss(self, ANewPrice, BNewPrice, aPos, bPos):
        """
        出場點 -> 負指損點 --不動作
        statusList = (0,-2)
        """
        pass

    def _stoplossBackwardExit(self, ANewPrice, BNewPrice, aPos, bPos):
        """
        正指損點 -> 出場點 --不動作
        statusList = (2, 0)
        """
        pass

    def _stoplossForwardExit(self, ANewPrice, BNewPrice, aPos, bPos):
        """
        負指損點 -> 出場點 --不動作
        statusList = (-2, 0)
        """
        pass

    def _stoplossForward(self, ANewPrice, BNewPrice, aPos, bPos):
        """
        負指損點 -> 正指損點 --不動作
        statusList = (-2, 2)
        """
        pass

    def _stoplossBackward(self, ANewPrice, BNewPrice, aPos, bPos):
        """
        正指損點 -> 負指損點 --不動作
        statusList = (2, -2)
        """
        pass