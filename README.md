## Frequent Listener 

Using the Fast Fourier Transform, songs get created into increasingly sized composite frequencies as the user tries to guess the song. 
Stores user stats including average score, accuracy, and times played in a SQLite database. 
Also stores song information such as every song used as well as average score per song. 
Has an admin side that controls the current song as well as the next songs in a weekly queue. 
Uses apis from both Youtube and Spotify to get song information and audio.


## User Side
Users are able to create an account that then gets stored in the database. These stores their scores from every game they have played, their total accuracy, and games played.
They user can play the song of the day by listening to the version of the song with the top 150 frequencies of the song. As they reveal more frequencies, their score goes down. 
Once they guessed, they can see a bar chart revealing their score for every song over all of their games. They will see if they were right or wrong and the correct song.

## Admin Side
On the admin side which requires a specific url and log in information to access the admin can queue up songs for the next 7 days, 
after the 7 days are over the songs get deleted from the database so that they don't take up too much space. The admin selects the song by using a spotify search api, 
the audio is extracted from youtube, and then the fourier transform is done so that the different compositions are created. The admin can select which songs are active if they don't 
like the current song as well as delete songs from the queue. 
