
import random
import json
import gspread
from gspread.ns import _ns
from oauth2client.client import SignedJwtAssertionCredentials

from GsReader import toJson
from SpreadSheetReader import SpreadSheetReader
import Models


from google.appengine.api import users
from flask import redirect, request
from google.appengine.api import modules



class Doc:
    def __init__(self):
        pass

    def getOptionDisplayString(self, name):
        v = self.doc_options.get(name, '')
        if name == 'typed':
            return (v == 'true') and 'typed' or 'string only'
        elif name == 'pretty':
            return (v == 'true') and 'pretty print' or 'compact print'
        return '%s=%s' % (name, v)

class DataFromGDrive:
    def __init__(self):
        self.json_key = json.load(open('service_account.json'))
        self.scope = ['https://spreadsheets.google.com/feeds']
        self.email = self.json_key['client_email']
        #self.credentials = AppAssertionCredentials(self.scope)

        self.credentials = SignedJwtAssertionCredentials(
            self.email,
            self.json_key['private_key'],
            self.scope)
        self.authorize()

    def authorize(self):
        self.gc = gspread.authorize(self.credentials)

    def list(self):
        for i in range(2):
            try:
                return self.listImpl()
            except gspread.exceptions.HTTPError as e:
                # Token invalid - Invalid token: Stateless token expired (oauth2)
                self.authorize()
        return []

    def listImpl(self):
        docs = []

        feed = self.gc.get_spreadsheets_feed()

        for elem in feed.findall(_ns('entry')):
            doc = Doc()
            doc.id = elem.find(_ns('id')).text.split('/')[-1].strip()
            doc.title = elem.find(_ns('title')).text.strip()
            doc.updated = elem.find(_ns('updated')).text.strip()
            author = elem.find(_ns('author'))
            #authorName = author.find(_ns('name')).text.strip()
            doc.author = author.find(_ns('email')).text.strip()

            docs.append(doc)

        return docs

    def open(self, name, key=""):
        for i in range(2):
            try:
                if name:
                    return self.gc.open(name)
                else:
                    return self.gc.open_by_key(key)
            except gspread.exceptions.HTTPError as e:
                # Token invalid - Invalid token: Stateless token expired (oauth2)
                self.authorize()

    def readSpreadsheet(self, name, sheet):
        sh = self.open(name)
        if not sh: return

        if type(sheet) is int:
            worksheet = sh.get_worksheet(sheet)
        else:
            worksheet = sh.worksheet(sheet)

        if not worksheet: return

        return worksheet.get_all_values()

dataFromGDrive = DataFromGDrive()

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


class PageInfo:
    def __init__(self):
        self.version = modules.get_current_version_name()
        self.accessorEmail = dataFromGDrive.email
        self.isadmin = users.is_current_user_admin()
        self.user = users.get_current_user()
        self.useremail = ""
        if self.user: self.useremail = self.user.email()
        if self.user:
            self.loginurl = ""
            self.logouturl = users.create_logout_url(request.url)
        else:
            self.loginurl = users.create_login_url(request.url)
            self.logouturl = ""

        if self.useremail:
            self.userInfo = Models.UserInfo.get_or_insert(self.useremail, private_pass='')
            if not self.userInfo.private_pass or self.userInfo.private_pass == 'aaaaa':
                self.userInfo.private_pass = ('%x' % random.getrandbits(64))
                self.userInfo.put()
        else:
            self.userInfo = None

    def private_pass(self):
        if self.userInfo:
            return self.userInfo.private_pass
        else:
            return ""


def get_doc_list(info):
    docs = []
    for doc in dataFromGDrive.list():
        if doc.author == info.useremail or info.isadmin:
            doc.key = "%s/%s" % (info.useremail, doc.id)

            data = Models.DocInfo.get_or_insert(doc.key, doc_mode='normal', doc_options='', doc_id=doc.id)

            doc.doc_mode = data.doc_mode
            if doc.doc_mode == 'normal':
                doc.other_mode = 'trans'
            else:
                doc.other_mode = 'normal'

            doc.doc_options = data.getOptionsDict()

            docs.append(doc)
    return docs
