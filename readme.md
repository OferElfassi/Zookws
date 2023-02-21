# 2.2.1 privilege separating login service

The first step towards protecting passwords will be to create a service that deals with user passwords and cookies, so that only that service can access them directly, and the rest of the Zoobar application cannot. In particular, we want to separate the code that deals with user authentication (i.e., passwords and tokens) from the rest of the application code. The current zoobar application stores everything about the user (their profile, their zoobar balance, and authentication info) in the Person table (see zoodb.py). We want to move the authentication info out of the Person table into a separate Cred table (Cred stands for Credentials), and move the code that accesses this authentication information (i.e., auth.py) into a separate service.

![image](https://user-images.githubusercontent.com/13490629/220238481-f53ea767-d8d1-433c-82c9-09fad5567858.png)
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
