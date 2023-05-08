    const validationRequired = document.getElementsByClassName("validate");	
    let radiosAnChecks = {};

    const head = document.getElementsByTagName("head")[0]
    const swalScript = document.createElement("script")
    swalScript.src = "/static/js/sweetalert2.js"
    head.appendChild(swalScript)

    const validationRequiredLinks = document.querySelectorAll("a.confirm");

    const confirmMessages = {
        "default": "Esta seguro de realizar esta acción?",
        "delete-product": "Está seguro de eliminar este producto?"
    }


    const patterns = {
        "default": /.*/,
        "validate-pattern-email": /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
        "validate-pattern-phone": /^\d{7,10}$/,
        "validate-pattern-personalID": /^\d{8,10}$/
    }

    function getPattern(name){
        let pattern = patterns["default"];
        if (name in patterns) {
            pattern = patterns[name];
        }
        
        return pattern;
    }


    function getConfirmMessage(link) {
        message = confirmMessages["default"];
        link.classList.forEach(classKey => {
            if(classKey in confirmMessages)
                message = confirmMessages[classKey];
        })
        return message;
    }

    validationRequiredLinks.forEach(link => {
        link.addEventListener("click", event=>{
            event.preventDefault();
            Swal.fire({
                icon: 'question',
                title: getConfirmMessage(link),
                showDenyButton: true,
                confirmButtonText: 'Si',
                confirmButtonColor: '#ff7851',
                denyButtonText: `No`,
                denyButtonColor: '#56cc9d',
          }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = link.href;
            }
        })
      });
    });


    function validate(){
        radiosAnChecks = {};
        let validInputs = 0;    
        for(let i = 0; i < validationRequired.length; i++){
            let children = validationRequired[i].childNodes;
            for(let j = 0; j  < children.length; j++){
                let element = children[j];
                if((element.tagName == "INPUT") || (element.tagName == "SELECT") || (element.tagName == "TEXTAREA")){
                    checkIsValid(element) ? validInputs++ : null;
                }
                if(element.tagName == "DIV" && element.classList.contains("form-check")){
                    let childrenCheck = element.childNodes;
                    element.onchange = ()=> checkRadiosAnChecks();
                    for(let k = 0; k < childrenCheck.length; k++){
                        if(childrenCheck[k].tagName == "INPUT" ){
                            radiosAnChecks[childrenCheck[k].name] != undefined ? radiosAnChecks[childrenCheck[k].name].push(childrenCheck[k]) : radiosAnChecks[childrenCheck[k].name] = [childrenCheck[k]];
                        }
                    }
                }
            }
        }
        validInputs += checkRadiosAnChecks();

        if (validInputs == validationRequired.length) {
            return true;
        }else {
            console.log("no puede mandar el formulario porque no ha completado todos los campos " + (validationRequired.length - validInputs));
            return false;
        }
        
    }
    function checkRadiosAnChecks(){
        let validChecks = 0;
        for(let key in radiosAnChecks){
            let isSelected = false;
            for(let i = 0; i < radiosAnChecks[key].length; i++){
                radiosAnChecks[key][i].checked == true ? isSelected = true : false;
            }
            for(let j = 0; j < radiosAnChecks[key].length; j++){
                isSelected ? radiosAnChecks[key][j].classList.remove("error") : radiosAnChecks[key][j].classList.add("error");
                let contenedor = radiosAnChecks[key][j].parentElement.parentElement;
                let children = contenedor.childNodes;
                for(let k = 0; k  < children.length; k++){ 
                    if(children[k].tagName == "DIV" && children[k].classList.contains("error-message") && !isSelected){
                        children[k].classList.add("d-block");
                    }else if((children[k].tagName == "DIV" && children[k].classList.contains("error-message")) && isSelected){
                        validChecks++;
                        children[k].classList.remove("d-block");
                    }
                }
            }
        }
        return validChecks;
    }
    function checkIsValid(element){
        let valid = false;
        element.onchange = ()=>{checkIsValid(element)};
        element.onkeyup = ()=>{checkIsValid(element)};
        let children = element.parentElement.childNodes;
        if(((element.tagName == "INPUT" || element.tagName == "TEXTAREA") && element.value == "") || (element.tagName == "SELECT" && element.selectedIndex == 0)){
            element.classList.add("error");
            for(let i = 0; i  < children.length; i++){ 
                if(children[i].tagName == "DIV" && children[i].classList.contains("error-message")){
                    children[i].classList.add("d-block");
                }
            }
            valid = false;
        }else if (((element.tagName == "INPUT" || element.tagName == "TEXTAREA") && element.value !="") || (element.tagName == "SELECT" && element.selectedIndex != 0)){
            element.classList.remove("error");
            for(let i = 0; i  < children.length; i++){ 
                if(children[i].tagName == "DIV" && children[i].classList.contains("error-message")){
                    children[i].classList.remove("d-block");     
                }
            }
            valid = true;
        }

        checkEqual(element) ? null : valid = false;
        checkRegEx(element) ? null : valid = false;

        return valid;
    }

    function checkEqual(element) {
        let ret = true;
     let pattern = /^validate-equal-.+$/;
     element.classList.forEach(class_=>{
        if(class_.match(pattern)){
            const validateEqual = document.getElementsByClassName(class_);
            value = validateEqual[0].value;
            for(input of validateEqual){
                if (input.value != value) {
                    input.classList.add("error");
                    const children = input.parentElement.childNodes;
                    for(let i = 0; i  < children.length; i++){ 
                        if(children[i].tagName == "DIV" && children[i].classList.contains("match-error-message")){
                            children[i].classList.add("d-block");     
                        }
                    }
                    ret = false;
                }else {
                    const children = input.parentElement.childNodes;
                    for(let i = 0; i  < children.length; i++){ 
                        if(children[i].tagName == "DIV" && children[i].classList.contains("match-error-message")){
                            children[i].classList.remove("d-block");     
                        }
                    }
                    ret = true;
                }
            }
        }
    });
    return ret;
    }



    function checkRegEx(element){
        ret = true;
        let pattern = /^validate-pattern-.+$/;
        element.classList.forEach(class_=>{
            if (class_.match(pattern)) {
                if (!element.value.match(getPattern(class_))) {
                    element.classList.add("error");
                    const children = element.parentElement.childNodes;
                    for(let i = 0; i  < children.length; i++){ 
                        if(children[i].tagName == "DIV" && children[i].classList.contains("pattern-error-message")){
                            children[i].classList.add("d-block");     
                        }
                    }
                    ret = false;
                }else{
                    const children = element.parentElement.childNodes;
                    for(let i = 0; i  < children.length; i++){ 
                        if(children[i].tagName == "DIV" && children[i].classList.contains("pattern-error-message")){
                            children[i].classList.remove("d-block");     
                        }
                    }
                    ret = true;
                }
            }
        });
        return ret;
    }