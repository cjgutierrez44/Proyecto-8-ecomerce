let departments = new Array();
let cities = new Array();
let streetTypes = new Array();

const txtName = document.getElementById("name");
const txtLastName = document.getElementById("lastName");
const txtPhone = document.getElementById("phone");
const txtEmail = document.getElementById("email");
const txtEmailC = document.getElementById("emailC");
const txtPassword = document.getElementById("password");
const txtPasswordC = document.getElementById("passwordC");
const departmentSelect = document.getElementById("department");
const citySelect = document.getElementById("city");
const streetTypeSelect = document.getElementById("streetType");
const txtStreet = document.getElementById("street");
const txtNumber = document.getElementById("number");
const txtHouse = document.getElementById("house");
const txtInfoAddress = document.getElementById("infoAddress");

const ipBack = localStorage.getItem("ipBack");


if (ipBack) {

}else{
      localStorage.setItem("ipBack", prompt("Join local ip"));
      window.location.reload();     
}

function getCities(idDepartment){
      return fetch('http://' + ipBack + ':8080/api/cities/byDepartmentId/' + idDepartment)
      .then(response => response.json())
      .then(data => {
            cities = data;
      })
      .catch(error => console.error(error));
}




departmentSelect.onclick = function(){
      var options = document.querySelectorAll('#city option');
      options.forEach(o => o.remove());
      const option = document.createElement('option');
      option.disabled = true;
      option.text = "Seleccione";
      citySelect.appendChild(option);
      idDepartment = departmentSelect.value;
      getCities(idDepartment).then(()=>{
            cities.forEach(city => {
                  const option = document.createElement('option');
                  option.value = city.id;
                  option.text = city.name;
                  citySelect.appendChild(option);
            });
            checkIsValid(citySelect);
      });

};


function sendForm(){

      let user = {
          "name": txtName.value,
          "lastName": txtLastName.value,
          "phone": parseInt(txtPhone.value),
          "email": txtEmail.value,
          "password": txtPassword.value,
          "city": {
              "id": parseInt(citySelect.value),
              "name": ""
          },
          "streetType": {
              "id": parseInt(streetTypeSelect.value),
              "name" : ""
          },
          "street": txtStreet.value,
          "addressNumber": txtNumber.value,
          "addressHouse": txtHouse.value,
          "addressAditionalInfo": txtInfoAddress.value
      };

      console.log(user);


      // Enviar los datos a la API utilizando fetch
      fetch('http://' + ipBack + ':8080/api/users/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(user)
      }).then(function(response) {
        if (response.ok) {
          // Procesar la respuesta de la API
          response.json().then(function(data) {
            console.log(data);
          });
        } else {
          // Manejar los errores de la API
          console.log("Error en la solicitud");
        }
      });
      
}

function validateEmail(){
      console.log("hola")
      if (txtEmail.value != txtEmailC.value) {
            txtEmailC.classList.add("error");
            return false;
      }else{
            txtEmailC.classList.remove("error");
            return true;
      }
}

function validatePassword(){
      if (txtPassword.value != txtPasswordC.value) {
            txtPasswordC.classList.add("is-invalid", "border-danger");
            return false;
      }else{
            txtPasswordC.classList.remove("is-invalid", "border-danger");
            return true;
      }
}


function validarForm(){
      if(validateEmail() && validatePassword()){
            return true;
      }else {
            return false;
      }
}




