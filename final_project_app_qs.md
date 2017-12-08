# SI 364 - Final Project questions

## Overall

* **What's a one-two sentence description of what your app will do?**

My application is a playlist creator.  It will create playlists for people based on their favorite songs.  

## The Data

* **What data will your app use? From where will you get it? (e.g. scraping a site? what site? -- careful not to run it too much. An API? Which API?)**

My application is going to use the itunes API and I will get the documentation from the itunes website.  https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/

* **What data will a user need to enter into a form?**

A user will need to input their username and a song they want to search for in the form. 

* **How many fields will your form have? What's an example of some data user might enter into it?**

There will be 2-3 fields that the form will have and an example of something the user might put in is their username so carlymatz and their favorite song at the time so "Hard Day's Night" by the Beatles. 


* **After a user enters data into the form, what happens? Does that data help a user search for more data? Does that data get saved in a database? Does that determine what already-saved data the user should see?**

After a user enters their username and favorite song there will be another page that asks the user to choose from a list of playlists that seem similar to their interests.  Then, we would help the user create a playlist from their favorite songs and playlists they see.  The playlist will be from outlets that give the user the best possible playlist with their favorite songs. So the original data in the form helps the user get to the playlists page and then to their final playlist. All of the data is saved into a database to help determine the final playlist that will also be stored in a database. It should not determine what already-saved data the user is going to see. 

* **What models will you have in your application?**

Playlist
Songs 
Users

* **What fields will each model have?**

Each model will have fields for user_ids, usernames and song names. 

* **What uniqueness constraints will there be on each table? (e.g. can't add a song with the same title as an existing song)**

Since I am using itunes, songs and playlists, the constraints will be that you cannot add a song to a playlist that has the same title as another song.

* **What relationships will exist between the tables? What's a 1:many relationship between? What about a many:many relationship?**

The 1:many relationship will be one username to many playlists or the one playlist to many songs and the many:many relationship will be many songs to many playlists because multiple songs can be on each playlist. 

* **How many get_or_create functions will you need? In what order will you invoke them? Which one will need to invoke at least one of the others?**

There will be 3 get_or_create functions.

## The Pages

* **How many pages (routes) will your application have?**

There will be 4 pages (routes) to my application. 

* **How many different views will a user be able to see, NOT counting errors?**

The user will see 6 different views. 

* **Basically, what will a user see on each page / at each route? Will it change depending on something else -- e.g. they see a form if they haven't submitted anything, but they see a list of things if they have?**

On the first page, they are going to see a form.  On the second page they will see a list of playlists that matches the form.  On the last page they will see a playlist that matches the user's needs and wants.  If they have submitted the form the wrong way, there will be an error.  For example, if they forgot a field or a song was not found there would be an error.  

## Extras

* **Why might your application send email?**

My application would send an email to the user when the playlist was ready to listen. 

* **If you plan to have user accounts, what information will be specific to a user account? What can you only see if you're logged in? What will you see if you're not logged in -- anything?**

I have not decided yet if I want to have a user log-in. If I do decide to incorporate that with my application then I want there to be benefits for those that have accounts.  For example, users will have more information in their account pertaining to their favorite music and playlists based on what their preferences that they put in when making their account. 

* **What are your biggest concerns about the process of building this application?**

My biggest concern about this project is mastering the log-in portion.  



