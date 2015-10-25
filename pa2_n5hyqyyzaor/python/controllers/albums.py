
from flask import *
import MySQLdb as mdb
from datetime import datetime
import time

from main import session_exists_check,duration,db_con
from main import *
import os

albums = Blueprint('albums', __name__, template_folder='views')

UPLOAD_FOLDER = './static'

ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@albums.route('/n5hyqyyzaor/pa2/albums', methods=['GET', 'POST'])
def myAlbums():
    cur = db_con()

    if 'username' in session:
        if (not session_exists_check() ):
            prev = "/n5hyqyyzaor/pa2/albums"
            return render_template("login.html",back_url = prev)
    else:
        public_albums = display_public()
        return render_template("public_albums_of_all_users.html",album_list = public_albums)


    if(session_exists_check()):
        if (time.time() - float(request.cookies['lastactivity']) < duration):
            options = {
                "edit": False
            }
            username = session['username']
            cur.execute("SELECT count(1) FROM User WHERE username = '" + username + "'")
            result = cur.fetchone()
            cur.execute("SELECT * from Album where username='" + username + "'")
            rows = cur.fetchall()

            resp = make_response(render_template("albums.html", user = username, album_list = rows, **options))
            resp.set_cookie('lastactivity',str(time.time()))
            return resp
        else:
            return "a"   
    else:

        prev = "/n5hyqyyzaor/pa2/albums"#?url="+url_for('main.edit_acc')
        return render_template("login.html",back_url = prev)
        

    


@albums.route('/n5hyqyyzaor/pa2/albums/edit', methods=['GET', 'POST'])
def myAlbumsEdit():
    cur = db_con()
    options = {
            "edit": True
    }
    if not session_exists_check():
        prev = "/n5hyqyyzaor/pa2/albums/edit"
        return render_template("login.html",back_url = prev)

    username = session['username']
    if request.method == 'POST':
        op = request.form['op']
        
        if(op == "add"):
            title = request.form['title']
            #username = request.form['username']
            i = datetime.now()
            strDate = i.strftime('%y-%m-%d')
            cur.execute("INSERT INTO Album(title, created, lastupdated, username, access) VALUES('" + title + "', '" + strDate + "', '" + strDate + "','" + username + "', 'private')")
        elif(op == "delete"):
            albumid = request.form['albumid']
            cur.execute("SELECT * FROM Contain WHERE albumid='" + albumid + "'")
            pics = cur.fetchall()
            for pic in pics:
                            
                # Remove from Contain
                cur.execute("DELETE FROM Contain WHERE picid='" + pic[1] + "'")
                # Remove phy files
                cur.execute("SELECT * FROM Photo WHERE picid='" + pic[1] + "'")
                row = cur.fetchone()
                os.remove(app.config['UPLOAD_FOLDER']+ row[1])
                # Remove from Photo 
                cur.execute("DELETE FROM Photo WHERE picid='" + pic[1] + "'")
            # Remove Access
            cur.execute("DELETE FROM AlbumAccess WHERE albumid='" + albumid + "'")
            # Remove Album
            cur.execute("DELETE FROM Album WHERE albumid='" + albumid + "'")
            cur.execute("SELECT * from Album where username='" + username + "'")
            rows = cur.fetchall()
    cur.execute("SELECT * from Album where username='" + username + "'")
    rows = cur.fetchall()
    # return render_template("albums.html", user = username, album_list = rows, **options)
    resp = make_response(render_template("albums.html", user = username, album_list = rows, **options))
    resp.set_cookie('lastactivity',str(time.time()))
    return resp
