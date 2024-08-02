Python version 3.10   
$cd to repo folder.   
$pip install -r requirements.txt   
Install mysql server, write credentials to the .env file(Can use the .env-dummy for reference.)   
Can use the sql dump provided on main branch to create the database.   
$mysql -u username -p database_name < myapp.sql   
Create strong random strings for password salt and jwt secret key.   
This is a clone of flaskforum's api part, written in fastAPI,written mainly for it to autocreate docs :)    
You can visit https://serdarbisgin.com.tr/docs to see it in action, though when my credits end, it will die :/   