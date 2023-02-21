# 2.2.2. Password Hashing and Salting

Implement password hashing and salting in the authentication service.
* Extending the cred table to include a salt column.
* modify register and login functions to use the salt column.
* store the salt in the database and use it to hash the password before storing it in the database.
