# 1.2 Code Injection

The goal here is to injected code will unlink (remove) a sensitive file on the server, namely
"grades.txt". using the *-exstack binaries, since they have an executable stack that
makes it easier to inject code.

### Part 1 - Writing assembly code that unlinks a file (shellcode.S)

Afterwards, compile the assembly code into a binary file (shellcode.bin)


![image](https://user-images.githubusercontent.com/13490629/217405206-8b65493e-3ce9-498a-877e-9ae5da96d99b.png)

**Testing the "shellcode.bin"**

* Make sure that "grades.txt" exist at the project folder
* Compile using make aand run the "run-shellcode" program providing the "shellcode.bin" path as argument

  ```shell
  ./run-shellcode shellcode.bin
  ```

### Part 2 - Find the target buffer bounderies and modify "exploit-template.py"

And then inject the compiled Shellcode.S to be executed on the web server:

Here I choose the “value[512]” variable of “http\_request\_headers” function, the exploit will send the shellcode so it will fill the start of the “value” variable buffer. And the calculate the remaining space until the return pointer of the function, and overwrite the return pointer with the address of the start of the exploited buffer where the compiled shellcode start and by this the function will return back to itself and execute the shellcode which will delete the grades.txt file from the server.

![image](https://user-images.githubusercontent.com/13490629/217408210-fafb45b9-1873-4791-b883-25e6b2004d34.png)

![image](https://user-images.githubusercontent.com/13490629/217408292-56c0523e-24da-4eb2-9807-dd01034b9f83.png)

To run this exploit, first run the server on desired port

```shell
./zookd-exstack 8080

```

Then while the server is running , execute the exploit-template.py script and watch how the "grades.txt" file is deleted.

```shell
python ./exploit-template.py localhost 8080
```
