# basic imports
import numpy as np
import pandas as pd

# self imports
from .io import *
from .lib import *

class GMap():
    """
    """
    def __init__(self):
        """
        ----------
        Parameters
        ----------
        """
        
        # map file
        self.pdMap = None
        self.isMap = False
        self.countNames = 0

        # dimension
        self.nCol = 0
        self.nRow = 0
        self.pxImgH = 0
        self.pxImgW = 0

        # rows/columns
        self.lsPxCol = []
        self.lsPxRow = []
        self.lsRatioCol = []
        self.lsRatioRow = []
        self.lsRatioColReset = []
        self.lsRatioRowReset = []

    def load(self, pathMap):
        """
        ----------
        Parameters
        ----------
        """

        self.pdMap = loadMap(pathMap)

        if self.pdMap is not None:
            self.nRow = self.pdMap.shape[0]
            self.nCol = self.pdMap.shape[1]
            self.isMap = True

    def findPlots(self, GImg, nRow=0, nCol=0, nSmooth=100):
        """
        ----------
        Parameters
        ----------
        """

        # get image info
        self.pxImgH, self.pxImgW = GImg.getShape()
        isDimAssigned = (nRow != 0 and nCol != 0)
        
        # if dim is assigned regardless have map or not, force changning nR and nC 
        if isDimAssigned:
            self.nRow, self.nCol = nRow, nCol

        # search for peaks
        self.lsPxRow, _ = findPeaks(
            GImg.get("binSeg"), nPeaks=self.nRow, axis=0, nSmooth=nSmooth)
        self.lsPxCol, _ = findPeaks(
            GImg.get("binSeg"), nPeaks=self.nCol, axis=1, nSmooth=nSmooth)

         # if neither assigned, update dim. from the peak searching algo.
        if (not isDimAssigned) and (not self.isMap):
            self.nRow = len(self.lsPxRow)
            self.nCol = len(self.lsPxCol)
        
        # udpate map with finalized dim. and names
        self.updateMapNames()

        # rescale them to [0, 1] for GUI
        self.lsRatioCol = scaleTo0and1(self.lsPxCol, self.pxImgW)
        self.lsRatioRow = scaleTo0and1(self.lsPxRow, self.pxImgH)
        self.lsRatioColReset = self.lsRatioCol.copy()
        self.lsRatioRowReset = self.lsRatioRow.copy()

    def updateMapNames(self):
        """
        ----------
        Parameters
        ----------
        """
        mapTemp = pd.DataFrame(np.zeros((self.nRow, self.nCol)))
        ctUnknown = 0
        for row in range(self.nRow):
            for col in range(self.nCol):
                try:
                    mapTemp.iloc[row, col] = self.pdMap[row, col]
                except:
                    mapTemp.iloc[row, col] = "unknown_%d" % (ctUnknown)
                    ctUnknown += 1
        # update map
        self.pdMap = mapTemp

    def getName(self, row, col):
        """
        ----------
        Parameters
        ----------
        """
        return self.pdMap.iloc[row, col]

    def getRatio(self):
        """
        GUI SPCIFIC
        """

        return self.lsRatioCol, self.lsRatioRow

    def delRatio(self, dim, index):
        """
        GUI SPCIFIC
        """

        if dim == 0:
            np.delete(self.lsRatioRow, index)
        elif dim == 1:
            np.delete(self.lsRatioCol, index)

        self.updateAnchors()

    def addRatio(self, dim, value):
        """
        GUI SPCIFIC
        """

        if dim == 0:
            np.append(self.lsRatioRow, value)
        elif dim == 1:
            np.append(self.lsRatioCol, value)

        self.updateAnchors()

    def modRatio(self, dim, index, value):
        """
        GUI SPCIFIC
        """

        if dim == 0:
            self.lsRatioRow[index] = value
        elif dim == 1:
            self.lsRatioCol[index] = value

        self.updateAnchors()

    def resetRatio(self):
        """
        GUI SPCIFIC
        """

        self.lsRatioRow = self.lsRatioRowReset.copy()
        self.lsRatioCol = self.lsRatioColReset.copy()

        self.updateAnchors()
    
    def updateAnchors(self):
        """
        GUI SPCIFIC
        """

        self.lsRatioCol = np.sort(self.lsRatioCol)
        self.lsRatioRow = np.sort(self.lsRatioRow)
        self.lsPxRow = scaleToOrg(self.lsRatioRow, self.pxImgH)
        self.lsPxCol = scaleToOrg(self.lsRatioCol, self.pxImgW)


def scaleTo0and1(array, length):
    array = np.array(array)
    return array/length


def scaleToOrg(array, length):
    array = np.array(array)
    return array*length
