#include "http.h"


enum svc_indexes {ZOOKD,HTTP_SVC,AUTH_SVC};
SVCS svcs[] = {
        {"zookd",  "zookd",  "0", "0", "0"},
        {"zookhttp","httpsvc","0", "0", "0"},
        {"authsvc/sock","zoobar/auth-server.py","0", "0", "0"},
};