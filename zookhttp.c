#include "http.h"
#include <err.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#define DBG_ON 1
#define DBG_COLOR CYAN
#define LOG(...) log_msg(TIME_NOW(),__FILE__, __func__, __LINE__,DBG_COLOR,DBG_ON,MSG,__VA_ARGS__);

void zooksvc(int);

int main(int argc, char **argv)
{
    LOG("zookhttp is on\n");

    int fd;
    if (argc < 2 )
        LOG_ERROR("Wrong arguments");
    fd = strToInt(argv[1]);
    signal(SIGPIPE, SIG_IGN);
    signal(SIGCHLD, SIG_IGN);


    for(;;) {
        char envp[8192];
        int sockfd = -1;
        pid_t pid;
        const char *errmsg;

        /* receive socket and envp from zookd */
        if ((recvfd(fd, envp, sizeof(envp), &sockfd) <= 0) || sockfd < 0)
            LOG_ERROR("recvfd");

        switch (fork())
        {
            case -1:
                err(1, "fork");
            case 0:  /* child */
                env_deserialize(envp, sizeof(envp));
                if ((errmsg = http_request_headers(sockfd)))
                    http_err(sockfd, 500, "http_request_headers: %s", errmsg);
                else
                    http_serve(sockfd, getenv("REQUEST_URI"));
                return 0;
            default: /* parent */
                close(sockfd);
                break;
        }
    }

}

