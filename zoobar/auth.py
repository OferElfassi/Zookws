import binascii

from zoodb import *
import secrets
from debug import *
import pbkdf2

import hashlib
import random
import bank_client
SALT_LEN = 25


def newtoken(db, cred):
    hashinput = "%s%.10f" % (cred.password, random.random())
    cred.token = hashlib.md5(hashinput.encode('utf-8')).hexdigest()
    db.commit()
    return cred.token


def login(username, password):
    db = cred_setup()
    cred = db.query(Cred).get(username)
    if not cred:
        return None
    if cred.password == pbkdf2.PBKDF2(password, cred.salt).hexread(32):
        return newtoken(db, cred)
    else:
        return None


def add_person(username):
    db = person_setup()
    person = db.query(Person).get(username)
    if person:
        return None
    newperson = Person()
    newperson.username = username
    db.add(newperson)
    db.commit()
    return newperson


def register(username, password):
    db = cred_setup()
    cred = db.query(Cred).get(username)
    if cred:
        return None
    newcred = Cred()
    newcred.salt = secrets.token_bytes(SALT_LEN)
    newcred.username = username
    newcred.password = password
    newcred.password = pbkdf2.PBKDF2(password, newcred.salt).hexread(32)
    db.add(newcred)
    db.commit()
    add_person(username)
    bank_client.create_account(username)
    return newtoken(db, newcred)


def check_token(username, token):
    db = cred_setup()
    cred = db.query(Cred).get(username)
    if cred and cred.token == token:
        return True
    else:
        return False