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
