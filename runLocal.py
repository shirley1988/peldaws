#!/usr/bin/env python

from praat import app, init_db

# Run server on port 5000
if __name__ == '__main__':
    app.config.update(
        SECRET_KEY = 'd83b92f46ec874a0e441abc51b797c6410380c48a301dfb5bbd5622f06321f50',
        DATABASE_URI = 'sqlite:///peldawsv1.db',
        GOOGLE_LOGIN_CLIENT_ID = '504212720496-k43hig4lcrt2c8ot6hdkelfvvme8tfq5.apps.googleusercontent.com',
        GOOGLE_LOGIN_CLIENT_SECRET = 'lroMckpPUtcgJdtgIbCmPTC2',
        GOOGLE_LOGIN_REDIRECT_URI = 'http://localhost:5000/oauth2callback',
        STAGE = 'development',
        STORAGE_LOCATION = 'local',
    )
    init_db()
    app.run(host='0.0.0.0', port=5000, threaded=True)
