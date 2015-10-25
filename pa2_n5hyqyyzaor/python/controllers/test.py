
from flask import *
import MySQLdb as mdb
import re
import hashlib
import sys
import time 
main = Blueprint('main', __name__, template_folder='views')
con = mdb.connect('localhost', 'group58', 'S200', 'group58')
cur = con.cursor()


usr = ""
cur.execute("SELECT Username FROM User WHERE Username = 'a';")
#print cur.fetchall()


def validation(usr,pwd,email):
    if len(email) != 0 :
        print "aaa"
    else :
        print "bbb"


validation('a','b','')

s = "andajfksdl"
print '3' in s

pattern_pwd0 = "^[A-Za-z]+[0-9]+$" or "^[0-9]+[A-Za-z]+$"
usr = "usssr";
firstname = "fn"
lastname = "ln"
pwd = "pwd"
email = "em"
picid = "a"
encrypted_pwd = "aaaa"
a= ("INSERT INTO User VALUES('"+usr+"','"+firstname+"','"+lastname+"','"+encrypted_pwd+"','"+email+"')")
print    a 