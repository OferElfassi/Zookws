from debug import *
from zoodb import *
import rpclib


def transfer(sender, recipient, zoobars, token):
    with rpclib.client_connect('/banksvc/sock') as c:
        kwargs = {"sender": sender, "recipient": recipient, "zoobars": zoobars, "token": token}
        ret = c.call('transfer', **kwargs)
        return ret


def balance(username):
    with rpclib.client_connect('/banksvc/sock') as c:
        kwargs = {"username": username}
        ret = c.call('balance', **kwargs)
        return ret


def create_account(username):
    with rpclib.client_connect('/banksvc/sock') as c:
        kwargs = {"username": username}
        ret = c.call('create_account', **kwargs)
        return ret


def get_log(username):
    with rpclib.client_connect('/banksvc/sock') as c:
        kwargs = {"username": username}
        ret = c.call('get_log', **kwargs)
        return ret
