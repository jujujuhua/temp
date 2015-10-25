from flask import *
import MySQLdb as mdb
from main import session_exists_check,duration,db_con,album_authen
import time
from datetime import datetime

pic = Blueprint('pic', __name__, template_folder='views')


def updateTime(albumid):
    cur = db_con()
    i = datetime.now()
    strDate = i.strftime('%y-%m-%d')
    cur.execute("UPDATE Album SET lastupdated='" + strDate + "' WHERE albumid='" + albumid + "'")   


@pic.route('/n5hyqyyzaor/pa2/pic', methods=['GET', 'POST'])
def pic_route():

        usr = ''
        cur = db_con()

        
        if(request.method == "GET"):
                picid = request.args.get("id")
        else:
                picid = request.form["id"]

        cur.execute("SELECT albumid FROM Contain WHERE picid = '" + picid +"'")
        album_id = cur.fetchone()[0]
        albumid = str(album_id)
        cur.execute("SELECT access FROM Album WHERE albumid = '"+albumid+"'")
        access = cur.fetchone()[0]

        

        accessLevel = 2
        if  access == 'private':
                if not session_exists_check():
                        prev = "/album?id="+str(albumid)
                        return render_template("login.html",back_url = prev)
                else :
                        usr = session["username"]

        
        if 'username' in session:
                if (not session_exists_check() ):
                        prev = "/n5hyqyyzaor/pa2/pic?id="+picid
                        return render_template("login.html",back_url = prev)
                else:
                        accessLevel = album_authen(session['username'],str(album_id))
                        usr = session["username"]
        
        

        if (accessLevel == 0):
                return redirect(url_for('main.index'))


        

        options ={"nextend":False, "prevend": False, "canEdit": False, "edit":False}
        if(accessLevel == 3):
                options['canEdit'] = True

        picid = request.args.get('id')
        if(request.method == "POST"):

                picid = request.form['id']
                if(request.form['submit'] == "Edit"):
                        options['edit']=True
                if(request.form['submit'] == "Change"):

                        updateTime(str(album_id))
                        options['edit']=False
                        newCaption = request.form["newCaption"]
                        cur.execute("UPDATE Contain SET caption = '" + newCaption +"' WHERE picid = '" + picid + "' AND albumid='" + str(album_id) + "'")
                        print "UPDATE Contain SET caption = '" + newCaption +"' WHERE picid = '" + picid + "' AND albumid='" + str(album_id) + "'"          
      
        
        # check for valid picid
        cur.execute("SELECT count(1) FROM Photo WHERE picid = '" + picid +"'")
        result = cur.fetchone()

        if picid == "" or result[0] == 0:
                return make_response(render_template('404.html'),404)
        cur.execute("SELECT format FROM Photo WHERE picid='" + picid + "'")
        ext = cur.fetchone()
        cur.execute("SELECT albumid FROM Contain WHERE picid='" + picid + "'")
        row = cur.fetchone()
        albumid = row[0]
        fn = picid + "." + ext[0]
        
        ## get the next picid
        #  get oldseqNUm
        cur.execute("SELECT sequencenum FROM Contain WHERE picid='" + picid + "'")
        row = cur.fetchone()
        oldSeqnum = row[0]
        # Get next picid
        cur.execute("SELECT picid FROM Contain WHERE (sequencenum >'" + str(oldSeqnum) + "') and (albumid='" + str(albumid) + "') ORDER BY sequencenum")
        row = cur.fetchone()
        if row != None:
                nextid = row[0]
        else:
                nextid = picid
                options["nextend"] = True
        ## get the prev picid
        cur.execute("SELECT picid FROM Contain WHERE (sequencenum <'" + str(oldSeqnum) +"') and (albumid='" + str(albumid) + "') ORDER BY sequencenum DESC")
        row2 = cur.fetchone()
        if row2 != None:
                previd = row2[0]
        else:
                previd = picid
                options["prevend"] = True

        cur.execute("SELECT caption FROM Contain WHERE albumid='" + str(albumid) + "' and picid = '" + picid + "'")
        caption = cur.fetchone()[0]

        resp = make_response(render_template("view_pic.html",user = usr, currPid = picid,picCaption = caption, albid=albumid, npid=nextid, ppid= previd, filename = fn, **options))
        resp.set_cookie('lastactivity',str(time.time()))

        return resp
