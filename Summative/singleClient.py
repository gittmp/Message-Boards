import sys
from socket import *

serverName = sys.argv[1]
serverPort = int(sys.argv[2])
errorMsg = "ERROR"

reqNo = 0

while True:

    clientSocket = socket(AF_INET, SOCK_STREAM)

    #client attempts to connect to the server
    try:
        clientSocket.connect((serverName, serverPort))
        
    except (ConnectionRefusedError, SyntaxError):
        print("Error: connection not available")

    #reqNo counter used to keep track of what iteration the loop is on
    reqNo +=1

    #if we are on the fist iteration of the connection, set the request as GET_BOARDS to retrieve all message board titles
    #otherwise get request from user
    if reqNo == 1:
        request = "GET_BOARDS"
    else:
        request = input("Request: ")

    #if the client has inputted an integer, encapsulate this in a GET_MESSAGES request to retrieve messages from the borresponding board
    if request.isdigit() == True:
        request = "GET_MESSAGES(" + request + ")"

    #send the request to the sever, and retrieve what it sends back
    clientSocket.send(request.encode())
    datas = eval(clientSocket.recv(1024).decode())

    #the OK/Error response is returned to the client as the first element of the list, and if OK the content sent is in the second element
    response = datas[0]
    if len(datas) > 1:
        content = datas[1]

    #print the response out to the client terminal
    print("Response returned: ", response + "\n")

    #request handling
    if request == "GET_BOARDS":
        if response == "OK":

            #the server has sent a dict of board names and their corresponding numbers
            #return this as a numbered list of names printed out on the clients terminal
            boards = content
            print("Boards: ")
            for counter in boards.keys():
                print(str(counter) + ". " + str(boards[counter]))
            
        else:

            #if the request has not been handled OK, return the error to the client
            print(response)
            break

    elif "GET_MESSAGES" in request:
        if response == "OK":

            #for each message provided by the server, return the title and content of each to the client's terminal
            messages = content
            print("Messages: ")
            for item in messages:
                print("Message Title: " + item.split(":")[0].replace(".txt", ""))
                print("Content: " + item.split(":")[1] + "\n")

        else:
            
            print(response)
            continue

    elif request == "POST":

        if response == "OK":

            #retrieve the board number, desired message title and content from the client
            inputNo = input("Board number: ")
            messageTitle = input("Message title: ")
            messageContent = input("Message content: ")

            #send this info to the server, replacing spaces in the message title with underscores
            messageInfo = [inputNo, messageTitle.replace(" ", "_"), messageContent]
            clientSocket.send(str(messageInfo).encode())
            print("Success: message posted to board " + str(inputNo))

        else:
            
            print(response)
        
    elif request == "QUIT" and response == "OK":

        #if requested by the client, terminate connection and break loop
        clientSocket.close()
        break

    else:

        #if any other attempt at a request is inputted, return an error
        print("Error: request invalid")
        continue
