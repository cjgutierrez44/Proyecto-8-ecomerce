from flask import Flask, render_template, redirect, request, session, flash, redirect, url_for
import json
import os
from werkzeug.utils import secure_filename
import requests
app	= Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route("/")
def index():
	return render_template("home.html")


@app.route("/login", methods=['POST' , 'GET'])
def login():
	if "user" in session:
		return redirect(url_for("index"))
	if request.method == "GET":	
		return render_template("login.html")
	else:

		data={"email": request.form["email"], "password": request.form["password"]}

		headers = {'Content-Type': 'application/x-www-form-urlencoded'}

		url = "http://127.0.0.1:8080/api/users/login"
		resp = requests.post(url, data=data, headers = headers)
		if resp.status_code == 200:
			print("no hay error")
			if resp.text != "":
				user = resp.json()
				session["user"] = user
			else:
				flash("Correo o contraseña incorrectos")
				return render_template("login.html")

		return redirect(url_for("index"))

@app.route("/logout")
def logout():
	session.pop('user', None)
	return redirect(url_for("index"))

@app.route("/reset")
def reset():
	if "user" in session:
		return redirect(url_for("index"))
	return render_template("resetPassword.html")


@app.route("/register", methods=['POST', 'GET'])
def register():
	if "user" in session:
		return redirect(url_for("index"))
	if request.method == "GET":
		url = "http://127.0.0.1:8080/api/departments"
		departments = requests.get(url).json()
		url = "http://127.0.0.1:8080/api/streetTypes"
		streetTypes = requests.get(url).json()
		return render_template("register.html", departments = departments, streetTypes = streetTypes)	
	else:
		user = {
			"name": request.form['name'],
			"lastName": request.form['lastName'],
			"phone": int(request.form['phone']),
			"email": request.form['email'],
			"password": request.form['password'],
			"city": {
				"id": int(request.form['city']),
				"name": ""
			},
			"streetType": {
				"id": int(request.form['streetType']),
				"name" : ""
			},
			"street": request.form['street'],
			"addressNumber": request.form['number'],
			"addressHouse": request.form['house'],
			"addressAditionalInfo": request.form['infoAddress']
		};
		headers = {'Content-type': 'application/json'}
		url = "http://127.0.0.1:8080/api/users/register"
		resp = requests.post(url, data=json.dumps(user), headers=headers)

		return redirect(url_for("login"))
	
@app.route("/editProfile", methods = ["GET", "POST"])
def editProfile():
	if request.method == "GET":
		if "user" in session:
			url = "http://127.0.0.1:8080/api/streetTypes"
			streetTypes = requests.get(url).json()
			return render_template("editProfile.html", user = session["user"], streetTypes = streetTypes)
		else:
			return redirect(url_for("index"))
	else:
		pass

@app.route("/registerProduct", methods = ["GET", "POST"])
def registerProduct():
	if "user" in session:
	
		if request.method == "GET":
			if "user" in session:
				url = "http://127.0.0.1:8080/api/categories"
				categories = requests.get(url).json()
				return render_template("registerProduct.html", categories = categories)
		else:


			eanCode = request.form['eanCode']
			name = request.form['name']
			description = request.form['description']
			brand = request.form['brand']
			price = request.form['price']
			picture =  request.files['picture']
			quantity = request.form['quantity'] 
			category = request.form['category']

			img_filename = secure_filename(picture.filename)
			picture.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))


			product = {            
				"eanCode": eanCode,
				"name": name,
				"description": description,
				"brand": brand,
				"price": price,
				"picture": "http://localhost:5000/static/uploads/" + img_filename,
				"quantity": quantity,
				"category":{
					"id": category,
					"name": ""
				}
			}

			headers = {'Content-type': 'application/json'}
			url = "http://localhost:8080/api/products/save"
			resp = requests.post(url, data=json.dumps(product), headers=headers)
			print(resp)
			return redirect(url_for("shop"))
	else:
		return redirect(url_for("login"))

@app.route("/shop")
def shop():
	url = "http://127.0.0.1:8080/api/categories"
	categories = requests.get(url).json()
	categoryId = str(request.args.get('categoryId'))
	try:
		entero = int(categoryId)
		url = "http://127.0.0.1:8080/api/products/ByCategoryId/"+categoryId
	except ValueError:
		print("todo")
		keyword = request.args.get('keyword')
		if keyword is None:
			keyword = ""

		minPrice = request.args.get('minPrice')
		maxPrice = request.args.get('maxPrice')

		if minPrice is None or minPrice == "":
			minPrice = 0

		if maxPrice is None or maxPrice == "":
			maxPrice = 0

		url = "http://127.0.0.1:8080/api/products?keyword=" + keyword + "&minPrice=" + str(minPrice) + "&maxPrice=" + str(maxPrice)
	products = requests.get(url).json()
	return render_template("shop.html", categories = categories, products = products)



@app.route("/shop/product/<id>")
def product(id):
	url = "http://127.0.0.1:8080/api/products/byId/" + id
	product = requests.get(url).json()
	url = "http://127.0.0.1:8080/api/comments/byProductId/" + id
	comments = requests.get(url).json()
	return render_template("product.html", product = product, comments = comments)


@app.route("/shop/product/<id>/comment", methods = ["POST"])
def comment(id):
	comment = {
		"product": {
		"id": id
		},
		"user":{
		"id": session["user"]["id"]
		},
		"comment": request.form["comment"],
		"date": ""
	}

	headers = {'Content-type': 'application/json'}
	url = "http://127.0.0.1:8080/api/comments/save/" + id
	
	resp = requests.post(url, data=json.dumps(comment), headers=headers)
	return redirect(url_for("product", id = id))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


app.run(host = "192.168.1.6")










