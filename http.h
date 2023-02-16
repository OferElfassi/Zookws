#pragma once

#define DBG_ON 1

#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <stddef.h>
#include <execinfo.h>
#include <time.h>
#include <inttypes.h>

#define UL_ON "\033[4m" //underline
#define UL_OFF "\033[24m" //stop underline
#define TIME_NOW() get_time()

#define LOG_ERROR(...) log_msg(TIME_NOW(),__FILE__, __func__, __LINE__,RED,1,ERROR,__VA_ARGS__);
#define LOG_SUCCESS(...) log_msg(TIME_NOW(),__FILE__, __func__, __LINE__,GREEN,1,MSG,__VA_ARGS__);

#define TO_STR(X, L) _Generic((X), \
int* : int_array_to_str,          \
char**: str_array_to_str          \
)(X,L)

typedef struct SVCS_T {
    char *name;
    char *path;
    pid_t pid;
    int sockfd1;
    int sockfd2;
    uid_t uid;
    gid_t gid;
    int ngrps;
    gid_t grps[10];
}SVCS;

static char *const colors[9] = {"\x1B[0m", "\x1B[31m", "\x1B[32m", "\x1B[33m", "\x1B[34m", "\x1B[35m", "\x1B[36m","\x1B[37m"};
typedef enum {NORMAL, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE} COLOR_t;
typedef enum log_typ {MSG, ERROR} Log_Type;

/** Read the request line like "GET /xxx HTTP/1.0". */
const char *http_request_line(int fd, char *reqpath, char *env, size_t *env_len);

/** Read all HTTP request headers.*/
const char *http_request_headers(int fd);

/** Send an HTTP error message. */
void http_err(int fd, int code, char *fmt, ...);

/** Dispatcher for generating an HTTP response. */
void http_serve(int fd, const char *);

/** handle file not found */
void http_serve_none(int fd, const char *);

/** serve file */
void http_serve_file(int fd, const char *);

/** serve directory */
void http_serve_directory(int fd, const char *);

/** serve executable */
void http_serve_executable(int fd, const char *);

void http_set_executable_uid_gid(int uid, int gid);

/** URL decoder. */
void url_decode(char *dst, const char *src);

/** Unpack and set environmental strings. */
void env_deserialize(const char *env, size_t len);

void fdprintf(int fd, char *fmt, ...);

/** Send file descriptor to another process. */
ssize_t sendfd(int socket, const void *buffer, size_t length, int fd);

/** Receive file descriptor from another process. */
ssize_t recvfd(int socket, void *buffer, size_t length, int *fd);

/** log message to stdout */
void log_msg(const char *time, const char *file, const char *func, int line, COLOR_t color_out, int dbg, Log_Type logType,const char *fmt, ...);

/** print backtrace */
void print_trace();

char *get_time();

/** print current directory */
void print_current_dir();

/** string to int */
int strToInt(const char *str);

/** int to string */
char *intToStr(int i);

/** delay seconds */
void delay(int number_of_seconds);

/** convert int array to string */
char *int_array_to_str(int *arr, int length);

/** convert string array to string */
char *str_array_to_str(char **arr, int length);

/** assert root user */
void assert_root_user();
