const cart = document.getElementById("cart");
const valueCart = document.getElementById("valueCart");
let time = 2000;
let timer = time;

const ipBack = localStorage.getItem("ipBack");


if (ipBack) {

}else{
	localStorage.setItem("ipBack", prompt("Join local ip"));
	window.location.reload();	
}


async function getUser(){
	try{
		const response = await fetch("/userInSession");
		if(!response.ok){
			throw new Error(message);
		}
		const data = await response.json();
		return data;
	}catch(error){
		console.log(error);
	}
}

async function getCart() {
	const userId = await getUser();
	if(userId != null){
		try {
			const response = await fetch("http://" + ipBack + ":8080/api/shoppingCarts/byUserId/" + userId)
			if (!response.ok) {
				throw new Error(message);
			}			
			const data = await response.json();			
			return data
		} catch(e) {
			console.log(e);
			return null;
		}
	}
}

function getImageLink(imageName){
	return fetch("/getImageLink/" + imageName)
	.then(response => response.json())
	.then(data => {
		result = data;
	})
	.catch(error => console.error(error));
}



function dropCart(){
	cart.innerHTML = "";
}

async function updateTotalCart(){
	let totalCart = 0;
	const cartProducts = await getCart();
	let totalProductos = cartProducts.shoppingCartProducts.length;
	let productosCargados = 0;
	cartProducts.shoppingCartProducts.forEach(detailCart => {
		totalCart += detailCart.amount * detailCart.product.price;
		valueCart.textContent = totalCart;
	});
}


async function loadCart(){
	const cartProducts = await getCart();
	
	cartProducts.shoppingCartProducts.forEach(detailCart => {
		
		let imageURL = "";
		let idAddBtn = "add-" + detailCart.id;
		let idRemoveBtn = "remove-" + detailCart.id;
		let idRemoveProductBtn = "remove-product-" + detailCart.id;

		getImageLink(detailCart.product.picture).then(() => {
			imageURL = result.url;
			let deiabledR = "disabled";
			let deiabledA = "disabled";
			if (detailCart.amount > 1)
				deiabledR = "";
			if (detailCart.amount < detailCart.product.quantity)
				deiabledA = "";
			const productCard = document.createElement("div");
			productCard.classList.add("card", "border-3", "mb-3");
			productCard.id =  "detailCart-" + detailCart.id;
			let productCardBody = `
			<div class="card-header">
			<div class="row">
			<div class="col-11">
			<p>${detailCart.product.name}</p>
			</div>
			<div class="col-1 d-flex justify-content-center">
			<button class="btn-close btn-remove-product" id="${idRemoveProductBtn}"></button>
			</div>
			</div>
			</div>
			<div class="card-body">
			<div class="row">
			<div class="col-3">
			<img class="card-img-top" src="${imageURL}" onerror='this.src="/static/uploads/${detailCart.product.picture}"'  style="width:100%;" alt="${detailCart.product.name}">
			</div>
			<div class="col-9 h-100">
			<div class="row">
			<div class="col-7 m-auto">
			<div class="input-group" role="group">
			<button type="button" class="btn btn-outline-dark btn-remove" ${deiabledR} id="${idRemoveBtn}"><i class="bi bi-dash-lg"></i></button>
			<span class="py-2 border border-1 text-center" style="border-color:black !important; width: 35px;" id="amount-${detailCart.id}">${detailCart.amount}</span>
			<button type="button" class="btn btn-outline-dark btn-add" ${deiabledA} id="${idAddBtn}" ><i class="bi bi-plus-lg"></i></button>
			</div>
			<small class="mt-2">Disponible: ${detailCart.product.quantity}</small>
			</div>
			<div class="col-5">
			<p class="fs-5 my-auto text-end">$ ${detailCart.product.price}</p>
			</div>
			</div>
			</div>
			</div>
			</div>
			`;
			productCard.innerHTML = productCardBody;
			cart.appendChild(productCard);

			document.getElementById(idAddBtn).addEventListener("click", addAmount);
			document.getElementById(idRemoveBtn).addEventListener("click", removeAmount);
			document.getElementById(idRemoveProductBtn).addEventListener("click", removeProduct);
		});

	});

}

(function(){

	const addProductButtons = document.getElementsByClassName("btn-add-product");
	for(button of addProductButtons){
		button.addEventListener("click", addProduct);
	}
	const addProductButtons2 = document.getElementsByClassName("btn-add-product2");
	for(button of addProductButtons2){
		button.addEventListener("click", addProduct2);
	}


	loadCart();

})();

let addAmountTimeout;


async function addAmount(event){
	updateAmount(event.srcElement, 1);
}

async function removeAmount(event){
	updateAmount(event.srcElement, -1);
}


function getMaxFromCard(button){
	let realButton = button;
	button.tagName == "I" ? realButton = button.parentElement : null;
	return realButton.parentElement.parentElement.children[1].textContent.split(" ")[1];
}

function updateAmount(button, value){
	
	const card = goToCard(button);
	const detailCartId = parseInt(card.id.split("-")[1]);
	const amount = document.getElementById("amount-" + detailCartId);

	let btnGroup = button.parentElement;
	if(btnGroup.tagName == "BUTTON"){
		btnGroup = btnGroup.parentElement;
	}
	for(element of btnGroup.children){
		if (element.classList.contains("btn-remove")) {
			if(parseInt(amount.textContent) + value == 1){
				button.disabled = true;
			}else{
				element.disabled = false;
			}
		}

		if(element.classList.contains("btn-add")){
			if(parseInt(amount.textContent) + value == getMaxFromCard(button)){
				element.disabled = true;
			}else{
				element.disabled = false;
			}
		}
	}

	
	if(parseInt(amount.textContent) + value > 0){
		amount.textContent = parseInt(amount.textContent) + value;
		if(addAmountTimeout){
			clearTimeout(addAmountTimeout);
		}
		addAmountTimeout = setTimeout(()=>{
			let url = "http://" + ipBack + ":8080/api/shoppingCarts/updateAmount/" + detailCartId + "/" + amount.textContent;

			sendFetch(url).then(data => {
				amount.textContent = data;
				if(amount.textContent == 0){
					card.remove();
				}
			});
			
			addAmountTimeout = null;
		}, 1000);
	}

}	


function sendFetch(url){
	return fetch(url).then(response => {
		return response.json();
	}).then(data => {
		return data;
	})
}


function removeProduct(event){
	const card = goToCard(event.srcElement);
	const detailCartId = parseInt(card.id.split("-")[1]);
	fetch("http://" + ipBack + ":8080/api/shoppingCarts/deleteProduct/" + detailCartId , {method: 'DELETE'}).then(response => {
		if (response.ok) {
			card.remove();
		}
	});
}

function goToCard(origin){
	if (origin.classList.contains("card")) {
		return origin;
	}else{
		return goToCard(origin.parentElement);
	}
}



async function addProduct(event) {

	const userId = await getUser();
	const card = goToCard(event.srcElement);
	const productId = parseInt(card.id.split("-")[1]);
	const amount = 1;
	try {
		const params = new URLSearchParams();
		params.append('userId', userId);
		params.append('productId', productId);
		params.append('amount', amount);

		const response = await fetch("http://" + ipBack + ":8080/api/shoppingCarts/addProduct", {
			method: "POST",
			headers: {
				"Content-Type": "application/x-www-form-urlencoded"
			},
			body: params
		});

		if (!response.ok) {
			throw new Error("Error en la solicitud");
		}

		const data = await response.json();
		const toastLiveExample = document.getElementById('liveToast')

		const toast = new bootstrap.Toast(toastLiveExample)

		toast.show()
		dropCart();
		loadCart();
		return data;
	} catch (error) {
		console.log(error);
	}

}



async function addProduct2(event) {

	const userId = await getUser();
	const productId = event.srcElement.id;
	const amount = 1;
	try {
		const params = new URLSearchParams();
		params.append('userId', userId);
		params.append('productId', productId);
		params.append('amount', amount);

		const response = await fetch("http://" + ipBack + ":8080/api/shoppingCarts/addProduct", {
			method: "POST",
			headers: {
				"Content-Type": "application/x-www-form-urlencoded"
			},
			body: params
		});

		if (!response.ok) {
			throw new Error("Error en la solicitud");
		}

		const data = await response.json();
		const toastLiveExample = document.getElementById('liveToast')

		const toast = new bootstrap.Toast(toastLiveExample)

		toast.show()
		dropCart();
		loadCart();
		return data;
	} catch (error) {
		console.log(error);
	}

}
