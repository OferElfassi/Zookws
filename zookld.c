#include <sys/types.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <grp.h>
#include <unistd.h>
#include <signal.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "http.h"

#define DBG_ON 1
#define LOG(...) log_msg(TIME_NOW(),__FILE__, __func__, __LINE__,BLUE,DBG_ON,MSG,__VA_ARGS__);

#define SVC_CNT 3
#define SHARED_GID "81111"
enum svc_indexes {ZOOKD,HTTP_SVC,AUTH_SVC};
SVCS svcs[SVC_CNT] = {
        {"zookd",  "zookd",  "-1", "-1", "-1","51001","51001"},
        {"zookhttp","httpsvc","-1", "-1", "-1","61001","61001"},
        {"authsvc/sock","zoobar/auth-server.py","-1", "-1", "-1","71001","71001"},
};


static pid_t launch_svc(int);

void handle_child_process();

void create_socket_pair();

void register_signal_handler();

void launch_child_processes();

int set_args(char *argv[], int service);

gid_t group_list[1];


struct sigaction sa;

char *PORT = "8080";

void print_cwd(){
    char cwd[1024];
    getcwd(cwd, sizeof(cwd));
    printf("Current working dir: %s\n", cwd);
}
int main(int argc, char **argv) {
    system("clear");
//    system("echo \"process details:\";pwd; echo \"UID: $UID\";echo \"GID: $(id -g)\";ls -la  ");
    char cwd[1024];
    print_cwd();

    group_list[0] = strToInt(SHARED_ID);
//    update_files();
    if (argc == 2)
        PORT = argv[1];
    create_socket_pair();
    register_signal_handler();
    launch_child_processes();

    pid_t pid;

    while ((pid = wait(NULL)) > 0) {
        for (int i = 0; i < SVC_CNT; i++) {
            if (strToInt(PATHS[i][PID]) == pid) {
                LOG("Process %s died, restarting", PATHS[i][NAME]);
                launch_svc(i);
                break;
            }
        }
    }
}

/**
 * Create a socket pairs and store the file descriptors in the config array
 */
void create_socket_pair() {
    int socketPair[2];
    for (int i = 1; i < SVC_CNT; ++i) {
        if (socketpair(AF_UNIX, SOCK_STREAM, 0, socketPair))
            LOG_ERROR("socketpair");
        svcs[i][SOCKFD1] = intToStr(socketPair[0]);
        svcs[i][SOCKFD2] = intToStr(socketPair[1]);
    }
}

/**
 * @brief register_signal_handler
 * register the signal handler for child process (keep alive)
 */
void register_signal_handler() {
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_child_process;
    sigaction(SIGCHLD, &sa, NULL);
}

/**
 * @brief launch_child_processes
 * launch all the child processes
 */
void launch_child_processes() {
    for (int i = 0; i < SVC_CNT; i++)
        launch_svc(i);
}

/**
 * @brief handle_child_process
 * keep alive handler for child processes
 */
void handle_child_process() {
    pid_t pid;
    int status;
    while ((pid = waitpid(-1, &status, WNOHANG)) != -1) {
        for (int i = 0; i < SVC_CNT; i++) {
            if (strToInt(PATHS[i][PID]) == pid) {
                LOG("Process %s died, restarting", PATHS[i][NAME]);
                launch_svc(i);
                return;
            }
        }
    }
}


/**
 * Launch a service
 * @param service index of the service in the config array
 * @return
 */
pid_t launch_svc(int service) {
    pid_t pid;
    char *argv[32] = {0};
    int args_len = 0;

    switch (pid = fork()) {
        case 0:
            break;
        case -1:
            LOG_ERROR("fork %s", PATHS[service][EXEC]);
        default:
            PATHS[service][PID] = intToStr(pid);
            LOG("%s:pid %d", PATHS[service][EXEC], pid);
            return pid;
    }
    chdir(JAIL_ROOT); // change the working directory to the jail root
    chroot("."); // chroot to the jail root
    print_current_dir();
    int uid = strToInt(PATHS[service][S_UID]);
    int gid = strToInt(PATHS[service][S_GID]);
//    printf("\n0)\tuid: %d, gid: %d\n",  getuid(), getgid());
    setresgid(gid, gid, gid);
    setgroups(1,group_list);
    setresuid(uid, uid, uid);
    args_len = set_args(argv, service);
    char cwd[1024];
    getcwd(cwd, sizeof(cwd));
    printf("Current working dir: %s\n", cwd);
    LOG("execv args:%s", TO_STR(argv, args_len));
    signal(SIGCHLD, SIG_DFL);
    signal(SIGPIPE, SIG_DFL);
    execv(PATHS[service][EXEC], argv);
    LOG_ERROR("execv %s", PATHS[service][EXEC]);
}


/**
 * set the arguments for the child process
 * args for zookd: [exec, port, fdCount, ....[fd,fdName]...]
 * args for httpsvc: [exec, fd,fdName]
 * @param argv string array to store the arguments
 * @param service  index of the service in the config array
 */
int set_args(char *argv[], int service) {
    int args_len = -1;
    int fd_count = SVC_CNT - 1;
    argv[++args_len] = PATHS[service][EXEC];
    if (service == ZOOKD) {
        argv[++args_len] = PORT;
        argv[++args_len] = intToStr(fd_count);
        for (int i = 1; i < SVC_CNT; i++) {
            argv[++args_len] = svcs[i][SOCKFD2];
            argv[++args_len] = PATHS[i][NAME];
        }
    } else {
        argv[++args_len] = svcs[service][SOCKFD1];
        argv[++args_len] = PATHS[service][NAME];
    }
    argv[++args_len] = NULL;
    return args_len;
}

