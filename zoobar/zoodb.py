from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *
from datetime import datetime, timedelta
import os
import sys
from debug import *

PersonBase = declarative_base()
TransferBase = declarative_base()
FailedLoginBase = declarative_base()
CredBase = declarative_base()
BankBase = declarative_base()


class Person(PersonBase):
    __tablename__ = "person"
    username = Column(String(128), primary_key=True)
    profile = Column(String(5000), nullable=False, default="")

    # static methods
    @staticmethod
    def get_person(username):
        person_session = person_setup()
        person = person_session.query(Person).get(username)
        person_session.close()
        return person

    @staticmethod
    def add_person(username):
        person_session = person_setup()
        person = Person(username=username)
        person_session.add(person)
        person_session.commit()
        person_session.close()
        return person


class FailedLogin(CredBase):
    __tablename__ = 'failed_logins'

    id = Column(Integer, primary_key=True)
    cred_id = Column(String, ForeignKey('cred.username'))
    cred = relationship("Cred", back_populates="failed_logins")
    timestamp = Column(DateTime)

    # static methods
    @staticmethod
    def add_failed_attempt(cred):
        failed_login_session = failed_logins_setup()
        failed_login = FailedLogin(cred=cred, timestamp=datetime.now())
        failed_login_session.add(failed_login)
        failed_login_session.commit()
        failed_login_session.close()

    # static methods for querying # all failed attempts that happened in the last blocking_duration_minutes minutes
    @staticmethod
    def get_failed_attempts(cred, time_ref, blocking_duration_minutes):
        failed_login_session = failed_logins_setup()
        blocking_start_time = time_ref - timedelta(minutes=blocking_duration_minutes)
        res = failed_login_session.query(FailedLogin).filter_by(cred=cred).filter(
            FailedLogin.timestamp > blocking_start_time).all()
        failed_login_session.close()
        return res

    # static method for deleting array of failed login attempts
    @staticmethod
    def delete_failed_attempts(failed_attempts):
        failed_login_session = failed_logins_setup()
        for failed_attempt in failed_attempts:
            failed_login_session.delete(failed_attempt)
        failed_login_session.commit()
        failed_login_session.close()


class Cred(CredBase):
    __tablename__ = "cred"
    username = Column(String(128), primary_key=True)
    password = Column(String(128))
    token = Column(String(128))
    salt = Column(String(128))
    failed_logins = relationship("FailedLogin", back_populates="cred")

    # static methods
    @staticmethod
    def get_by_username(username):
        cred_session = cred_setup()
        res = cred_session.query(Cred).filter(Cred.username == username).first()
        cred_session.close()
        return res

    @staticmethod
    def add_cred(username, password, salt):
        cred_session = cred_setup()
        cred = Cred(username=username, password=password, salt=salt)
        cred_session.add(cred)
        cred_session.commit()
        cred_session.close()
        return cred

    @staticmethod
    def set_token_by_username(username, token):
        cred_session = cred_setup()
        cred = cred_session.query(Cred).filter(Cred.username == username).first()
        cred.token = token
        cred_session.commit()
        cred_session.close()
        return cred

    # instance methods

    # string representation of a cred instance
    def __str__(self):
        return f"Cred(username='{self.username}', password='{self.password}', token='{self.token}', salt='{self.salt}')"


class Transfer(TransferBase):
    __tablename__ = "transfer"
    id = Column(Integer, primary_key=True)
    sender = Column(String(128))
    recipient = Column(String(128))
    amount = Column(Integer)
    time = Column(String)


class Bank(BankBase):
    __tablename__ = "bank"
    username = Column(String(128), primary_key=True)
    zoobars = Column(Integer, nullable=False, default=10)


def dbsetup(name, db_base):
    thisdir = os.path.dirname(os.path.abspath(__file__))
    dbdir = os.path.join(thisdir, "db", name)
    if not os.path.exists(dbdir):
        os.makedirs(dbdir)
    dbfile = os.path.join(dbdir, "%s.db" % name)
    db_engine = create_engine('sqlite:///%s' % dbfile, isolation_level='SERIALIZABLE')
    db_base.metadata.create_all(db_engine)
    db_session = sessionmaker(bind=db_engine)
    return db_session()


def person_setup():
    return dbsetup("person", PersonBase)


def transfer_setup():
    return dbsetup("transfer", TransferBase)


def cred_setup():
    return dbsetup("cred", CredBase)


def bank_setup():
    return dbsetup("bank", BankBase)


def failed_logins_setup():
    return dbsetup("failed_logins", CredBase)


def user_exists(username):
    person_session = person_setup()
    return person_session.query(Person).filter(Person.username == username).first() is not None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(("Usage: %s [init-person|init-transfer]" % sys.argv[0]))
        exit(1)

    cmd = sys.argv[1]
    if cmd == 'init-person':
        person_setup()
    elif cmd == 'init-transfer':
        transfer_setup()
    elif cmd == 'init-cred':
        cred_setup()
    elif cmd == 'init-bank':
        bank_setup()
    elif cmd == 'init-failed_logins':
        failed_logins_setup()
    else:
        raise Exception("unknown command %s" % cmd)
