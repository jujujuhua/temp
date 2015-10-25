#error 0 : cannot find username
#error 1 : password mismatch
#error 2 : username and password did not pass validation test
#error 4 : username already exists

from flask import *
from flask import Flask
from flask_mail import Mail, Message
from flask_mail import Message
from flask import url_for
from datetime import timedelta
from datetime import datetime
import time
from validate_email import validate_email
import re
import hashlib
import MySQLdb as mdb
from smtplib import SMTP
import smtplib



pattern_usr = "^[A-Za-z0-9_]+$"
pattern_pwd = "^[a-zA-Z0-9_]*[a-zA-Z]+[a-zA-Z0-9_]*[0-9]+[a-zA-Z0-9_]*$||^[a-zA-Z0-9_]*[0-9]+[a-zA-Z0-9_]*[a-zA-Z]+[a-zA-Z0-9_]*$"
app.permanent_session_lifetime = timedelta(minutes=5)
app.secret_key = '\x92f\xa5#\xa2T\x91\xdc\xbd\x1f_\xbb|\x9c\x0c\xf8\xd6\x1d\xa3\x1d5G\x8d\x08'
main = Blueprint('main', __name__, template_folder='views')

duration = 300



def db_con():
    con = mdb.connect('localhost', 'group58', 'S200', 'group58')
    cur = con.cursor()
    con.autocommit(True)
    return cur


def validation(usr,pwd,email):

    if len(email) != 0 :
        if ( (not validate_email(email))or (len(email) >20) ):
            return False

    
    if (len(usr) < 3 or len(usr) > 20 or len(pwd) <5 or len(pwd)>15 ):
        return False 
    if (not re.match(pattern_usr,usr) or not re.match(pattern_pwd,pwd)):
        return False

    return True

def encrypt_password(pwd):
    m = hashlib.sha1()
    m.update(pwd)
    sha = m.hexdigest()
    return sha[0:20]

def authentication(pwd,ver):
    m = hashlib.sha1()
    m.update(pwd)
    sha = m.hexdigest()
    return sha[0:20] == ver

def album_authen(usr,aid):
    cur = db_con()
    accessLevel = 0
    cur.execute("SELECT username FROM Album WHERE albumid ='" + aid + "'" )
    username = cur.fetchone()[0]
    albumid = aid
    cur.execute("SELECT access FROM Album where albumid='" + albumid + "'")
    acc = cur.fetchone()[0]

    if username == usr:
        accessLevel = 3
    elif usr != "":
        if acc == "private":
            accessLevel = 0
            cur.execute("SELECT count(1) FROM AlbumAccess WHERE username = '" + usr + "' AND albumid ='"+aid+"'")
            accessLevel = cur.fetchone()[0]
        else:
            accessLevel = 1
    else:
        if acc == "private":
            accessLevel = 0
        else:
            accessLevel = 2
    return accessLevel


def session_exists_check():
    
    if( ('username' in request.cookies ) and ('lastactivity'in request.cookies)):
        if (time.time() - float(request.cookies['lastactivity']) < duration):
            return True
        else:
            session.pop('username',None)
            return False
    else:
        session.pop('username',None)
        return False

def display_public():
    cur = db_con()
    sql = "SELECT * FROM Album WHERE access = 'public' ORDER BY username; "
    cur.execute(sql)
    return cur.fetchall()

def display_private():
    user = session['username']
    cur = db_con()
    sql = "SELECT * FROM Album WHERE username = '"+user+"' "
    cur.execute(sql)
    return cur.fetchall()



def display_authorized():
    user = session['username']
    cur = db_con()
    sql = "SELECT * from Album INNER JOIN AlbumAccess ON Album.albumid=AlbumAccess.albumid WHERE AlbumAccess.username = '" + user + "' ORDER BY Album.username"
    print sql
    cur.execute(sql)
    return cur.fetchall()


def send_email(recv,msg0 ):
    msg = str(msg0)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('eecs485group58@gmail.com','eecsS200')
    server.sendmail('eecs485group58@gmail.com',recv,msg)
    server.quit()




@main.route('/n5hyqyyzaor/pa2/', methods=['GET', 'POST'])
def index():
    public_albums = display_public()
    if 'username' in session:
        #return str(('username' in session))
        if session_exists_check():
            private_albums = display_private()
            authorized_album = display_authorized()
            username = session['username']
            resp = make_response(render_template("logged_in_homepage.html",user = request.cookies["username"],albums_public = public_albums ,albums = private_albums,  albums_authorized= authorized_album))
            resp.set_cookie('lastactivity',str(time.time()))
            return resp 
        else:
            resp = make_response(render_template("default_home_page.html", album_list = public_albums ))
            return resp  
    else:
        resp = make_response(render_template("default_home_page.html", album_list = public_albums ))
        return resp
    
        #return render_template("logged_in_homepage.html", user = request.cookies["username"])
    

@main.route('/n5hyqyyzaor/pa2/user', methods=['GET', 'POST'])
def new_user_page():
    if request.method == 'POST':
        
        usr = request.form['username']
        pwd = request.form['pass0']
        pwd1 = request.form['pass1']
        lastname = request.form['lastname']
        firstname = request.form['firstname']
        email = request.form['email']

        if (not validation(usr,pwd,email)):
            return render_template("new_user.html",err=2),401
        cur = db_con()

        #detect if username exists
        cur.execute("SELECT username FROM User WHERE username = '"+usr+"';")
        rows = cur.fetchall()
        if len(rows) != 0:
            return render_template("new_user.html",err=4),401
        #server side check if two passwords match
        if (pwd != pwd1 ):
            return render_template("new_user.html",err=1),401
        encrypted_pwd = encrypt_password(pwd)
        #cur.execute("INSERT INTO User VALUES(%s''",'''%s''','''%s''',%s,%s');"%(usr,firstname,lastname,pwd,email))
        cur.execute("INSERT INTO User VALUES('"+usr+"','"+firstname+"','"+lastname+"','"+encrypted_pwd+"','"+email+"');")
        #Enrypt password

        m = hashlib.sha1()
        m.update(usr+encrypted_pwd)
        sha = m.hexdigest()   
        veri = sha[0:40]

        msg = "{{replace hostname here}}"+url_for('main.mail')+ "?username="+usr+"&ver="+usr+encrypted_pwd
        send_email(email,str(msg))
        
        return redirect(url_for('main.login'))

    return render_template("new_user.html" )



@main.route('/n5hyqyyzaor/pa2/user/edit', methods=['GET', 'POST'])
def edit_acc():    
    if (not session_exists_check() ):
        prev = url_for('main.edit_acc')
        return render_template("login.html",back_url = prev)

    if request.method == 'POST':
        if (not session_exists_check() ):
            prev = url_for('main.login')+ "?url="+url_for('main.edit_acc')
            return redirect(prev)

        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password0 = request.form['password0']
        password1 = request.form['password1']
        emailaddress = request.form['emailaddress']
        
        usr = session['username']
        if len(firstname) > 20 or len(lastname) > 20:
            return render_template("EditAccount.html", err = 5), 401
        if password0 != password1 :
            return render_template("EditAccount.html",err=1),401
        if (not validation(usr,password0,"") or (not validate_email(emailaddress))or (len(emailaddress) >20)):
            return render_template("EditAccount.html",err=2),401

        encrypted_pwd = encrypt_password(password0)
        cur = db_con()

        sql = "UPDATE User SET firstname = '"+firstname+"',lastname = '"+lastname+"',password = '"+encrypted_pwd+"',email = '"+emailaddress+"'"
        sql += " WHERE username = '"+usr+"'"
        cur.execute(sql)

        resp = make_response(redirect(url_for('main.index')) )
        resp.set_cookie('lastactivity',str(time.time()))
        return resp
    return render_template("EditAccount.html")


@main.route('/n5hyqyyzaor/pa2/usr/delete', methods=['GET', 'POST'])
def delete_acc():
    if session_exists_check():
        cur = db_con()
        usr = session['username']

        #Delete usr's access to other albums
        sql = "DELETE FROM AlbumAccess "
        sql += "WHERE username = '"+usr+"'"
        cur.execute(sql)

        #Get the ids of the usr's albums 
        sql = "SELECT albumid FROM Album "
        sql += "WHERE username = '"+usr+"'"
        cur.execute(sql)
        album_id_list = cur.fetchall()

        #Get the pic id of the usr
        pic_id_list = ()
        aid = ""
        for i in album_id_list:
            aid = str(int(i[0]))
            sql = "SELECT picid FROM Contain "
            sql += "WHERE albumid = "+aid+""
            cur.execute(sql)
            pic_id_list += cur.fetchall()

            #Delete usr's albums' access to other users        
            sql = "DELETE FROM AlbumAccess "
            sql += "WHERE albumid = '"+aid+"'"
            cur.execute(sql)
            sql = "DELETE FROM Contain "
            sql += "WHERE albumid = '"+aid+"'"
            cur.execute(sql)
         
            #Delete 


        #Delete pictures
        for i in pic_id_list:
            pid = i[0]
            sql = "DELETE FROM Photo "
            sql += "WHERE picid = '"+pid+"'"
            cur.execute(sql)

        #Delete Albums
        for i in album_id_list:
            aid = str(int(i[0]))
            sql = "DELETE FROM Album "
            sql += "WHERE albumid = '"+aid+"'"
            cur.execute(sql)


        #Delete User
        sql = "DELETE FROM User "
        sql += "WHERE username = '"+usr+"'"
        cur.execute(sql)

        
        return redirect(url_for('main.logout'))
    else:
        return redirect(url_for('main.login'))

    

@main.route('/n5hyqyyzaor/pa2/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        usr = request.form['username']
        pwd = request.form['password']

        cur = db_con()
        cur.execute("SELECT password FROM User WHERE username = '"+usr+"';")
        rows = cur.fetchall()

        prev_url = url_for('main.index')
        if 'url' in request.form:
            prev_url = request.form['url']
        
        if len(rows) == 0:
            return render_template("login.html",err=0,back_url = prev_url)
        if  not authentication(pwd, rows[0][0]):
            return render_template("login.html",err=1,back_url = prev_url)

        session['username'] = usr
        #stroe cookie
        
        if prev_url == "":
            resp = make_response(redirect(url_for('main.index')))
        else :
            #return prev_url
            resp = make_response(redirect(prev_url))

        resp.set_cookie('username', usr)
        resp.set_cookie('lastactivity',str(time.time()))
        #return url_for('main.index')
        return resp
        #return redirect(url_for('main.logged_in_homepage'))
    return render_template("login.html")

@main.route('/n5hyqyyzaor/pa2/logout', methods=['GET', 'POST'])
def logout():
    if session_exists_check():
        resp = make_response(redirect(url_for('main.index')))
        resp.set_cookie('lastactivity','0')
        session.pop('username',None)
        return resp
    else: 
        return render_template("login.html")



@main.route("/n5hyqyyzaor/pa2/invitation")
def mail():
    usr = request.args.get("username")
    veri_can = request.args.get("ver")
    cur = db_con()
    cur.execute("SELECT password FROM User WHERE username = '"+usr+"';")
    rows = cur.fetchall() 
    pwd = str(rows[0][0])

    m = hashlib.sha1()
    m.update(usr+pwd)
    sha = m.hexdigest()
    verify = sha[0:40]
    if (usr+pwd)== veri_can:
        session['username'] = usr
        resp = make_response(redirect(url_for('main.index')))
        resp.set_cookie('username', usr)
        resp.set_cookie('lastactivity',str(time.time()))
        #return url_for('main.index')
        return resp

    return redirect(url_for('main.index'))
   

@main.route('/n5hyqyyzaor/pa2/forgetpwd', methods=['GET', 'POST'])
def forgetpwd():

    if request.method == 'POST':
        #send emailaddress
        
        emailaddress= request.form['emailaddress']
        usr = request.form['username']
        cur = db_con()
        sql = "SELECT email FROM User"
        sql += " WHERE username = '"+usr+"'"
        cur.execute(sql)
        rows = cur.fetchall()
        if (len(rows)==0):
            
            return render_template("forgetpwd.html",err ='username not exists')
        if (rows[0][0] != emailaddress):
            
            return render_template("forgetpwd.html",err ='no email adress')

        default_password = encrypt_password("abcd0000")
        sql = "UPDATE User SET password = '"+default_password+"'"
        sql += " WHERE username = '"+usr+"'"
        cur.execute(sql)
        rows = cur.fetchall()


        #msg = "You new pwd is: abcd0000 Login through: "
        
        #url = url_for('main.index')
        #msg += url
        
        msg = "your new password is abcd0000 {{replace hostname here}}" + url_for('main.index')
        send_email(emailaddress,str(msg))

        return render_template("login.html")

    return render_template("forgetpwd.html")







