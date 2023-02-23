#!/usr/bin/env python3
from zoodb import *

import time

from zoodb import *

import hashlib
import random

import bank
import rpclib
import sys
from debug import *
from bank import *


class BankRpcServer(rpclib.RpcServer):
    def rpc_transfer(self, **kwargs):
        sender, recipient, zoobars, token = kwargs["sender"], kwargs["recipient"], kwargs["zoobars"], kwargs["token"]
        return transfer(sender, recipient, zoobars, token)

    def rpc_balance(self, **kwargs):
        username = kwargs["username"]
        return balance(username)

    def rpc_create_account(self, **kwargs):
        username = kwargs["username"]
        return create_account(username)


    def rpc_get_log(self, **kwargs):
        username = kwargs["username"]
        return get_log(username)


(_, dummy_zookld_fd, sockpath) = sys.argv
print(("Bank server starting up on %s and zookld fd %s" % (sockpath, dummy_zookld_fd)))


s = BankRpcServer()
s.run_sockpath_fork(sockpath)
