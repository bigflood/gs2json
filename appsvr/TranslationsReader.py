# -*- coding: utf-8 -*-

from GsReader import *



class TranslationsReader(GsReader):

    def readAll(self, lang):
        self.lang = lang.strip().lower()
        self.json["version"] = 1
        self.json['language'] = self.lang
        self.json['updated'] = self.doc.get_worksheet(0).updated
        self.json['translations'] = self.readTranslations()

        return self.json

    def readTranslations(self):
        self.loadSheetAt(0)
        startRow, startCol = self.findCellWithValue('ID')
        headers = dict(map(lambda (x,y):(x.strip().lower(),y), self.readCellsH(startRow, startCol+1)))
        if self.lang not in headers: return []

        commentCol = startCol
        if 'comment' in headers: commentCol = headers['comment']
        translationCol = headers[self.lang]

        translationList = []
        row = startRow
        while row < self.numRows:
            row += 1
            translationId = self.valueAt(row, startCol)
            comment = self.valueAt(row, commentCol)
            translation = self.valueAt(row, translationCol)
            if translation:
                translationList.append([translationId, comment, translation])

        return translationList
