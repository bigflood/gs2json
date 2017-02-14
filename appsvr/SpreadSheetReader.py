# -*- coding: utf-8 -*-


from GsReader import GsReader


def isfloat(s):
    if '.' not in s: return s.isdigit()
    return ''.join(s.split('.')).isdigit()

def isIgnoreKey(n):
    return n and (type(n) in [str,unicode]) and n.startswith('#')

class SpreadSheetReader(GsReader):

    def asTypedValue(self, s):
        s = s.strip()
        if self.doc_options.get('typed') != 'true':
            pass
        else:
            if s.isdigit(): return int(s)
            if isfloat(s): return float(s)

        return s

    def readAll(self):
        self.json = {}
        i = 0

        while True:
            sheet = self.getSheetAt(i)
            if not sheet: break
            if not sheet.title.strip().startswith('!'):
                self.loadSheetOf(sheet)
                self.readSheet()

            i += 1

        return self.json

    def readSheet(self):
        row, col = 0, 0

        while True:
            r = self.findCode(row, col)
            if not r: break
            row, col = r
            self.readAt(row, col)
            row, col = self.nextOf(row, col)

    def readAt(self, row, col):
        rootName, slist = self.interpretCode(self.valueAt(row, col))
        self.transposed = rootName.startswith('/')
        rootName = rootName.lstrip('/')
        if self.transposed:
            row, col = col, row
            
        #print rootName, slist

        if slist == '{}':
            self.json[rootName] = self.readMapAt(row, col)
        elif slist == '{}{}':
            self.json[rootName] = self.readMapOfMapAt(row, col)
        elif slist == '{}[]':
            self.json[rootName] = self.readMapOfListAt(row, col)
        elif slist == '[]{}':
            self.json[rootName] = self.readListOfMapAt(row, col)

        self.transposed = False

    def addKeyValue(self, m, k, v):
        k = k.strip()

        if k.endswith('[]'):
            k = k[:-2].strip()
            m[k] = [self.asTypedValue(s.strip()) for s in v.split(',')]
        elif k.endswith('[*]'):
            if v:
                k = k[:-3].strip()
                self.addKeyValueAsList(m, k, v)
        else:
            m[k] = self.asTypedValue(v)

    def addKeyValueAsList(self, m, k, v):
        if k in m:
            vl = m[k]
            if type(vl) is not list:
                vl = [vl]
        else:
            vl = []

        vl.append(v)
        m[k] = vl

    def readMapAt(self, row, col):
        keyCol = self.findCol(row,col+1, "$key")
        valCol = self.findCol(row,col+1, "$value")
        if not keyCol or not valCol: return {}

        m = {}

        row += 1
        while row < self.numRows:
            n = self.valueAt(row, keyCol).strip()
            v = self.valueAt(row, valCol)
            if not n: break
            if not isIgnoreKey(n):
                self.addKeyValue(m, n, v)
            row += 1
        return m

    def readMapOfMapAt(self, startRow, col):
        keyCol = self.findCol(startRow,col+1, "$key")
        if not keyCol: return {}
        m = {}

        row = startRow + 1
        while row < self.numRows:
            n = self.valueAt(row, keyCol).strip()
            if not n: break

            if not isIgnoreKey(n):
                info = {}
                m[n] = info

                col = keyCol + 1
                while col < self.numCols:
                    k = self.valueAt(startRow, col).strip()
                    if not k: break
                    if not isIgnoreKey(k):
                        v = self.valueAt(row, col)
                        self.addKeyValue(info, k, v)
                    col += 1

            row += 1
        return m

    def readListOfMapAt(self, startRow, startCol):
        m = []

        row = startRow + 1
        while row < self.numRows:
            v = self.valueAt(row, startCol+1).strip()
            if not v: break

            info = {}
            m.append(info)

            col = startCol + 1
            while col < self.numCols:
                k = self.valueAt(startRow, col).strip()
                if not k: break

                if not isIgnoreKey(k):
                    v = self.valueAt(row, col)
                    self.addKeyValue(info, k, v)

                col += 1

            row += 1
        return m

    def readMapOfListAt(self, startRow, startCol):
        m = {}

        col = startCol + 1
        while col < self.numCols:
            n = self.valueAt(startRow, col).strip()
            if not n: break

            if not isIgnoreKey(n):
                info = []
                m[n] = info

                row = startRow + 1
                while row < self.numRows:
                    v = self.valueAt(row, col).strip()
                    if not v: break
                    info.append( self.asTypedValue(v) )
                    row += 1

            col += 1
        return m

    def findCol(self, row, col, v):
        v = v.strip().lower()
        while col < self.numCols:
            if v == self.valueAt(row, col).strip().lower():
                return col
            col += 1


    def interpretCode(self, code):
        code = code.strip()
        if not code.startswith("#"): return
        code = code[1:]
        slist = []
        while code:
            r = code[-1]
            if r == '}':
                l = '{'
            elif r == ']':
                l = '['
            else:
                break
            i = code.find(l)
            if i < 0: break
            slist.append(l + r)
            code = code[:i] + code[i+1:-1]

        return code, ''.join(slist)


    def nextOf(self, row, col):
        return row, col + 1

    def findCode(self, row, col):
        while True:
            if col >= self.numCols:
                col = 0
                row += 1
            if row >= self.numRows:
                break

            v = self.valueAt(row, col)
            if self.interpretCode(v): return row, col

            col += 1
