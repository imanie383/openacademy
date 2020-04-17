#correr en pytho  2.8 en 3 no jala 
#python  xmlrpc_odoo_test.py
import functools
import xmlrpclib
HOST = 'localhost'
PORT = 8069
DB = 'imanie'
USER = 'admin'
PASS = 'admin'
ROOT = 'http://%s:%d/xmlrpc/' % (HOST,PORT)

# 1. Login
uid = xmlrpclib.ServerProxy(ROOT + 'common').login(DB,USER,PASS)
print "Logged in as %s (uid:%d)" % (USER,uid)

call = functools.partial(
    xmlrpclib.ServerProxy(ROOT + 'object').execute,
    DB, uid, PASS)

# 2. Read the sessions
#indicamos los campos que vamos a obtener
sessions = call('openacademy.session','search_read', [], ['name','seats','course_id'])
for session in sessions:
    print "Session %s (%s seats) %s" % (session['name'], session['seats'], session['course_id'])
# 3.create a new session
session_id = call('openacademy.session', 'create', {
    'name' : 'My session',
    'course_id' : 9,
})

#podemos usar todos los metodos
#buscamos un curso
course_id = call('openacademy.course','search', [('name','ilike','python')])[0]
session_id = call('openacademy.session', 'create', {
    'name' : 'My session 2',
    'course_id' : course_id,
})