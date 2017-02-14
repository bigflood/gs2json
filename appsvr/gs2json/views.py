from gs2json import app
from gspread.ns import _ns
from flask import request
from flask import make_response
from flask import render_template, url_for, redirect
from functools import wraps
from google.appengine.api import users
from PageInfo import PageInfo, get_doc_list, dataFromGDrive, Doc
import Models
from SpreadSheetReader import SpreadSheetReader
from TranslationsReader import TranslationsReader
from GsReader import toJson


def checkPermission(info, doc, useremail=None):
    if not doc: return False
    if info and info.isadmin: return True

    if info and not useremail:
        useremail = info.useremail

    print "checkPermission", info, doc, useremail

    authorEntry = doc._feed_entry.find(_ns('author'))
    #authorName = author.find(_ns('name')).text.strip()
    author = authorEntry.find(_ns('email')).text.strip()

    return useremail == author


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not users.get_current_user():
            return redirect(users.create_login_url(request.url))
        return func(*args, **kwargs)
    return decorated_view

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not users.is_current_user_admin():
            return redirect(url_for("admin_required_page"))
        return func(*args, **kwargs)
    return decorated_view

# ------------------------------------------------------------------------

@app.route('/')
def home_page():
    """Return a friendly HTTP greeting."""
    return render_template('home.html', info=PageInfo())

@app.route('/admin_required')
def admin_required_page():
    return render_template('admin_required.html', info=PageInfo())


@app.route('/list_docs', methods=['GET'])
@login_required
def list_docs():
    info=PageInfo()
    return render_template('list_docs.html', info=info, docs=get_doc_list(info))

@app.route('/regen_pass', methods=['GET'])
@login_required
def regen_pass():
    info=PageInfo()
    info.userInfo.private_pass = ('%x' % random.getrandbits(64))
    info.userInfo.put()
    return redirect(url_for('list_docs'))


@app.route('/json', methods=['GET'])
def json_data():
    info=PageInfo()
    try:
        private_pass = request.args.get('pass', '')
        key = request.args.get('key', '')
        owner, docid = key.split('/', 1)

        ownerData = Models.GetUserInfoWithId(owner)
        docData = Models.GetDocInfoWithId(key)
        print docData
        print ownerData
        if docData and ownerData and ownerData.private_pass == private_pass:
            docOptions = docData.getOptionsDict()
            prettyPrint = (docOptions.get('pretty') == 'true')

            doc = dataFromGDrive.open(name='', key=docid)

            if checkPermission(info, doc, useremail=owner):

                if docData.doc_mode == 'trans':
                    lang = request.args.get('lang', 'english')
                    reader = TranslationsReader(doc)
                    reader.doc_options = docOptions
                    json = toJson(reader.readAll(lang), pretty=prettyPrint)
                else:
                    reader = SpreadSheetReader(doc)
                    reader.doc_options = docOptions
                    json = toJson(reader.readAll(), pretty=prettyPrint)
            else:
                json = "{'error':'permission denied'}"
        else:
            json = "{'error':'invalid pass'}"

    except Exception as e:
        json = '{"error":"%s"}' % (repr(e),)

    resp = make_response(json)
    resp.mimetype = 'text/plain'
    return resp


@app.route('/table_view', methods=['GET'])
@admin_required
def table_view():

    info=PageInfo()
    sheets = []

    try:
        docid = request.args.get('docid', '')

        doc = dataFromGDrive.open(name='', key=docid)
        if checkPermission(info, doc):
            i = 0
            while True:
                ws = doc.get_worksheet(i)
                if not ws: break
                sheet = Doc()
                sheet.title = ws.title
                sheet.rows = ws.get_all_values()
                sheets.append(sheet)
                i += 1

    except Exception as e:
        sheet = Doc()
        sheet.title = repr(e)
        sheet.rows = []
        sheets.append(sheet)

    return render_template('table_view.html', info=info, sheets=sheets)

@app.route('/chmode', methods=['GET'])
@login_required
def chmode():
    info=PageInfo()

    mode = request.args.get('mode', '')
    docid = request.args.get('docid', '')
    doc = dataFromGDrive.open(name='', key=docid)
    if checkPermission(info, doc):
        key = '%s/%s' % (info.useremail, docid)
        docData = Models.GetDocInfoWithId(key)
        docData.doc_mode = mode
        docData.put()

    return redirect(url_for('list_docs'))
\
@app.route('/chmode2', methods=['GET'])
@login_required
def choption():
    info=PageInfo()

    name = request.args.get('name', '')
    docid = request.args.get('docid', '')
    doc = dataFromGDrive.open(name='', key=docid)
    if checkPermission(info, doc):
        key = '%s/%s' % (info.useremail, docid)
        docData = Models.GetDocInfoWithId(key)

        v = docData.getOption(name)
        if name == 'typed':
            v = (v == 'true') and 'false' or 'true'
        elif name == 'pretty':
            v = (v == 'true') and 'false' or 'true'
        docData.setOption(name, v)

        docData.put()

    return redirect(url_for('list_docs'))
