const revealFolderButton = document.querySelector("#folders #addFolder");

const createFolder = document.querySelector(".createFolder");
const addFolderButton = document.querySelector(".createFolder #addButton");
const folderTypes = document.querySelectorAll(".createFolder ul li button");
const folderAlert = document.querySelector(".createFolder #folderAlert");
const alertDiv = document.querySelector(".createFolder div");
const folderInput = document.querySelector(".createFolder [name=foldername]");
const startAmount = document.querySelector(".createFolder [name=startAmount]");

const cancel = document.querySelectorAll(".cancel");
for (const button of cancel)
{
    button.addEventListener("click", function(){
        // make it hidden
        try
        {
            document.querySelector("#options").classList.toggle("hidden");
        }
        catch (error)
        {
            try
            {
                createFolder.classList.toggle("hidden");
                startAmount.value = 0;
            }
            catch(error)
            {
                console.log(error);
            }
        }
    });
}

let selected = null;

revealFolderButton.addEventListener("click", function(){
    createFolder.classList.toggle("hidden");
});

function removeSelected()
{
    if (selected)
    {
        selected.classList.toggle("selected");
    }
}

for (const type of folderTypes)
{
    type.addEventListener("click", function(){
        // remove any other folderType that has the selected class assigned to it, making the current selected the only oen with the selected class
        removeSelected();
        selected = this;
        this.classList.toggle("selected");
    });
}

function reveal()
{
    if (folderAlert.classList.contains("hidden"))
    {
        folderAlert.classList.toggle("hidden");
    }
}

function makeAlert(adding, removing)
{
    if (alertDiv.getAttribute("class").indexOf(removing) != -1)
    {
        alertDiv.classList.toggle(removing);
    }
    if (alertDiv.getAttribute("class").indexOf(adding) == -1)
    {
        alertDiv.classList.toggle(adding);
    }
}

function showAlert(wantSuccess, headerMessage, pMessage)
{
    if (wantSuccess)
    {
        makeAlert("alert-success", "alert-warning");
    }
    else
    {
        makeAlert("alert-warning", "alert-success");
    }

    folderAlert.children[0].children[0].innerText = headerMessage;
    alertP.innerText = pMessage;
    reveal();
}

const alertP = folderAlert.children[0].children[1];

addFolderButton.addEventListener("click", function(){
    if (folderInput.value)
    {
        if (selected)
        {
            fetch("/main", {
                method: "POST",
                headers: new Headers ({
                    "content-type":"application/json"
                }),
                body: JSON.stringify({
                    foldername: folderInput.value,
                    // TODO change this to a more efficient data type, such as an int, or id of the type in the database
                    folderType: selected.innerText,
                    startAmount: startAmount.value
                })
            })
            .then((r)=>{
                return r;
            })
            .then((r)=>{
                if (r.status == 200)
                {
                    // show success message
                    showAlert(true, "Success!", "Added \"" +  folderInput.value + "\" to your folders!");
                    setTimeout(()=>{
                        // hide the create folder
                        createFolder.classList.toggle("hidden");
                        document.location.href = "/main";
                    }, 1000)
                }
                else if (r.status == 401)
                {
                    // a folder with that name already exists, tell the user
                    showAlert(false, "Error!", "A folder with the name \"" + folderInput.value + "\" already exists.");
                }
                else if (r.status == 409)
                {
                    // let the user know that invalid keyword areguments were entered
                    showAlert(false, "Error!", "You trying to be sneaky? Please try again ;)");
                }
                else
                {
                    showAlert(false, "Error!", "Something went wrong :( Refresh and try again :D");
                    // if the user does not want to refresh then make him refresh.
                }
            })
            .catch((e)=>{
                console.log(e);
                showAlert(false, "Server Error!", "Refresh and try again please :)");
            });
        }
        else
        {
            showAlert(false, "Whoooops!", "Did not choose a folder type.");
        }
    }
    else
    {
        showAlert(false, "Oh no!", "You did not provide a folder title....");
    }
});

let updateForm = document.querySelector("#update");
if (updateForm)
{
    const title = document.querySelector("#update input");
    const titleDefault = title.value;
    const desc = document.querySelector("#update textarea");
    const descDefault = desc.value;
    const priority = document.querySelector("#update input:nth-child(2)");
    const priorityDefault = priority.value;

    updateForm.addEventListener("submit", function(e){
        if (titleDefault == title.value && descDefault == desc.value && priorityDefault == priority.value)
        {
            alert("You did not change anything.")
            e.preventDefault();
        }
        else
        {
            if (desc.value == descDefault)
            {
                desc.parentElement.removeChild(desc);
            }
            if (title.value == titleDefault)
            {
                title.parentElement.removeChild(title);
            }
            if (priority.value == priorityDefault)
            {
                priority.parentElement.removeChild(priority);
            }
        }
    });
}

const todoSections = Object.values(document.querySelectorAll(".wholeEncapsulation"));
let selector = document.querySelector("select");
selector.addEventListener("change", function(){
    console.log(this.value);
    // make a request to the server,
    fetch("/sort", {
        method: "POST",
        headers: new Headers ({
            "content-type":"application/json"
        }),
        body: JSON.stringify({
            option: this.value,
            folder: document.querySelector("#middleFolderTitle").innerText.split(":")[0]
        })
    })
    .then(async (r)=>{
        return await r.json();
    })
    .then((r)=>{
        switch (r)
        {
            case 409:
                console.log("Did not provide body");
                break
            case 401:
                console.log("Did not provide necessary information");
            default:
                console.log("Everything went well.");
                break;
        };
        let finalResult = [];
        const array = r["body"];
        for (const value of array)
        {
            // replace current index of value index
            finalResult.push(todoSections[value]);
        }
        // pop off everything in the current todo section, append the current list
        const notes = document.querySelector("#notes");
        for (const note of notes.children)
        {
            notes.removeChild(note);
        }
        // Problem, since, save the default order of the list
        for (const note of finalResult)
        {
            notes.appendChild(note);
        }
    })
    .catch((e)=>{
        console.log(e);
        alert("An error has occcured inside of sort change event listener....");
    });
});