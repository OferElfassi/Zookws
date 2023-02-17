# 2.1 privilege separation

Two aspects make privilege separation challenging in the real world and in this lab. First,
privilege separation requires to take apart the application and split it up in separate
pieces.  Second, ensure that each piece runs with minimal privileges, which
requires setting permissions precisely and configuring the pieces correctly.

![image](https://user-images.githubusercontent.com/13490629/219546840-b4d3f292-1c18-4baf-8209-86a72eeaccee.png)

### Part 1 - Prepare the environment

* Create jail directory
* Create virtual environment for the web server python code in the jail directory
* Install the required python packages in the virtual environment
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

* Activate the virtual environment
* Run the web server loader executable zookld which is the only executable that runs with root privileges and located out of jail directory
* then the zookld will load the web server executable zookd and zookhttp processes by attaching each process to new forked chrooted jail process

```shell
cd project/directory
sudo ./zookld 8080
```
