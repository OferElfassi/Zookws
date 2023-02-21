from zoodb import *
from debug import *
import auth_client
import time


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


def balance(username):
    db = bank_setup()
    user_bank = db.query(Bank).get(username)
    if user_bank is None:
        return "User does not exist!"
    return user_bank.zoobars


def get_log(username):
    db = transfer_setup()
    l = db.query(Transfer).filter(or_(Transfer.sender == username, Transfer.recipient == username))
    r = []
    for t in l:
        r.append({'time': t.time,
                  'sender': t.sender,
                  'recipient': t.recipient,
                  'amount': t.amount})
    return r


def create_account(username):
    if not user_exists(username):
        return "User does not exist!"
    db = bank_setup()
    new_account = Bank()
    new_account.username = username
    db.add(new_account)
    db.commit()
    return "Account created."


def log_transfer(sender, recipient, zoobars):
    db = transfer_setup()
    new_transfer = Transfer()
    new_transfer.sender = sender
    new_transfer.recipient = recipient
    new_transfer.amount = zoobars
    new_transfer.time = time.asctime()
    db.add(new_transfer)
    db.commit()
    return "Transfer logged!"
