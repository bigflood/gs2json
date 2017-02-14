from flask import Flask
import settings

app = Flask('gs2json')
app.config.from_object('gs2json.settings')

import views
