import sys
import os
import datetime as dt
from socket import *
import threading

#function to determine the most recent datatime out of two inputted
def mostRecent(datetime1, datetime2):
    if datetime1[:8].isdigit() == True and datetime2[:8].isdigit() == True and datetime1[9:15].isdigit() == True and datetime2[9:15].isdigit() == True:
        if int(datetime1[:8]) > int(datetime2[:8]):
            return 1
        elif int(datetime1[:8]) < int(datetime2[:8]):
            return 0
        else:
            if int(datetime1[9:15]) >= int(datetime2[9:15]):
                return 1
            else:
                return 0
    else:
        return 0

#function which uses the mostRecent function to select the most recent 100 messages from a list
def latestHun(lst):
    output = []
    for x in range(100):
        n = len(lst)
        maxVal = lst[n-1]
        for y in range(len(lst)):
            if mostRecent(lst[y], maxVal) == True:
                maxVal = lst[y];        
        lst.remove(maxVal);
        output.append(maxVal)
    return output



#class to deal with implementing threading when multiple clients connect, serving their requests
class threadClient(threading.Thread):

    #initiates threading connection
    def __init__(self, addr, connSocket):
        threading.Thread.__init__(self)
        self.connSock = connSocket

    #code to be ran by a new thread opened on a new client
    def run(self):
        
        print ("New client connected on address: ", addr)

        #serve client with desired requests about the message boards
        while True:

            try:

                #retrieve request data from client
                request = self.connSock.recv(2048).decode()
                print("Request recieved: ", request)

                #construct initial data about incoming request to be later stored in the server.log file
                logInfo = [serverIP + ":" + str(serverPort), str(dt.datetime.now())[:19]]   

                #outer conditional statements check the type of request recieved from the client
                if request == "GET_BOARDS":
                    
                    #log message type
                    logInfo.append("GET_BOARDS")

                    #check if the board folder has been defined
                    if os.path.isdir("board"):

                        #loop which creates an ordered dict of board names (each board gets a respective label number from counter)
                        ordBoards = {}
                        counter = 0
                        
                        #first checks if any boards have been defined
                        if len(os.listdir("board")) > 0:

                            #then, for ever message board in the board folder, updates dict with corresponding counter label
                            for board in os.listdir("board"):
                                if os.path.isdir(os.path.join("board", board)):
                                    counter += 1
                                    ordBoards.update({counter:board})

                            self.connSock.send(str([responseOK, ordBoards]).encode())
                            logInfo.append("OK")
                            
                        else:

                            #catches error of no message boards in board folder
                            errorType = "Error: no message boards defined"
                            print(errorType)
                            self.connSock.send(str([errorType]).encode())
                            logInfo.append("Error")
                            sys.exit()
                    else:

                        #catches error of board folder not having been created
                        errorType = "Error: board folder does not exist"
                        print(errorType)
                        self.connSock.send(str([errorType]).encode())
                        logInfo.append("Error")
                        sys.exit()
                        
                elif "GET_MESSAGES(" in request and ")" in request:
                    
                    logInfo.append("GET_MESSAGES")

                    #if message is of type "GET_MESSAGES" then remove the type enclosure to leave the requested board number
                    reqBoard = request.replace("GET_MESSAGES(", "").replace(")", "")

                    #check the board number relates to a board in the dict, and if so get the board name
                    numBoard = int(reqBoard)
                    if numBoard in ordBoards.keys():
                        namBoard = ordBoards[numBoard]
                    else:
                        print("Error: board index out of range")
                        self.connSock.send(str(["Error: board index out of range"]).encode())
                        continue

                    #create the path to the board location
                    boardpath = "board/" + namBoard
                    messages = []

                    if namBoard in os.listdir("board"):

                        #create a list of all non-hidden files in the specified board
                        boardMessages = [ x for x in os.listdir(boardpath) if not x.startswith(".") ]

                        #check if the board contains any messages - if not return error
                        if len(boardMessages) > 0:

                            #if there is less than 100 messages in the board, select all of them
                            if len(boardMessages) <= 100:

                                for messageTitle in boardMessages:

                                    messagePath = boardpath + "/" + messageTitle
                                    with open(messagePath, 'r') as file:
                                        content = file.read().replace("\n", "")

                                    messages.append(messageTitle + ":" + content)

                            else:

                                #otherwise, select the most recent 100 messages from board using our pre-defined function
                                recentMessages = latestHun(boardMessages)

                                for messageTitle in recentMessages:
                                
                                    messagePath = boardpath + "/" + messageTitle
                                    with open(messagePath, 'r') as file:
                                        content = file.read().replace("\n", "")

                                    messages.append(messageTitle + ":" + content)

                            #return selected messages to client
                            print("Accessing board: ", boardpath)
                            respond = str([responseOK, messages])
                            self.connSock.send(respond.encode())
                            logInfo.append("OK")
                            
                        else:
                            
                            errorType = "Error: no messages available"
                            print(errorType)
                            self.connSock.send(str([errorType]).encode())
                            logInfo.append("Error")
                        
                    else:
                        
                        errorType = "ERROR: board not found"
                        print(errorType)
                        self.connSock.send(str([errorType]).encode())
                        logInfo.append("Error")

                elif request == "POST":

                    logInfo.append("POST")
                    self.connSock.send(str([responseOK]).encode())

                    #collect the information about the message trying to be posted from the client
                    messageInfo = eval(self.connSock.recv(2048).decode())

                    #check if a board number has been supplied, and the corresponding board exists
                    if messageInfo[0].isdigit() == True and int(messageInfo[0]) in ordBoards.keys():

                        #retrieve the board for the message to be posted to, and note the current date/time in the desired format
                        messageBoard = ordBoards[int(messageInfo[0])]
                        datentime = str(dt.datetime.now())
                        timestamp = datentime[:10].replace("-", "") + "-" + datentime[11:19].replace(":", "")

                        #create the message title, and desired path to where the message file will be created
                        messageTitle = timestamp + "-" + messageInfo[1] + ".txt"
                        messagePath = "board/" + messageBoard + "/" + messageTitle
                        messageContent = messageInfo[2]

                        #create the message file, and write the content of the client's message to it
                        with open(messagePath, 'w') as new:
                            new.write(messageContent)
                            
                        print("Added message: ", messageContent)
                        print("To location: ", messagePath)
                        self.connSock.send(responseOK.encode())
                        logInfo.append("OK")
                    
                    else:
                        errorType = "Error: message not posted"
                        self.connSock.send(errorType.encode())
                        print(errorType)
                        logInfo.append("Error")
                        continue

                elif request == "QUIT":

                    logInfo.append("QUIT")
                    
                    print("Quitting connection")
                    self.connSock.send(str([responseOK]).encode())
                    logInfo.append("OK")

                else:

                    #if an unrecognised request is inputted by the client, return an error
                    logInfo.extend(["UNRECOGNISED", "Error"])
                    errorType = "Error: request not recognised"
                    print(errorType)
                    self.connSock.send(str([errorType]).encode())

                #if the server.log file exists, append the log for this request to it, otherwise create the file and write to it
                if os.path.isfile("server.log"):
                    with open("server.log", 'a') as log:
                        log.write(str(logInfo) + "\n")
                else:
                    with open("server.log", 'w') as log:
                        log.write(str(logInfo) + "\n")
    
            except (BrokenPipeError, ConnectionResetError, KeyboardInterrupt):
                print ("Client on address " + str(addr) + " has disconnected")
                break



#define the server socket, retrieve server name/port from terminal arguments
serverSocket = socket(AF_INET, SOCK_STREAM)
serverIP = sys.argv[1]
serverPort = int(sys.argv[2])
print("Server IP: ", serverIP, "\nServer port: ", serverPort)
responseOK = "OK"

#attempt to bind sever socket to specified name/port
try:
    serverSocket.bind((serverIP, serverPort))
except PermissionError:
    print("Error: you do not have permission to access this port")
    sys.exit()
except OSError:
    print("Error: server currently unavailable")
    sys.exit()

#implement indefinitely whilst server is running
while True:

    #listen for incomming connections from client to server
    serverSocket.listen(1)

    #accept connection
    connectionSocket, addr = serverSocket.accept()

    #create new thread to run connection on
    threadIt = threadClient(addr, connectionSocket)
    threadIt.start()

