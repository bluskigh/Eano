const aboutImage = document.querySelector("#about img");

const contactBlinkers = document.querySelectorAll(".input span[name=blinker]");
console.log(contactBlinkers);

const getRandom = ()=>{
    return parseInt(Math.random() * 255) + 100;
};

const inputs = document.querySelectorAll("span[role=textbox]");
for (const input of inputs)
{
    input.addEventListener("click", function(){
        // stop all other cursors from blinking
        // make current one blink

        const blinker = this.parentElement.children[2];

        // turn off all other blinkers
        for (const b of contactBlinkers)
        {
            if (b.classList.contains("blink"))
            {
                if (b.classList.contains("hidden"))
                {
                    b.classList.toggle("hidden");
                }
                console.log("true")
                // remove ikt
                b.classList.toggle("blink");
            }
        }

        if (blinker.classList.contains("blink") == false)
        {
            // not found, add it
            blinker.classList.toggle("blink");
        }

    })
}

const blink = ()=>{
    setTimeout(()=>{
        const blinkers = document.querySelectorAll(".blink");
        for (const blinker of blinkers)
        {
            blinker.classList.toggle("hidden");
        }
        blink();
    }, 500);
};
blink();