/* dispatch daemon */

#include "http.h"
#include <err.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netdb.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <dirent.h>
#include <pwd.h>
#include <grp.h>
#define MINARGS 3
#define DBG_ON 1
#define DBG_COLOR MAGENTA
#define LOG(...) log_msg(TIME_NOW(),__FILE__, __func__, __LINE__,DBG_COLOR,DBG_ON,MSG,__VA_ARGS__);

static void process_client(int);

static int run_server(const char *port);

static int start_server(const char *portstr);

void parse_args(int argc, char **argv);
int sock_fd;
char *port;
int fd_count =-1;
int fds[32];
char *fd_names[32] = {0};

int main(int argc, char **argv) {

    LOG("zookd is on\n");
    parse_args(argc, argv);
    LOG("parsed args:\nport:%s \nfds:%s \nfd_names:%s",port, TO_STR(fds,fd_count),TO_STR(fd_names,fd_count));
//    LOG("Start delay");
//    delay(5000);
//    LOG("End delay");
    run_server(port);
}

/**
 * accept connections
 * @param port port to listen on
 */
static int run_server(const char *port) {
    int sockfd = start_server(port);
    LOG("Listening on port %s", port);

    for (;;) {
        int cltfd = accept(sockfd, NULL, NULL);
        if (cltfd < 0)
            err(1, "accept");
        process_client(cltfd);
        close(cltfd);
    }
}

/**
 * create http socket on port portstr provided by the args sent to zookd from zookld
 * @param portstr port to create socket on
 * @return socket file descriptor
 */
static int start_server(const char *portstr) {
    LOG("start_server on port %s", portstr);
    struct addrinfo hints = {0}, *res;
    int sockfd;
    int e, opt = 1;

    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;

    if ((e = getaddrinfo(NULL, portstr, &hints, &res)))
        LOG_ERROR("getaddrinfo: %s", gai_strerror(e));
    if ((sockfd = socket(res->ai_family, res->ai_socktype, res->ai_protocol)) < 0)
        LOG_ERROR("socket");
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)))
        LOG_ERROR("setsockopt");
    if (fcntl(sockfd, F_SETFD, FD_CLOEXEC) < 0)
        LOG_ERROR("fcntl");
    if (bind(sockfd, res->ai_addr, res->ai_addrlen))
        LOG_ERROR("bind");
    if (listen(sockfd, 5))
        LOG_ERROR("listen");
    freeaddrinfo(res);

    return sockfd;
}


/**
 * process client request
 * @param cltfd client socket
 */
static void process_client(int fd) {

    static char env[8192];
    static size_t env_len = 8192;
    char reqpath[4096];
    const char *errmsg;


    /* get the request line */
    if ((errmsg = http_request_line(fd, reqpath, env, &env_len)))
        return http_err(fd, 500, "http_request_line: %s", errmsg);

    LOG("reqpath: %s", reqpath);

    if (sendfd(fds[0], env, env_len, fd) < 0)
        LOG_ERROR("ERROR sendfd socket:%d, fd:%d", sock_fd, fds[0]);
}

/**
 * args for zookd: [exec, port, fdCount, ....[fd,fdName]...]
 * @param argc number of args
 * @param argv args
 */
void parse_args(int argc, char **argv) {
    LOG("parse_args");
    if (argc < MINARGS)
        LOG_ERROR("Wrong arguments");
    int fds_itr = 2;
    port =argv[1];
    fd_count = strToInt(argv[2]);
    for (int i = 0; i < fd_count; i++) {
        fds[i] = strToInt(argv[++fds_itr]);
        fd_names[i] = argv[++fds_itr];
    }
}

