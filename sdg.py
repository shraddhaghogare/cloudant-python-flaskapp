# http://code.runnable.com/UiPcaBXaxGNYAAAL/how-to-upload-a-file-to-the-server-in-flask-for-python
# https://pythonprogramming.net/flask-users-tutorial/?completed=/flash-flask-tutorial/
# http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
# http://python-cloudant.readthedocs.io/en/latest/getting_started.html
# http://stackoverflow.com/questions/30597687/how-can-i-connect-to-cloudant-from-a-flask-app-running-in-bluemix
# http://pythoncentral.io/hashing-files-with-python/
# http://opentechschool.github.io/python-flask/core/form-submission.html
# http://stackoverflow.com/questions/18010876/how-to-check-if-a-couchdb-document-exists-using-python
# https://www.decalage.info/python/html#attachments


"""Cloud Foundry test"""
from flask import Flask, flash, redirect, render_template, \
     request, url_for
import requests
import HTML
import sys
import os
import hashlib
import platform
import os.path, time
import cgi, io
import json
import requests
import cgitb; cgitb.enable()
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
from cloudant.client import Cloudant
from cloudant.document import Document

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Emit Bluemix deployment event
#cf_deployment_tracker.track()

app = Flask(__name__)

app.config.update(
    DEBUG=True,
)

UPLOAD_FOLDER = '/home/sdg/Desktop/output/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.secret_key = 'sdg is crazy'

@app.route('/')
def main():
    	return render_template('index.html')

#------------------------------------------------------------------------------------------------------------------
@app.route('/DeleteFile',methods=['GET','POST'])
def DeleteFile():
	return render_template('file-delete.htm')	

@app.route('/delfile',methods=['POST'])
def delfile():
	fileName=request.form['fileName']
	fileVersion=request.form['fileVersion']

	client = Cloudant("accesS_key","secret key", 	url='url')
	client.connect()
    	session = client.session()
    	my_database = client['test']

	selector = {'name': {'$eq': fileName} }
	resp =my_database.get_query_result(selector, raw_result=True, limit=100)
	if resp['docs']:
		for doc in resp['docs']:
			if doc in resp['docs']:
				#selector1 = {'version': {'$eq': fileVersion}}
				#resp1 = my_database.get_query_result(selector1, raw_result=True, limit=100)
				#print doc['version']
				#print fileVersion
				if(doc['version']==int(fileVersion)):
					#print doc['_id']
					dId=doc['_id']
					my_document = my_database[dId]
					# Delete the document
					my_document.delete()
					#doc['name'].delete()
					html = '''<html>
					<title>Attributes</title>
					%s
					</html>''' %('Document Deleted')    
					client.disconnect()   
					return html
				else:
					html = '''<html>
					<title>Attributes</title>
					File with entered version not found.
					</html>''' #%(doc['content'])    
					return html
	else:
		html = '''<html>
		<title>Attributes</title>
		File not found.
		</html>''' #%(doc['content'])    
		return html

#------------------------------------------------------------------------------------------------------------------
@app.route('/file-upload', methods=['GET', 'POST'])
def fileUpload():
	return render_template('file-upload.htm')

@app.route('/fileDownload',methods=['GET','POST'])
def fileDownload():
	return render_template('file-download.htm')	

@app.route('/downloadfile',methods=['POST'])
def downloadfile():
	fileName=request.form['fileName']
	fileVersion=request.form['fileVersion']
	#print 'here: '+fileName
	#return redirect('/')

	client = Cloudant("accesS_key","secret key", 	url='url')

	client.connect()
    	session = client.session()
    	my_database = client['test']

	selector = {'name': {'$eq': fileName} }
	resp =my_database.get_query_result(selector, raw_result=True, limit=100)
	if resp['docs']:
		for doc in resp['docs']:
			if doc in resp['docs']:
				if(doc['version']==int(fileVersion)):
					html = '''<html>
					<title>Attributes</title>
					%s
					</html>''' %(doc['content'])   
					with io.FileIO(doc['name'], "w") as file:
					    file.write(doc['content']) 
					client.disconnect()   
					return html
				else:
					html = '''<html>
					<title>Attributes</title>
					File with entered version not found.
					</html>'''     
					return html
	else:
		html = '''<html>
		<title>Attributes</title>
		File not found.
		</html>'''    
		return html

@app.route('/ListFiles',methods=['GET','POST'])
def ListFiles():
	client = Cloudant("accesS_key","secret key", 	url='url')

	client.connect()
	session = client.session()
	print 'Username: {0}'.format(session['userCtx']['name'])
	print 'Databases: {0}'.format(client.all_dbs())
	my_database = client['test']
	## Get all of the documents from my_database
	t = HTML.Table(header_row=['File Name', 'File Version', 'Last Modified Date'])
	for document in my_database:
		t.rows.append([document['name'],document['version'],document['Last_Modified_Date']])
	htmlcode = str(t)
    	return htmlcode

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/save-file', methods=['GET','POST'])
def saveFile():	
	import os, time
	file = request.files['file']
        filename =  file.filename
	fContent = file.read()
	BLOCKSIZE = 65536
	(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filename)
	last_modified_date = time.ctime(mtime)
	hasher = hashlib.sha1()
	with open(filename, 'rb') as afile:
	    buf = afile.read(BLOCKSIZE)
	    while len(buf) > 0:
        	hasher.update(buf)
	        buf = afile.read(BLOCKSIZE)
 	client = Cloudant("accesS_key","secret key", 	url='url')

	client.connect()
	i=1
	session = client.session()
	my_database = client['test']
	temp = list()
	selector = {'name': {'$eq': filename}}
	resp = my_database.get_query_result(selector, raw_result=True, limit=100)
	if resp['docs']:
		for doc in resp['docs']:
			if(doc['name']==filename):
				# file exists, update version
				if (doc['hash']!=hasher.hexdigest()):
					print 'just update version. Content Edited'
					i=doc['version']
					i=int(i+1)
					data = {
					    'name': filename,
					    'content': fContent,
					    'Last_Modified_Date': 'some date',
					    'version': i,
					    'hash': hasher.hexdigest()
					    }	
					my_document = my_database.create_document(data)
					return render_template('file-upload.htm')

				# else check if document exists and file content is same.	
				else:
					if(doc['hash']==hasher.hexdigest()):
						print 'File has NOT been modified'
						html = '''<html>
						<title>Attributes</title>
						%s
						</html>''' %('File already exists!')    
						return html

	# file is brand new.
	else:
		data = {
		    'name': filename,
		    'content': fContent,
		    'Last_Modified_Date': last_modified_date,
		    'version': 1,
		    'hash': hasher.hexdigest()
		    }	
		my_document = my_database.create_document(data)
		return render_template('file-upload.htm')


port = os.getenv('VCAP_APP_PORT', '5000')	
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))

