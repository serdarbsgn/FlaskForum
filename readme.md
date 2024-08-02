Python version 3.10  
$cd to repo folder.  
$pip install -r requirements.txt  
Install mysql server, write credentials to the .env file(Can use the .env-dummy for reference.)  
Can use the sql dump provided to create the database.  
$mysql -u username -p database_name < myapp.sql  
If you wish to use google and facebook oauth features, need to obtain their client id's and passwords from developer console.  
Create strong random strings for password salt and jwt secret key.  
Working with UI's are not my favourite pastime so it's pretty barebone.  
You can visit https://serdarbisgin.com.tr/ to see it in action, though when my credits end, it will die :/  
