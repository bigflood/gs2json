from google.appengine.api import users
from google.appengine.ext import ndb


class UserInfo(ndb.Model):
    """Sub model for representing an user info."""
    private_pass = ndb.StringProperty(indexed=False)

def GetUserInfoWithId(id):
    return ndb.Key(UserInfo, id).get()


class DocInfo(ndb.Model):
    """Sub model for representing an user info."""
    doc_mode = ndb.StringProperty(indexed=False)
    doc_options = ndb.StringProperty(indexed=False)
    doc_id = ndb.StringProperty(indexed=False)

    def getOptionsDict(self):
        d = {}
        if self.doc_options:
            for s in self.doc_options.split(','):
                if '=' in s:
                    n, v = s.split('=', 1)
                    d[n] = v
                else:
                    d[s] = 'true'

        return d

    def getOption(self, name):
        return self.getOptionsDict().get(name, '')

    def setOption(self, name, v):
        d = self.getOptionsDict()
        d[name] = v
        self.doc_options = ','.join(['%s=%s' % (n, v) for n, v in d.items()])

def GetDocInfoWithId(id):
    return ndb.Key(DocInfo, id).get()
