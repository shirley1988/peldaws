#!/usr/bin/env python

from praat import app, init_db

# Run server on port 80
if __name__ == '__main__':
    app.config.update(
        SECRET_KEY = '16f470fe142040d4def5597ab082c84d1b27eaf900ccaa8f74aa987328eaddc9',
        DATABASE_URI = 'mysql://appsrv@peldaws:4O8de38Fc1db@peldaws.mysql.database.azure.com/peldaws',
        GOOGLE_LOGIN_CLIENT_ID = '504212720496-a18osahn5t51jdffqh26hdhul2kblmsb.apps.googleusercontent.com',
        GOOGLE_LOGIN_CLIENT_SECRET = 'B6mzHoERK5lYv-nRImfd2-1o',
        GOOGLE_LOGIN_REDIRECT_URI = 'http://peldawsnliu.azurewebsites.net/oauth2callback',
        STAGE = 'production',
    )
    init_db()
    app.run(host='0.0.0.0', port=8000, threaded=True)
