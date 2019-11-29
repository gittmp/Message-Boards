import sys
import time
from socket import *

#extract server ID and port no. from command line
serverName = sys.argv[1]
serverPort = int(sys.argv[2])

#connect to server before we send any data to it

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

#create message to send

messageTitle = input("Input message title: ")
#message = input("Input message content: ")

#send message to server

clientSocket.send(messageTitle.encode())

#await response from server, then close connection

response = clientSocket.recv(1024)
print("Response returned as: ", response.decode())

clientSocket.close()
