
from flask import *
import MySQLdb as mdb
import os
from werkzeug import secure_filename
import hashlib
import time
from main import session_exists_check,duration,db_con,album_authen
from datetime import datetime
import mimetypes
import os.path

album = Blueprint('album', __name__, template_folder='views')
con = mdb.connect('localhost', 'group58', 'S200', 'group58')
con.autocommit(True)
cur = con.cursor()

UPLOAD_FOLDER = './static'

ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
        return os.path.basename(mimetypes.guess_type(filename)[0]) in ALLOWED_EXTENSIONS

def updateTime(albumid):
    cur = db_con()
    i = datetime.now()
    strDate = i.strftime('%y-%m-%d')
    cur.execute("UPDATE Album SET lastupdated='" + strDate + "' WHERE albumid='" + albumid + "'")   


@album.route('/n5hyqyyzaor/pa2/album', methods=['GET', 'POST'])
def viewAlbum():

    cur = db_con()
    
    albumid = request.args.get("id")
    username = ""
    accessLevel = 2
    if 'username' in session:
        if not session_exists_check():
                prev = "/n5hyqyyzaor/pa2/album?id="+str(albumid)
                return render_template("login.html",back_url = prev)
        accessLevel = album_authen(session['username'],albumid)
        username = session['username']

    if (accessLevel == 0):
        return redirect(url_for('main.index'))


    
    cur.execute("SELECT access FROM Album WHERE albumid = '"+albumid+"'")
    access = cur.fetchone()[0]

    
    if  access == 'private':
        if not session_exists_check():
                prev = "/album?id="+str(albumid)
                return render_template("login.html",back_url = prev)
        else :
                username = session["username"]
    
    options = {"edit": False, "canEdit":False}
    if accessLevel == 3:
        options["canEdit"] = True

    albumid = request.args.get("id")
    cur.execute("SELECT * FROM User")
    usrs = cur.fetchall()
    albumid = request.args.get("id")
    # check for invalid album id
    cur.execute("SELECT count(1) FROM Album WHERE albumid = '" + albumid +"'")
    result = cur.fetchone()
    if albumid == "" or result[0] == 0:
        return make_response(render_template('404.html'),404)
    
    cur.execute("SELECT * from Contain where albumid='" + albumid + "' ORDER BY sequencenum")
    rows = cur.fetchall()
    
    cur.execute("SELECT title FROM Album WHERE albumid='" + albumid + "'")
    title = cur.fetchone()[0]

    cur.execute("SELECT * from Photo INNER JOIN Contain on Photo.picid=Contain.picid where albumid= '" + albumid + "' ORDER BY sequencenum")
    thumb = cur.fetchall()

    cur.execute("SELECT username FROM Album WHERE albumid='" + albumid + "'")
    own = cur.fetchone()[0]
    
    resp = make_response(render_template("edit_album.html", albumOwner= own, zipped = zip(rows, thumb), users = usrs, user = username, pics=rows, id = albumid, albumTitle = title, **options))
    if accessLevel != 2 :
        resp.set_cookie('lastactivity',str(time.time()) )
    return resp
    


    

@album.route('/n5hyqyyzaor/pa2/album/edit', methods=['GET', 'POST'])
def editAlbum():
    #albumid = request.form['id']
    albumid = request.args.get("id")    
    if not session_exists_check():

        prev = "/n5hyqyyzaor/pa2/album/edit?id="+albumid#?url="+url_for('main.edit_acc')
        return render_template("login.html",back_url = prev)

    #album_id = request.args.get("id")
    accessLevel = album_authen(session['username'],albumid)
    if (accessLevel != 3):
        return redirect(url_for('main.index'))
    
    username = session["username"]
    options = {"edit": True, "canEdit": False}
    if accessLevel == 3:
        options["canEdit"] = True
    cur.execute("SELECT * FROM User")
    usrs = cur.fetchall()
    #albumid = request.args.get("id")
    # check for invalid album id
    cur.execute("SELECT count(1) FROM Album WHERE albumid = '" + albumid +"'")
    result = cur.fetchone()
    if(request.method=="POST"):
        op = request.form["op"]
        if (op == "delete"):
            picid = request.form["picid"]
            albumid = request.form["albumid"]
            cur.execute("SELECT * FROM Photo WHERE picid ='" + picid + "'")
            pic = cur.fetchone()
            #Remove from Contain
            cur.execute("DELETE FROM Contain WHERE picid='"+ picid + "'")
            #Remove phy files
            os.remove(app.config['UPLOAD_FOLDER'] + pic[1])
            #Remove from Photo
            cur.execute("DELETE FROM Photo WHERE picid='" + picid + "'")
            #Update date modified
            
            updateTime(albumid)

        elif (op == "add"):
            file = request.files['file']
            albumid = request.form["albumid"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # picid
                i = datetime.now()
                picid = hashlib.md5("filename" + i.strftime('%y-%m-%d-%H:%M:%S')).hexdigest()
                # extention
                ext = file.filename.rsplit('.', 1)[1]

                # seq num
                seqnum = '0'
                cur.execute("SELECT MAX(sequencenum) FROM Contain where albumid ='" + albumid + "'")
                row = cur.fetchone()
                if row[0] != None:
                        seqnum = str(int(row[0]) + 1)
                strDate = i.strftime('%y-%m-%d')

                # URL
                url = "/pictures/" + picid + "." + ext

                # Save physical files
                file.save(os.path.join(app.config['UPLOAD_FOLDER'] + "/pictures", picid+"."+ext))
                # Insert into Photo
                cur.execute("INSERT INTO Photo VALUES('" + picid + "', '" + url + "', '" + ext + "', '" + strDate + "')")

                # Insert into Contain
                cur.execute("INSERT INTO Contain VALUES(" + albumid + ", '" + picid + "', '" + picid + "." + ext + "'," + seqnum + ")")

                # Update last updated date
                updateTime(albumid)
        elif (op=="change"):
            access = request.form['access']
            if(access != "nochange"):
                cur.execute("UPDATE Album SET access='" + access + "' WHERE albumid='" + albumid + "'")
            updateTime(albumid)
            if access == "public":
                cur.execute("DELETE FROM AlbumAccess WHERE username !='" + username + "' AND albumid = '" + albumid + "'")
            else:
                operation = request.form['submit']
                if operation == 'Add':
                    
                    name = request.form['names']
                    # cur.execute("INSERT INTO AlbumAccess VALUES('" + albumid + "','" + name +"')")
                    cur.execute("INSERT INTO AlbumAccess VALUES('"+albumid + "','" +name +"') ON DUPLICATE KEY UPDATE albumid=albumid")
                elif operation == 'revoke':
                    name = request.form['name']
                    cur.execute("DELETE FROM AlbumAccess WHERE username ='" + name + "' AND albumid = '" + albumid + "'")   
                elif operation == 'rename':
                    newTitle = request.form['newName']
                    cur.execute("UPDATE Album SET title = '" + newTitle + "' WHERE albumid = '" + albumid + "'")
                

    cur.execute("SELECT count(1) FROM Album WHERE albumid = '" + albumid + "'")
    result = cur.fetchone()
    if albumid == "" or result[0] == 0:
            return make_response(render_template('404.html'),404)
    cur.execute("SELECT * from Contain where albumid='" + albumid + "' ORDER BY sequencenum")
    rows = cur.fetchall()


    cur.execute("SELECT username FROM AlbumAccess WHERE albumid='" + albumid + "'")
    aUsers = cur.fetchall()

    cur.execute("SELECT username FROM User WHERE username NOT IN (SELECT username FROM AlbumAccess WHERE albumid ='" + albumid + "')")
    usrs = cur.fetchall()    
    cur.execute("SELECT username FROM Album WHERE albumid ='" + albumid + "'")
    owner = cur.fetchone()
    #print owner == usrs[0]
    newUsrs = []
    for a in usrs:
        if a != owner:
            newUsrs.append(a)
    
    
    cur.execute("SELECT title FROM Album WHERE albumid='" + albumid + "'")
    title = cur.fetchone()[0]

    cur.execute("SELECT username FROM Album WHERE albumid='" + albumid + "'")
    own = cur.fetchone()[0]

    cur.execute("SELECT * from Photo INNER JOIN Contain on Photo.picid=Contain.picid where albumid= '" + albumid + "' ORDER BY sequencenum")
    thumb = cur.fetchall()

    resp = make_response(render_template("edit_album.html", albumOwner = own, zipped = zip(rows, thumb), unallowedUsers = newUsrs, allowedUsers = aUsers, user = username , pics=rows, id = albumid, albumTitle = title, **options))
    resp.set_cookie('lastactivity',str(time.time()))
    return resp




# @album.route('/static/pictures/<path:filename>', methods=['GET','POST'])
# def serve_image(filename):
#                 return send_from_directory(app.config['UPLOAD_FOLDER'] + "/pictures", filename)
                
                
