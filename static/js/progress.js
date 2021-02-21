const undoButtons = document.querySelectorAll(".undo");
const no = document.querySelector("[name=no]");
const yes = document.querySelector("[name=yes]");
let undoWell = document.querySelector("#undoWell");
console.log(undoWell);
let success = document.querySelector("#undoWell div");

let info = null;
const quote = document.querySelector("#quote");
const author = document.querySelector("blockquote");
const generate = document.querySelector("#generateQuote");

function generateQuote()
{
  fetch("https://type.fit/api/quotes")
    .then(function(response) {
      return response.json();
    })
    .then(function(data) {
      let randomNumber = Math.floor(Math.random() * data.length);
      quote.innerText = '"' + data[randomNumber]["text"] + '"';
      author.innerText = data[randomNumber]["author"];
    });
}

// generate a quote on load
generateQuote();

generate.addEventListener("click", function(){
  generateQuote();
});

function afterDecision(button, undoButton)
{
  // toggling the class hdiden on the error section
  button.parentElement.parentElement.parentElement.classList.toggle("hidden");
  // removing the row from the table
  undoButton.parentElement.parentElement.parentElement.removeChild(undoButton.parentElement.parentElement);
  // reactivate all the buttons
  for (let bu of  document.querySelectorAll(".undo"))
  {
    bu.disabled = false;
  }

}

function displaySuccess(message)
{
    success.innerHTML = "<b>" + message + "</b> successfully!"
    undoWell.classList.toggle("hidden");
    setTimeout(()=>{
      // hide it again
      undoWell.classList.toggle("hidden");
    }, 1200);
}

for (const button of undoButtons)
{
  button.addEventListener("click", function(){
    const parentTr = this.parentElement.parentElement.children;

    let checked = 0;
    if (parentTr.isChecked.children[0].getAttribute("id") == "checked")
    {
      checked = 1;
    }

    info = {
      folderId: parentTr.folderId.innerText,
      historyId: parentTr.historyId.innerText,
      day: parentTr.day.innerText,
      folderTitle: parentTr.folderTitle.innerText,
      title: parentTr.title.innerText,
      desc: parentTr.desc.innerText,
      priority: parentTr.priority.innerText,
      isChecked: checked
    };

    // disable all buttons until a choice is made
    for (const b of undoButtons)
    {
      b.disabled = true;
    }

    // make background of note stand out
    this.parentElement.parentElement.classList.toggle("selected");

    let current = this;

    fetch("/undo", {
      method: "POST",
      headers: new Headers ({
        "content-type":"application/json"
      }),
      body: JSON.stringify(info)
    })
    .then((r)=>{
      if (r.statusText == 'NOT IMPLEMENTED')
      {
        // show some visual queue to the user that it went well.
        document.querySelector("#error").classList.toggle("hidden");
        elzsdf = info;

        yes.addEventListener("click", function(){
          // reactivate the buttons
          fetch("/undo", {
            method: "POST",
            headers: new Headers ({
              "content-type": "application/json"
            }),
            body: JSON.stringify({
              "addFolder":true,
              "data":info
            })
          })
          .then((r)=>{
            afterDecision(this, current);
            displaySuccess("CREATED FOLDER / UNDO TODO");
          })
          .catch((e)=>{
            console.log("error occurred inside the 'yes' event listener fetch");
          });
        });
        no.addEventListener("click", function(){
          // reactivate the buttons

          fetch("/undo",
          {
            method: "POST",
            headers: new Headers ({
              "content-type":"application/json"
            }),
            body: JSON.stringify({
              "delete":true,
              "data":info
            })
          })
          .then((r)=>{
            // reveal it
            displaySuccess("REMOVED");
            afterDecision(this, current);
          })
          .catch((e)=>{
            console.log("Error occurred inside the no event listener");
          });
        });

      }
      else
      {
        // remove the page itself
        this.parentElement.parentElement.parentElement.removeChild(this.parentElement.parentElement);
        for (const z of undoButtons)
        {
          z.disabled = false;
        }
        displaySuccess("UNDO");
      }
    })
    .catch((e)=>{
      alert("Somethignw ent wrong");
    });

  });
}
