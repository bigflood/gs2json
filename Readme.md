## gs2json for Google App Engine


## Deploy
To deploy the application:
1. Install 3rd party libs
   (use install_3rd_party_libs.sh)

1. Use the [Admin Console](https://appengine.google.com) to create a
   project/app id. (App id and project id are identical)
   (update app.yaml and service_account.json)
1. [Deploy the
   application](https://developers.google.com/appengine/docs/python/tools/uploadinganapp) with

   ```
   appcfg.py -A <your-project-id> --oauth2 update .
   ```
1. Congratulations!  Your application is now live at your-app-id.appspot.com


## References

* [Flask micro framework](http://flask.pocoo.org).
* [Google Cloud Platform github repos](https://github.com/GoogleCloudPlatform)
* [App Engine Python SDK](https://developers.google.com/appengine/downloads).
