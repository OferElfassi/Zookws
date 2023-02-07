# 1.1 Finding Buffer Overflows

The **zookws** web server is running a simple python web application, **zoobar**, where users transfer "zoobars" (
credits) between each other.

### Installation and execution
1. Using command line, navigate to the project directory
   ```sh
   cd ~/zookws/ 
   ```
2. Compile the code
   ```sh
   make all 
   ```
3. Run the server on port 8080 
   ```sh
   ./zookd-exstack 8080
   ```
4. Test the exploit-template.py script in another terminal window
   ```sh
   python ./exploit-template.py localhost 8080
   ```

## Application layout and potential buffer overflows

<div style="text-align:center;display:flex;flex-direction: column; width: 100%">
    <img src="https://user-images.githubusercontent.com/13490629/217200886-83e8b9be-3508-4bea-9faf-97470a3ec877.png" style="display: block;-webkit-user-select: none;margin: auto;"><br/>
    <img src="https://user-images.githubusercontent.com/13490629/217201214-f8f4ccf9-11ef-4bc4-9b78-9960856a3608.png" style="display: block;-webkit-user-select: none;margin: auto;"><br/>
    <img src="https://user-images.githubusercontent.com/13490629/217201420-d668b7d7-3817-4154-a7ff-98aa298a9ed6.png" style="display: block;-webkit-user-select: none;margin: auto;"><br/>
    <img src="https://user-images.githubusercontent.com/13490629/217203457-8000f037-6039-4fdc-b827-4b6d61f8e67a.png" style="display: block;-webkit-user-select: none;margin: auto;"><br/>
    <img src="https://user-images.githubusercontent.com/13490629/217203965-c89aa02a-2dc8-4831-9b69-5807c564be64.png" style="display: block;-webkit-user-select: none;margin: auto;">
</div><br/>

![image](https://user-images.githubusercontent.com/13490629/217298168-6ed747f9-9a04-4285-9ed2-b43f75943940.png)
