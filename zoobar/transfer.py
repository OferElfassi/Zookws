from flask import g, render_template, request

from login import requirelogin
from zoodb import *
from debug import *
import traceback
import bank_client


@catch_err
@requirelogin
def transfer():
    warning = None
    try:
        if 'recipient' in request.form:
            zoobars = 0
            if request.form['zoobars'].isnumeric():
                zoobars = eval(request.form['zoobars'])
            res = bank_client.transfer(g.user.person.username,request.form['recipient'], zoobars, g.user.token)
            warning = "%s" % res
    except (KeyError, ValueError, AttributeError) as e:
        traceback.print_exc()
        warning = "Transfer to %s failed" % request.form['recipient']

    return render_template('transfer.html', warning=warning)

