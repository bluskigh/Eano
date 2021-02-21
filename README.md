# EANO
#### Description:
An application that was created for ease of use when taking notes and or todos.
Created using the following technologies: Python, JS, SQLite3, FLask. You're
given the option to create a folder, which you can store notes in. Following the
creation, you can provide a specific folder type that classifies your newly created folder.
You can also provide a starting amount, which automatically generates X todos when the
folder is created... Giving you X starting templates of todos. You can track your
progress via the Progress tab, once hit you will see your progress every day.
The progress bar scales depending on the daily goal amount set (can update).
An option to view the history is available too, you can undo the todo, but complications
may occur. If you undo a to-do that was marked complete (checked) then it will deduce from
your progress!
Another cool feature is when you undo a todo which has a folder that no longer exists; you're
given the option to create the folder again and simply place the todo in the created folder.
You can also update your account via the account tab. A username/password change is available for
those who decide they are not satisfied with their current username/password.

### application.py
Contains most of the logic that goes behind EANO.
## First steps
At first, I found it difficult to implement a request from the browser to flask, so I decided to
reload the page everything by using a form that was submitted to "/destination" via POST.
This was of course, not the best approach as it could have been better to just make a fetch request
to the server. At the time I did not know that I could do such an action... So, a good portion of
# def main.py
contained inefficient code that was waiting to be changed.

### Complications
## Getting information from the "server".
This was a problem that was first encountered when getting the user to change his username/password in the
account section of the page. In order to make a good experience, you want to let the user know whether
or not we successfully updated his username/password. In order to do that, we cannot reload the page after
the user hits submit! So, I learned how to use fetch() via JS... I then made a fetch request to the server
which then responded and I properly alerted the user depending on the status that was sent back from the
server. **THIS** made my page much better and interactive, as it provided interaction between the user
and the server.
# I could use this knowledge for creating folders too!
Before I knew how to use fetch() I had to submit to the server via the form and reload the page, in return
putting valuable information in hidden input tag's **values**! So something like this *<input type="text" style="visibility: hidden" value="**INFORMATION HERE**">*
this was awful! Now that I know how to use fetch, there is no longer a need to store such valuable information
in input tags. Instead, I can process the response from the server in the script, and update the page properly!
**AND** I can also show interactivity without reloading the page every time the user wants to add a folder/todo...
While showing an alert such as **Succes! Added a folder** or if something went wrong **Error! That folder already exists**
which is great as the user is interacting with the website more.
## Sorting Todos!
This was also quite difficult... At first, I thought maybe I can just sort it via js alone, no need to make requests
to the server, but because of the way, I implemented the todos into HTML. I was not able to use just js for the sorting
mechanism :( Instead, I made a fetch request, found all the todos connected to the folder selected (for the current user of course)
and then returned back a list of indexes which was based on the array of objects that were sent through to the server.
The indexes sent back are sorted according to the option selected (desc, asc, title) and all I had to do in JS
is realign the given indexes. For example, *[2, 0, 5, 3, 1]* is a response from the server, in JS I then have an array of
the todos *[Object.todo1, Object.todo2, Object.todo3, Object.todo4, Object.todo5]* I loop through the response array, index 0
contains value 2, so index 0 of the object array should be switched with index 2 of the object array!
## Deciding what sorting algorithm to use?
As learned in the course, merge sort is very fast, but at what cost? So I decided to use **Binary Search** as I simplified
the number of things that are needed to sort via the introduction of folders. If folders did not exist then I would have to sort through
quite a lot of todos... But folders minimize everything, and so I decided to implement Binary Seach instead.

###Purpose
Help me learn how to use Flask, SQL, and Python together to create a simple web application.

# By Mario Molinito, 2021
