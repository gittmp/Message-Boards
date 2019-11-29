import sys
import time
from socket import *

#extract server ID and port no. from command line
serverName = sys.argv[1]
serverPort = int(sys.argv[2])

print("Server name is: ", serverName, "\nServer port is: ", serverPort)

#socket created and binded to an address (listening socket)
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((serverName, serverPort))

serverSocket.listen(10)
print("Server ready...")
responseOK = "OK"
responseError = "Error"

while True:
    #seperate socket created to deal with each incoming connection (connection socket)
    #accept function waits for incomming connections
    connectionSocket, addr = serverSocket.accept()

    #recieve message from client
    message = connectionSocket.recv(1024).decode()

    print("Message recieved: ", message)

    #create and send a response message back to client
    connectionSocket.send(responseOK.encode())

    #connection closed and returns to listening for other clients
    connectionSocket.close()
    
