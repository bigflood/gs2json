
import json
import gspread
from gspread.ns import _ns
from oauth2client.client import SignedJwtAssertionCredentials
import sys

sys.path.append('./appsvr')

from SpreadSheetReader import SpreadSheetReader
from GsReader import toJson

docname = sys.argv[1]
print "File:", docname

json_key = json.load(open('appsvr/service_account.json'))
scope = ['https://spreadsheets.google.com/feeds']

credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)

gc = gspread.authorize(credentials)
#print dir(gc)

#try:

reader = SpreadSheetReader(gc.open(docname))
reader.doc_options = {}
prettyPrint = True

print toJson(reader.readAll(), pretty=prettyPrint)
