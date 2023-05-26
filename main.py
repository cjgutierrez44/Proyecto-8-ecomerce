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

api = "http://44.211.126.252/api"

@app.route('/userInSession', methods=['GET'])
def userInSession():
	if "user" in session:
		user = str(session["user"]["id"])
	else:
		user = "null"
	return user



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

		url = api + "/users/login"
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
		url = api + "/departments"
		departments = requests.get(url).json()
		url = api + "/streetTypes"
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
		url = api + "/users/register"
		resp = requests.post(url, data=json.dumps(user), headers=headers)

		return redirect(url_for("login"))
	
@app.route("/editProfile", methods = ["GET", "POST"])
def editProfile():
	if request.method == "GET":
		if "user" in session:
			url = api + "/streetTypes"
			streetTypes = requests.get(url).json()
			return render_template("editProfile.html", user = session["user"], streetTypes = streetTypes)
		else:
			return redirect(url_for("index"))
	else:
		return redirect(url_for("editProfile"))

@app.route("/registerProduct", methods = ["GET", "POST"])
def registerProduct():
	if "user" in session:
	
		if request.method == "GET":
			if "user" in session:
				url = api + "/categories"
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

			img_filename = eanCode + "-"+secure_filename(picture.filename)

			picture.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))

			img_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))

			with open(img_path, 'rb') as f:
				imagen = f.read()

			product = {            
				"eanCode": eanCode,
				"name": name,
				"description": description,
				"brand": brand,
				"price": price,
				"picture": img_filename,
				"quantity": quantity,
				"category":{
					"id": category,
					"name": "",
				},
				"user": {
					"id": session["user"]["id"]
				}
				
			}

			headers = {'Content-type': 'application/json'}
			url = api + "/products/save"
			resp = requests.post(url, data=json.dumps(product), headers=headers)


			url = api + "/products/upload/"+ img_filename
			response = requests.post(url, files={'file': imagen})

			return redirect(url_for("shop"))
	else:
		return redirect(url_for("login"))

@app.route("/shop")
def shop():
	url = api + "/categories"
	categories = requests.get(url).json()
	categoryId = str(request.args.get('categoryId'))
	try:
		entero = int(categoryId)
		url = api + "/products/ByCategoryId/"+categoryId
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

		url = api + "/products?keyword=" + keyword + "&minPrice=" + str(minPrice) + "&maxPrice=" + str(maxPrice)
	products = requests.get(url).json()
	return render_template("shop.html", categories = categories, products = products)



@app.route("/shop/product/<id>")
def product(id):
	url = api + "/products/byId/" + id
	product = requests.get(url).json()
	url = api + "/comments/byProductId/" + id
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
	url = api + "/comments/save/" + id
	
	resp = requests.post(url, data=json.dumps(comment), headers=headers)
	return redirect(url_for("product", id = id))

@app.route("/myProducts")
def myProducts():
	if "user" in session:
		url = api + "/products/ByUserId/" + str(session["user"]["id"])
		products = requests.get(url).json()
		return render_template("myProducts.html", products = products)
	else:
		return redirect(url_for("index"))

@app.route("/deleteProduct/<id>")
def deleteProduct(id):
	if "user" in session:
		url = api + "/products/byId/" + id
		product = requests.get(url).json()
		if product["user"]["id"] == session["user"]["id"]:
			url = api + "/products/remove/" + id
			resp = requests.get(url).json()
			return  redirect(url_for("myProducts"))
		else:
			return redirect(url_for("myProducts"))
	else:
		return redirect(url_for("index"))

@app.route("/myProducts/deleted")
def deletedProducts():
	if "user" in session:
		url = api + "/products/ByUserIdDeleted/" + str(session["user"]["id"])
		products = requests.get(url).json()
		return render_template("myProducts.html", products = products)
	else:
		return redirect(url_for("index"))


@app.route("/restoreProduct/<id>")
def restoreProduct(id):
	if "user" in session:
		url = api + "/products/byId/" + id
		product = requests.get(url).json()
		if product["user"]["id"] == session["user"]["id"]:
			url = api + "/products/restore/" + id
			resp = requests.get(url).json()
			return  redirect(url_for("deletedProducts"))
		else:
			return redirect(url_for("deletedProducts"))
	else:
		return redirect(url_for("index"))


@app.route("/updateProduct/<id>", methods = ["GET", "POST"])
def updateProduct(id):
	if "user" in session:
		if request.method == "GET":
			url = api + "/products/byId/" + id
			product = requests.get(url).json()
			if product["user"]["id"] == session["user"]["id"]:
				url = api + "/categories"
				categories = requests.get(url).json()
				return render_template("editProduct.html", product = product, categories = categories)
			else:
				return redirect(url_for("myProducts"))
		else:
			url = api + "/products/byId/" + id
			productE = requests.get(url).json()

			eanCode = request.form['eanCode']
			name = request.form['name']
			description = request.form['description']
			brand = request.form['brand']
			price = request.form['price']
			picture =  request.files['picture']
			quantity = request.form['quantity'] 
			category = request.form['category']

			img_filename = eanCode + "-"+secure_filename(picture.filename)

			if secure_filename(picture.filename) == "":
				img_filename = productE["picture"]
			else:
				picture.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
				img_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
				with open(img_path, 'rb') as f:
					imagen = f.read()
				url = api + "/products/upload/"+ img_filename
				response = requests.post(url, files={'file': imagen})
				
			product = {
				"id": id,
				"eanCode": eanCode,
				"name": name,
				"description": description,
				"brand": brand,
				"price": price,
				"picture": img_filename,
				"quantity": quantity,
				"category":{
					"id": category,
					"name": "",
				},
				"state": productE["state"],
				"user": {
					"id": session["user"]["id"]
				}
			}

			headers = {'Content-type': 'application/json'}
			url = api + "/products/update"
			resp = requests.post(url, data=json.dumps(product), headers=headers)

			return redirect(url_for("myProducts"))

	else:
		return(redirect(url_for("index")))


@app.route("/myShopping", methods = ["GET", "POST"])
def myShopping():
	url = api + "/invoices/getInvoicesByUserId/" + str(session["user"]["id"])
	shopping = requests.get(url).json()
	return render_template("myShopping.html", shopping = shopping)



@app.route("/checkout", methods = ["GET", "POST"])
def checkout():
	
	if not "user" in session:
		return redirect(url_for("shop")) 

	if request.method == "GET":
		url = api + "/shoppingCarts/byUserId/" + str(session["user"]["id"])
		shoppingCart = requests.get(url).json()
		if len(shoppingCart["shoppingCartProducts"]) == 0:
			return redirect(url_for("shop"))
		subtotal = 0
		for product in shoppingCart["shoppingCartProducts"]:
			subtotal += product["product"]["price"] * product["amount"]
		total = subtotal + (subtotal*0.19)
		url = api + "/paymentMethods"
		paymentMethods = requests.get(url).json()
		return render_template("checkout.html", shoppingCart = shoppingCart, subtotal = subtotal, total = total, paymentMethods = paymentMethods)
	else:
		cc = request.form["cedula"]
		payment = request.form["payment"]
		invoice = {
			"date": "",
			"customerDocument": cc,
			"subTotal": 0,
			"total": 0,
			"user":{
				"id": session["user"]["id"]
			},
			"paymentMethod": {
				"id": payment
			},
			"state": {
				"id" : 1
			}
		}

		url = api + "/invoices/save"
		headers = {'Content-type': 'application/json'}
		resp = requests.post(url, data=json.dumps(invoice), headers=headers).json()
		return redirect(url_for("purchaseSummary", id = resp["id"]))
		

@app.route("/purchaseSummary/<id>")
def purchaseSummary(id):
	url = api + "/invoices/getInvoiceById/" + str(id)
	invoice = requests.get(url).json()
	if (invoice["user"]["id"] == session["user"]["id"]):
		return render_template("purchaseSummary.html", invoice = invoice)
	else:
		return(redirect(url_for("index")))
	

@app.route("/payInvoice/<id>")
def payInvoice(id):
	url = api + "/invoices/payInvoice/" + str(id)
	invoice = requests.get(url) 
	return redirect(url_for("purchaseSummary", id = id))

@app.route("/cancelInvoice/<id>")
def cancelInvoice(id):
	url = api + "/invoices/cancelInvoice/" + str(id)
	invoice = requests.get(url)
	return redirect(url_for("purchaseSummary", id = id))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


app.run()











