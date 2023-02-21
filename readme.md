# 2.3. privilege separating bank service

To improve the security of zoobar balances, the plan is similar to operations made on the authentication service: 
split the zoobar balance information into a separate Bank database, and set up a bank_svc service,
whose job it is to perform operations on the new Bank database and the existing Transfer database.
As long as only the bank_svc service can modify the Bank and Transfer database.
![image](https://user-images.githubusercontent.com/13490629/220483589-ac36ae9f-fc2a-45eb-b907-80167cc4e4b9.png)
### Part 1 - Prepare the environment

* Create jail directory
* compile the c code and check for required files and directories and copy them to the jail directory
* copy any required packages and environment variables to the jail directory
* change the owners and permissions of the jail directory properly

the setup.sh script will do all the above steps

```shell
cd project/directory
make all
sudo ./setup.sh
```

### Part 2 - Run the web server

* Run the web server loader executable zookld which is the only executable that runs with root privileges and located out of jail directory
* then the zookld will load the web server executable zookd, zookhttp and authsvc processes by attaching each process to new forked chrooted jail process

```shell
cd project/directory
sudo ./zookld 8080
```
<br>
<br>

#### alternative all the above steps can be done automatically by running the following command

```shell
cd project/directory
sudo ./launch.sh 8080 1
```
* the second argument is indicator if we want to start fresh jail or completely delete the jail directory and start fresh