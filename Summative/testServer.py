import sys
import os
from socket import *

serverName = sys.argv[1]
serverPort = int(sys.argv[2])

print("Server name: ", serverName, "\nServer port: ", serverPort)

serverSocket = socket(AF_INET, SOCK_STREAM)
try:
    serverSocket.bind((serverName, serverPort))
except PermissionError:
    print("Error: you do not have permission to access this port")
    sys.exit()
except OSError:
    print("Error: server currently unavailable")
    sys.exit()

serverSocket.listen(10)
print("Server ready...")

while True:
    connectionSocket, addr = serverSocket.accept()

    request = connectionSocket.recv(1024).decode()
    print("Request recieved: ", request)

    connectionSocket.send("OK".encode())
    connectionSocket.close()
    
    
