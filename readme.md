# 2.1 privilege separation

Privilege separation challenges: first, requires to take apart the application and split it up in separate
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
cd jail/directory
source venv/bin/activate
cd project/directory
sudo ./zookld 8080
```

### Part 3 - Test code injection exploit

* Run the web server with zookld-exstack executable which execute the http service tht compiled with executable stack (zookhttp-exstack)
* Run the exploit-template2.py

```shell
cd jail/directory
source venv/bin/activate
cd project/directory
sudo ./zookld-exstack 8080
```

![image](https://user-images.githubusercontent.com/13490629/219696223-483cc4a1-a10a-46b4-bc65-aeb796c2d1d5.png)