# import the necessary packages
from flask import Flask, render_template, redirect, url_for, request,session,Response
import pickle
#from phishing import *
import pickle
import tensorflow as tf
from keras.models import Sequential, Model, model_from_json, load_model
from keras.preprocessing import sequence
import json
from string import printable
import sqlite3
from qrReader import *
import os
from werkzeug import secure_filename
link = ""
# load json and create model
json_file = open('model3conv_200.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("model3conv_200.h5")
print("Loaded model from disk")

name = ''

app = Flask(__name__)

app.secret_key = '1234'
app.config["CACHE_TYPE"] = "null"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/', methods=['GET', 'POST'])
def landing():
	return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	global name
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		con = sqlite3.connect('mydatabase.db')
		cursorObj = con.cursor()
		cursorObj.execute(f"SELECT Name from Users WHERE Email='{email}' AND password = '{password}';")
		try:
			name = cursorObj.fetchone()[0]
			return redirect(url_for('home'))
		except:
			error = "Invalid Credentials Please try again..!!!"
			return render_template('login.html',error=error)
	return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		if request.form['sub']=='Submit':
			name = request.form['name']
			email = request.form['email']
			password = request.form['password']
			rpassword = request.form['rpassword']
			pet = request.form['pet']
			if(password != rpassword):
				error='Password dose not match..!!!'
				return render_template('register.html',error=error)
			try:
				con = sqlite3.connect('mydatabase.db')
				cursorObj = con.cursor()
				cursorObj.execute(f"SELECT Name from Users WHERE Email='{email}' AND password = '{password}';")
			
				if(cursorObj.fetchone()):
					error = "User already Registered...!!!"
					return render_template('register.html',error=error)
			except:
				pass
			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")			
			con = sqlite3.connect('mydatabase.db')
			cursorObj = con.cursor()
			cursorObj.execute("CREATE TABLE IF NOT EXISTS Users (Date text,Name text,Email text,password text,pet text)")
			cursorObj.execute("INSERT INTO Users VALUES(?,?,?,?,?)",(dt_string,name,email,password,pet))
			con.commit()

			return redirect(url_for('login'))

	return render_template('register.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
	error = None
	global name
	if request.method == 'POST':
		email = request.form['email']
		pet = request.form['pet']
		con = sqlite3.connect('mydatabase.db')
		cursorObj = con.cursor()
		cursorObj.execute(f"SELECT password from Users WHERE Email='{email}' AND pet = '{pet}';")
		
		try:
			password = cursorObj.fetchone()
			#print(password)
			error = "Your password : "+password[0]
		except:
			error = "Invalid information Please try again..!!!"
		return render_template('forgot-password.html',error=error)
	return render_template('forgot-password.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
	global name
	return render_template('home.html',name=name)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	return render_template('dashboard.html',name=name)


@app.route('/email', methods=['GET', 'POST'])
def email():
	if request.method == 'POST':
		sentence = request.form['script']
		# and later you can load it
		with open('bestModel.pkl', 'rb') as f:
			clf = pickle.load(f)
			pred = clf.predict([sentence])
			print(pred)

			if(pred[0] == 1):
				pred = "Phishing Email"
			else:
				pred = "Legitimate Email"

		return render_template('email.html',xss_r=pred,name=name)

	return render_template('email.html',name=name)

@app.route('/phishing', methods=['GET', 'POST'])
def phishing():
	if request.method == 'POST':
		url = request.form['url']
		# Step 1: Convert raw URL string in list of lists where characters that are contained in "printable" are stored encoded as integer 
		url_int_tokens = [[printable.index(x) + 1 for x in url if x in printable]]
		# Step 2: Cut URL string at max_len or pad with zeros if shorter
		max_len=75
		X = sequence.pad_sequences(url_int_tokens, maxlen=max_len)
		y_prob = loaded_model.predict(X,batch_size=1)
		result = 'Legitimate URL' if y_prob[0][0]<0.5 else 'Phishing URL'

		return render_template('phishing.html',url_r=result,name=name)

	return render_template('phishing.html',name=name)

@app.route('/image', methods=['GET', 'POST'])
def image():
	global link
	if request.method == 'POST':
		if request.form['sub']=='Upload':
			savepath = r'upload/'
			photo = request.files['photo']
			photo.save(os.path.join(savepath,(secure_filename(photo.filename))))
			image = cv2.imread(os.path.join(savepath,secure_filename(photo.filename)))
			cv2.imwrite(os.path.join("static/img/","test_image.jpg"),image)
			link = extract_qr_code("static/img/test_image.jpg")
			return render_template('image.html',link=link)
		elif request.form['sub'] == 'Test':
			url = link
			print("Url = ",url)
			# Step 1: Convert raw URL string in list of lists where characters that are contained in "printable" are stored encoded as integer 
			url_int_tokens = [[printable.index(x) + 1 for x in url if x in printable]]
			# Step 2: Cut URL string at max_len or pad with zeros if shorter
			max_len=75
			X = sequence.pad_sequences(url_int_tokens, maxlen=max_len)
			y_prob = loaded_model.predict(X,batch_size=1)
			result = 'Legitimate URL' if y_prob[0][0]<0.5 else 'Phishing URL'			
		
			return render_template('image.html',result1=result,link=link)
	return render_template('image.html')

# No caching at all for API endpoints.
@app.after_request
def add_header(response):
	# response.cache_control.no_store = True
	response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '-1'
	return response


if __name__ == '__main__' and run:
	app.run(host='0.0.0.0', debug=True, threaded=True)
