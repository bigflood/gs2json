
import json
import gspread
from gspread.ns import _ns
from oauth2client.client import SignedJwtAssertionCredentials
import sys

sys.path.append('./appsvr')

from GsReader import toJson
from TranslationsReader import TranslationsReader

docname = sys.argv[1]
print "File:", docname

json_key = json.load(open('appsvr/service_account.json'))
scope = ['https://spreadsheets.google.com/feeds']

credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)

gc = gspread.authorize(credentials)

doc = gc.open(docname)

reader = TranslationsReader(doc)
o = reader.readAll(sys.argv[1])

print toJson(o, pretty=True)

