
from flask import Flask, render_template
import controllers
import os

from flask_mail import Mail
from flask_mail import Message


app = Flask(__name__, template_folder='views')
app.register_blueprint(controllers.album)
app.register_blueprint(controllers.albums)
app.register_blueprint(controllers.pic)
app.register_blueprint(controllers.main)

app.secret_key = 'super secret key'





UPLOAD_FOLDER = './static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# comment this out using a WSGI like gunicorn
# if you dont, gunicorn will ignore it anyway
if __name__ == '__main__':
    # listen on external IPs
    app.run(host='0.0.0.0', port=20000, debug=True)