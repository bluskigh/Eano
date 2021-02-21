const form = document.querySelector("form");
const formButton = document.querySelector("form button");
const inputs = document.querySelectorAll("form input");
const warn = document.querySelector("#warnUser");
const mainSection = document.querySelector("#encapsulation");
const agree = document.querySelector("[name=agree]");

const info = document.querySelector("#info");
const infoP = document.querySelector("#info #infoHeader p");
const infoDiv = document.querySelector("#info div");

const no = document.querySelector("[name=no]");
const yes = document.querySelector("[name=yes]");

function makeDanger()
{
    const classes = infoDiv.getAttribute("class");
    if (classes.indexOf("alert-danger") == -1)
    {
        // not present, so make it present
        infoDiv.classList.toggle("alert-danger");
    }

    // check if success is in there
    if (classes.indexOf("alert-success"))
    {
        // remove it, so danger can aspire
        infoDiv.classList.toggle("alert-success");
    }
}

function makeSuccess()
{
    const classes = infoDiv.getAttribute("class");
    // check if success is already set
    if (classes.indexOf("alert-success") == -1)
    {
        // add it
        infoDiv.classList.toggle("alert-success");
    }
    // check if danger is already in there
    if (classes.indexOf("alert-danger"))
    {
        // remove it
        infoDiv.classList.toggle("alert-danger");
    }
}
function removeAll()
{
    const classes = infoDiv.getAttribute("class");
    if (classes.indexOf("alert-danger"))
    {
        // remove danger
        infoDiv.classList.toggle("alert-danger");
    }
    if (classes.indexOf("alert-success"))
    {
        // removing success
        infoDiv.classList.toggle("alert-success");
    }
}

function infoActions()
{
    info.classList.toggle("warnHidden");
    setTimeout(()=>{
        info.classList.toggle("warnHidden");
        infoP.innerText = "";
        removeAll();
    }, 4000);
}

function actionEverything(d)
{
    for (const input of inputs)
    {
        if (d == false)
        {
            input.value = "";
        }
        input.disabled = d;
    }
    formButton.disabled = d;

    agree.value = "";
}

form.addEventListener("submit", function(e){
    e.preventDefault();
    // make the type in i agree
    warn.classList.toggle("warnHidden");
    mainSection.classList.toggle("highlighted");
    // disable inputs and button
    actionEverything(true);
});

no.addEventListener("click", function(){
    // do not do anything, and just reenable everything, clear inputs
    // clear inputs
    actionEverything(false);

    // togle warn
    warn.classList.toggle("warnHidden");
    mainSection.classList.toggle("highlighted");

    infoP.innerText = "Did not configure anything.";
    makeDanger();
    infoActions();
});

yes.addEventListener("click", function(){
    // make sure that I agree was typed
    if (agree.value == "I agree.")
    {
        // if wants to update password, make sure the passwords match
        const password = document.querySelector("[name=password]");
        const confirmation = document.querySelector("[name=confirmation]");
        if (password.value)
        {
            if (password.value == confirmation.value)
            {
                // update the password, send request to the server
                fetch("/account",{
                    method: "POST",
                    headers: new Headers ({
                        "content-type":"application/json"
                    }),
                    body: JSON.stringify({
                        "password":password.value,
                        "confirmation":confirmation.value,
                    })
                })
                .then((r)=>{
                    return r;
                })
                .then((r)=>{
                    if (r.status == 501)
                    {
                        // passwords are the same
                        infoP.innerText += "New password is the same as old password.\n"
                        makeDanger();
                    }
                    else
                    {
                        infoP.innerText += "Configured Password\n";
                        makeSuccess();
                    }
                })
                .catch((e)=>{
                    console.log(e)
                    console.log("Error occurred inside of fetch /account");
                });
            }
            else
            {
                infoP.innerText = "Confirmation does not match new password.\n"
                makeDanger();
            }
        }

        const username = document.querySelector("[name=username]");
        // update the username next
        if (username.value)
        {
            fetch("/account", {
                method: "POST",
                headers: new Headers ({
                    "content-type":"application/json"
                }),
                body: JSON.stringify({
                    "username":username.value
                })
            })
            .then((r)=>{
                return r;
            })
            .then((r)=>{
                if (r.status == 501)
                {
                    infoP.innerText += "New username is same as current\n";
                    makeDanger();
                }
                else if (r.status == 409)
                {
                    infoP.innerText += "Username already taken, choose another one.\n";
                    makeDanger();
                }
                else
                {
                    infoP.innerText += "Configured Username\n";
                    makeSuccess();
                }
            })
            .catch((e)=>{
                console.log("There was an error inside of /account for username")
            });
        }
    }
    else
    {
        // make the p in the div equal to this
        infoP.innerText = 'Did not enter "I agree." / Nothing was changed.'
        makeDanger();
    }

    // reactivate the inputs and buttons
    actionEverything(false);

    infoActions();

    // hide the warn
    warn.classList.toggle("warnHidden");
    mainSection.classList.toggle("highlighted");
});