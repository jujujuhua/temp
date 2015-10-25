# pa2_n5hyqyyzaor
Group Name:
Great Jinhao
  
Members:
Tingshuo Xu (xts): setup the database, setup the routes, show and upload image, pic pages 
Jinghao Ping(jinhping): SQL query, customized http 404 page, Login, Edit_Account Pages and Bonus 
Junhua Chen(cobbju): Album pages, new user login pages and set up email conn 

Details:
Create new_user page and login, login_base page and edit_account pages
Set session and authentication stuff
Connect sql and modify previous pages and finish public, private album view
Set the upload folder in album.py and albums.py to where you want to store your pictures.
If pictures do not display properly, check if the folder exists and pictures are in there.

Deploy:
pip install < requirement.txt

Extra:
I took 0 late days.

Bonus: 
1. When form is submitted in the New User page, send an e-mail message to the new user confirming his/her membership and redirect them to the logged in home page. (HINT: Check out flask-mail - Ask Josh for help.)

2. Ask the user if he/she has forgotten the password and if so, create a new password and e-mail it to them.
