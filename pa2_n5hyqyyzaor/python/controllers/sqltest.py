
from flask import *
import MySQLdb as mdb
from datetime import datetime
import mimetypes
import os.path

album = Blueprint('album', __name__, template_folder='views')
con = mdb.connect('localhost', 'group58', 'S200', 'group58')
con.autocommit(True)
cur = con.cursor()

albumid = '4'



filename = "bbb.JpG"
type, trashs = mimetypes.guess_type(filename)

print os.path.basename(type)



