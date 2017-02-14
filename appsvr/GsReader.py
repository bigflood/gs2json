# -*- coding: utf-8 -*-

import json

def toJson(v, pretty=False):
    if pretty:
        return json.dumps(v, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        return json.dumps(v)

def isfloat(s):
    if '.' not in s: return s.isdigit()
    return ''.join(s.split('.')).isdigit()

def asTypedValue(s):
    s = s.strip()
    #if s.isdigit(): return int(s)
    #if isfloat(s): return float(s)
    return s


class GsReader:
    def __init__(self, doc):
        self.curSheetName = None
        self.doc = doc
        self.json = {}
        self.transposed = False
        self._numRows = 0
        self._numCols = 0

    @property
    def numRows(self):
        if self.transposed:
            return self._numCols
        else:
            return self._numRows

    @property
    def numCols(self):
        if self.transposed:
            return self._numRows
        else:
            return self._numCols

    def translate(self, v):
        return v

    def enumWithFunc(self, findFunc, foreachFunc, arg1):
        baseRow = -1
        while True:
            r = self.findCellWithFunc(findFunc, startRow=baseRow+1)
            if not r: break
            foreachFunc(arg1, r)
            (baseRow, _, _) = r

    def getSheetAt(self, i):
        return self.doc.get_worksheet(i)

    def loadSheetAt(self, i):
        return self.loadSheetOf(self.getSheetAt(i))

    def loadSheet(self, name):
        if self.curSheetName == name: return
        return self.loadSheetOf(self.findSheet(name))

    def loadSheetOf(self, sheet):
        if not sheet: return
        self.curSheetName = sheet.title
        self.sheet = sheet
        #self.values = [map(asTypedValue, s) for s in self.sheet.get_all_values()]
        self.values = self.sheet.get_all_values()
        self._numRows = len(self.values)
        if self._numRows > 0:
            self._numCols = len(self.values[0])
        else:
            self._numCols = 0

    def mapValues(self, mapFunc):
        for row in self.values:
            for i, v in enumerate(row):
                row[i] = mapFunc(v)

    def findSheet(self, name):
        name = name.lower().strip()
        for s in self.doc.worksheets():
            if name == s.title.split('(')[0].strip().lower():
                return s

    def valueAt(self, row, col):
        if self.transposed:
            row, col = col, row

        if row < 0 or row >= self._numRows: return ""
        r = self.values[row]
        if col < 0 or col >= len(r): return ""
        return r[col]

    def findCellWithValue(self, v, startRow=0, startCol=0):
        v = v.strip().lower()
        for row in range(startRow, self.numRows):
            for col in range(startCol, self.numCols):
                w = self.valueAt(row, col)
                if v == w.strip().lower(): return (row, col)
            startCol = 0

    def findCellWithFunc(self, pr, startRow=0, startCol=0):
        for row in range(startRow, self.numRows):
            for col in range(startCol, self.numCols):
                v = self.valueAt(row, col)
                r = pr(v)
                if r: return (row, col, r)
            startCol = 0

    def findNonEmptyCol(self, row, col):
        while col < self.numCols:
            v = self.valueAt(row, col)
            if v: return col
            col += 1

        return None

    def readCellsV(self, row, col):
        l = []
        while row < self.numRows:
            v = self.valueAt(row, col)
            if not v: break
            l.append((v, row))

            row += 1

        return l

    def readCellsH(self, row, col):
        l = []
        while col < self.numCols:
            v = self.valueAt(row, col)
            if not v: break
            l.append((v, col))

            col += 1

        return l

    def readCellsV2(self, row, col):
        l = []
        while row < self.numRows:
            v1 = self.valueAt(row, col)
            v2 = self.valueAt(row, col+1)
            if not v1 and not v2: break
            l.append((v1, v2, row))

            row += 1

        return l

    def readValuesH(self, row, col):
        l = []
        while col < self.numCols:
            v = self.valueAt(row, col)
            if not v: break
            l.append(v)

            col += 1

        return l

    def readCellsHWithNames(self, names, col, mapFunc):
        l = []
        while True:
            info = {}
            valCount = 0
            for name, row in names:
                name = self.translate(name)
                v = mapFunc( self.valueAt(row, col) )
                if v: valCount += 1
                info[name] = v

            if not valCount: break
            l.append((info, col))
            col += 1

        return l
