#include <sys/types.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <grp.h>
#include <unistd.h>
#include <signal.h>
#include <string.h>
#include <stdio.h>
#include <dirent.h>
#include <stdlib.h>
#include "http.h"

#define DBG_ON 1
#define LOG(...) log_msg(TIME_NOW(),__FILE__, __func__, __LINE__,BLUE,DBG_ON,MSG,__VA_ARGS__)

#define SVC_CNT 2
#define SHARED_GID 1000
#define JAIL_ROOT "/var/okws/run"
enum svc_indexes {ZOOKD,HTTP_SVC,AUTH_SVC};
SVCS svcs[SVC_CNT] = {
        {"zookd",  "zookd",  -1, -1, -1,500,500,0,{}},
        {"zookhttp","zookhttp",-1, -1, -1,600,600,0,{}},
};


//gid_t group_list[1] = {SHARED_GID};

static pid_t launch_svc(int);

void handle_child_process();

void create_socket_pair();

void register_signal_handler();

void launch_child_processes();

int set_args(char *[], int );

void set_groups(int);

void list_files(char *dir_name);

struct sigaction sa;

char *PORT = "8080";

void print_cwd();

int main(int argc, char **argv) {
    system("clear");
    print_cwd();
    if (argc == 2)
        PORT = argv[1];
    create_socket_pair();
    register_signal_handler();
    launch_child_processes();

    pid_t pid;

    while ((pid = wait(NULL)) > 0) {
        for (int i = 0; i < SVC_CNT; i++) {
            if (svcs[i].pid == pid) {
                LOG("Process %s died, restarting", svcs[i].name);
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
    for (int i = 1; i < SVC_CNT; i++) {
        if (socketpair(AF_UNIX, SOCK_STREAM, 0, socketPair))
            LOG_ERROR("socketpair");
        svcs[i].sockfd1 = socketPair[0];
        svcs[i].sockfd2 = socketPair[1];
        LOG("Created socket pair for %s , sockfd1 =%d, sockfd2 =%d,", svcs[i].name, svcs[i].sockfd1, svcs[i].sockfd2);
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
            if (svcs[i].pid == pid) {
                LOG("Process %s died, restarting", svcs[i].name);
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
pid_t launch_svc(int svc_index) {
    pid_t pid;
    char *argv[32] = {0};
    int args_len = 0;

    switch (pid = fork()) {
        case 0:
            break;
        case -1:
            LOG_ERROR("fork %s", svcs[svc_index].path);
        default:
            svcs[svc_index].pid = pid;
            LOG("%s:pid %d", svcs[svc_index].path, pid);
            return pid;
    }
    chdir(JAIL_ROOT); // change the working directory to the jail root
    LOG("CWD: %s", getcwd(NULL, 0));
    chroot("."); // chroot to the jail root
    list_files(".");
    uid_t uid = svcs[svc_index].uid;
    gid_t gid = svcs[svc_index].gid;
    printf("\n0)\tuid: %d, gid: %d\n",  getuid(), getgid());
    setgid(gid);
    set_groups(svc_index);
    setuid(uid);
    args_len = set_args(argv, svc_index);
    print_cwd();
    list_files(".");
    printf("\n0)\tuid: %d, gid: %d\n",  getuid(), getgid());
    LOG("execv path:%s args:%s",svcs[svc_index].path, TO_STR(argv, args_len));
    signal(SIGCHLD, SIG_DFL);
    signal(SIGPIPE, SIG_DFL);
    execv(svcs[svc_index].path, argv);
    LOG_ERROR("execv %s", svcs[svc_index].path);
    return 0;
}


/**
 * set the arguments for the child process
 * args for zookd: [exec, port, fdCount, ....[fd,fdName]...]
 * args for httpsvc: [exec, fd,fdName]
 * @param argv string array to store the arguments
 * @param service  index of the service in the config array
 */
int set_args(char *argv[], int svc_index) {
    int args_len = -1;
    int fd_count = SVC_CNT - 1;
    argv[++args_len] = svcs[svc_index].path;
    if (svc_index == ZOOKD) {
        argv[++args_len] = PORT;
        argv[++args_len] = intToStr(fd_count);
        for (int i = 1; i < SVC_CNT; i++) {
            argv[++args_len] = intToStr(svcs[i].sockfd2);
            argv[++args_len] = svcs[i].name;
        }
    } else {
        argv[++args_len] = intToStr(svcs[svc_index].sockfd1);
        argv[++args_len] = svcs[svc_index].name;
    }
    argv[++args_len] = NULL;
    return args_len;
}

void set_groups(int svc_index){
    int group_count = svcs[svc_index].ngrps;
    if(group_count == 0)
        return;
    gid_t group_list[group_count];
    for (int i = 0; i < group_count; i++) {
        group_list[i] = svcs[svc_index].grps[i];
    }
    setgroups(group_count,group_list);
}

void print_cwd(){
    char cwd[1024];
    getcwd(cwd, sizeof(cwd));
    printf("Current working dir: %s\n", cwd);
}

void list_files(char *dir_name) {
    DIR *d;
    struct dirent *dir;
    d = opendir(dir_name);
    printf("Files in %s:\n", dir_name);
    if (d) {
        while ((dir = readdir(d)) != NULL) {
            printf("%s\n", dir->d_name);
        }
        closedir(d);
    }
}
