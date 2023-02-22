#!/usr/bin/env python3

from zoodb import *

import hashlib
import random

import rpclib
import sys
from debug import *
from auth import *


class AuthRpcServer(rpclib.RpcServer):

    def rpc_login(self, **kwargs):
        username, password = kwargs["username"], kwargs["password"]
        return login(username, password)

    def rpc_register(self, **kwargs):
        username, password = kwargs["username"], kwargs["password"]
        return register(username, password)

    def rpc_check_token(self, **kwargs):
        username, token = kwargs["username"], kwargs["token"]
        return check_token(username, token)


(_, dummy_zookld_fd, sockpath) = sys.argv
print(("Auth server starting up on %s and zookld fd %s" % (sockpath, dummy_zookld_fd)))

s = AuthRpcServer()
s.run_sockpath_fork(sockpath)
