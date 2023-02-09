"""
Using python3 language in this file.
"""
import os
import sys
import time
from socket import *
from threading import Thread
from datetime import datetime

# validating command format to start a client
if len(sys.argv) != 4:
    print("\nInvalid number of arguments for client file.\n")
    print("Correct usage: python3 client.py server_IP server_port client_udp_server_port\n")
    exit(0)

# storing the server IP and port and client UDP port numbers from the command line argumenrs    
serverHost = sys.argv[1]
serverPort = int(sys.argv[2])
UDPServerPORT = int(sys.argv[3])

# creating the client socket to connect to the server
serverAddress = (serverHost, serverPort)
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(serverAddress)

# creating the UDP server socket for the client to receive files from other clients
udpServerSocket = socket(AF_INET, SOCK_DGRAM)
udpServerSocket.bind((gethostname(), UDPServerPORT)) # getting hostname of the machine so that client can run on any network

# initializing the variables and data structures to store in-memory data at the server
udp_server_created = False      # this variable indicates whether the UDP server thread has been created or not
close_client = False            # this variable indicates when the user has logged out and UDP server thread can be closed
buf = 1024                      # buffer size to send and receive messages via UDP
recd_file_seq = 1               # this variable indicates the next sequence number for the received files
received_files = dict()         # this dictionary stored the received file details that needs to be shown to the user
sent_file_seq = 1               # this variable indicates the next sequence number for the sent files
sent_files = dict()             # this dictionary stored the sent file details that needs to be shown to the user
active_users = dict()           # this dictionary stores the active user details to verify whether to send file to an user

"""
Defining a multi-thread class for running the UDP server on the client.
Only one instance of this class will be run in a separate thread
when the user has successfully logged in.
"""
class UDPServer(Thread):
    def __init__(self, udpServerSocket):
        Thread.__init__(self)
        self.udpServerSocket = udpServerSocket
        
    def run(self):
        global recd_file_seq
        while not close_client:
            udpServerSocket = self.udpServerSocket
            
            # setting UDP server timeout to 2 seconds and then catching timeout exception using try
            # this is required because when an user logs out, we need to terminate this thread
            # so that the client terminal can go back to prompt. If we do not do this, 
            # then it would be stuck waiting to receive message at this socket
            udpServerSocket.settimeout(2)
            try:
                try:
                    message, clientAddress = udpServerSocket.recvfrom(1024)
                except:
                    continue
                
                # decoding the first received message to extract the file and user name
                received_message = message.decode()                
                if received_message.split(':')[0] == 'Filename':
                    filename = received_message.split(':')[1]
                    user = received_message.split(':')[2]
                    
                    file = open(user+'_'+filename, "wb")
                    udpServerSocket.settimeout(1)   # setting timeout to 1 second for processing the file
                    
                    while True:
                        try:
                            received_message, clientAddress = udpServerSocket.recvfrom(1024)                            
                            file.write(received_message) # receiving file packets and writing it to disk
                        except: # if no more data packet is received for 1 second, file is closed
                            file.close()
                            udpServerSocket.settimeout(2)
                            break
                        
                    # update the details of received files to be shown to user before entering next command
                    current_time = datetime.now()
                    current_time = current_time.strftime("%d %b %Y %H:%M:%S") 
                    received_files[recd_file_seq] = [user, filename, current_time]
                    recd_file_seq += 1
                    
            except Exception as e: # catching any other errors during processing the received messages
                if close_client is False:
                    print("Got error for UDP server thread", e)


"""
Defining a multi-thread class for running the UDP client on the client.
A separate instance of this class will be run in a separate thread
every time the client issues a correct UPD command to send a file to other user.
"""
class UDPClient(Thread):
    def __init__(self, serverName, serverPort, user_from, user_to, filename):
        Thread.__init__(self)
        self.serverName = serverName
        self.serverPort = serverPort
        self.user_from = user_from
        self.user_to = user_to
        self.filename = filename
        print(f"Started UPD client thread to send the file: {self.filename}.\n")
        
    def run(self):
        global sent_file_seq
        try:
            udpClientSocket = socket(AF_INET, SOCK_DGRAM) # created the socket to send the file
            
            # creating and sending first message with the file name and user name
            message = "Filename:" + self.filename + ":" + self.user_from
            udpClientSocket.sendto(message.encode('utf-8'),(self.serverName, self.serverPort))
            time.sleep(0.01)
            
            # reading the file in binary which needs to be sent
            file = open(self.filename, "rb")
            data = file.read(buf)
            
            # sends the data packets as long as there is some data to be sent
            while(data):
                if udpClientSocket.sendto(data, (self.serverName, self.serverPort)):
                    data = file.read(buf)
                    time.sleep(0.01) # Allow UDP server time to process the data
            
            file.close()   
            
            # update the details of sent files to be shown to user before entering next command
            current_time = datetime.now()
            current_time = current_time.strftime("%d %b %Y %H:%M:%S") 
            sent_files[sent_file_seq] = [self.user_to, self.filename, current_time]
            sent_file_seq += 1
            
            udpClientSocket.close()
            # Close the socket
            
        except Exception as e:
            print("Error in sending file:", e)
            

# getting the list for all the allowed characters in a message
allowed_characters = [chr(char) for char in range(ord('a'), ord('z')+1)]
allowed = [chr(char) for char in range(ord('A'), ord('Z')+1)]
allowed_characters.extend(allowed)
allowed = [str(dig) for dig in range(10)]
allowed_characters.extend(allowed)
allowed_characters.extend(['!', '@', '#', '$', '%', '.', '?', ',', ' '])

"""
Function for validating the input and message format for each command and
also checking the format for each argument of the command.
If all the required arguments are present and formats are correct,
this function will return False indicating no issue.
If a problem is found with any format or agument, this function
will return True indicating message is not valid and
user will be sent an error message and asked to enter the command again.
"""
def is_message_format_invalid(username, message):
    if len(message) == 0:
        return True
    
    command = message.split(' ')[0]
    
    if command == 'BCM':
        if len(message.split(' ')) < 2: # checking for correct number of arguments
            print('No argument provided for the BCM command.')
            return True
        
        message_text = message.split(' ')[1:]
        message_text = ' '.join(message_text)
        
        for char in message_text:
            if char not in allowed_characters: # checking for invalid characters in the message
                print('Invalid characters in message for BCM command.')
                return True
                break        
    
    elif command == 'ATU':
        if message != 'ATU': # checking for correct number of arguments
            print('ATU command does not take any arguments.')
            return True
    
    elif command == 'SRB':
        if len(message.split(' ')) < 2: # checking for correct number of arguments
            print('SRB command takes at least one argument.')
            return True
        elif username in message.split(' '): # checking if one's own username is not mentioned in the arguments
            print("Ones's own username is not allowed as an argument for SRB command.")
            return True
    
    elif command == 'SRM':
        if len(message.split(' ')) < 3: # checking for correct number of arguments
            print('Not enough arguments for the SRM command.')
            return True
        
        room_id = message.split(' ')[1]
        if room_id.isnumeric() is False: # checking that the supplied room ID is an integer
            print('Room ID must be an integer.')
            return True
        
        if int(room_id) <= 0: # checking that the supplied room ID is not less than 1
            print('Room ID cannot be less than 1.')
            return True
        
        message_text = message.split(' ')[2:]
        message_text = ' '.join(message_text)
        
        for char in message_text:
            if char not in allowed_characters: # checking for invalid characters in the message
                print('Invalid characters in message for SRM command.')
                return True
                break   
    
    elif command == 'RDM':
        if len(message.split(' ')) != 6: # checking for correct number of arguments
            print('Invalid number of arguments for the RDM command.')
            return True
        
        if message.split(' ')[1] not in ['b', 's']: # checking for allowed message types
            print('Only allowed RDM message types are b or s.')
            return True
        
        m_time = message.split(' ')[2:]
        m_time = ' '.join(m_time)
        format = "%d %b %Y %H:%M:%S"
        try:
            datetime.strptime(m_time, format)
        except: # checking for the correct date format
            print('Invalid date format for RDM command.')
            return True        
    
    elif command == 'UPD':
        if len(message.split(' ')) != 3: # checking for correct number of arguments
            print('Invalid number of arguments for the UPD command.')
            return True
        

    elif command == 'OUT':
        if message != 'OUT': # checking for correct number of arguments
            print('OUT command does not take any arguments.')
            return True
    
    else:
        return True
    
    return False # if no issue observed, send False indicating message is valid

            
# statements to get username and password from the client and validate login            
try:
    login_status = False
    username = input("Username: ")
    while login_status is False:
        password = input("Password: ")
        
        if len(username.split(' ')) > 1: # checking if the username is one word only
           print('Invalid username format. Please try again.')       
           username = input("Username: ")
           continue
        
        if len(password.split(' ')) > 1: # checking if the username is one word only
           print('Invalid password format. Please try again.')    
           continue
        
        # sending a message to the server with the command LOGIN and username and password
        message = username + " LOGIN " + password
        clientSocket.sendall(message.encode())
        
        # receiving response from the server
        data = clientSocket.recv(1024)
        receivedMessage = data.decode()
        
        # based on response from server, either logging in the user or
        # checking for invalid login attempt and blocking user if exceeded max limit
        if receivedMessage.split(' ')[0] == 'LOGIN':
           if receivedMessage.split(' ')[1] == 'success':
               message = username + " PORT " + str(UDPServerPORT)
               clientSocket.sendall(message.encode())
               login_status = True
               print(f'Hello {username}. Welcome to Toom!')
           elif receivedMessage.split(' ')[1] == 'failed':
               print('Invalid password. Please try again.')
           elif receivedMessage.split(' ')[1] == 'locked':
               print('Invalid Password. Your account has been blocked for 10 seconds. Please try again later.')
               break
           elif receivedMessage.split(' ')[1] == 'blocked':
               print('Your account is still blocked due to multiple login failures. Please try again later.')
               break
except Exception as e:
    print("Got the below error during logging in a client:")
    print(e)

# After user has logged in, this while loop will run infinitely until user logs out.
# This loop will ask user to enter the commands, call function to validate the command
# and sends the command messages to the server if the message is valid.
try:
    while login_status is True:
        # creating and starting a UDP server thread if not done before
        if udp_server_created is False:
            udpServerThread = UDPServer(udpServerSocket)
            udpServerThread.start()
            udp_server_created = True
        
        # checking if user has received any files and displaying the details
        if len(received_files) > 0:
            file_list = list(received_files.keys())
            for file in file_list:
                print(f"RECEIVED file {received_files[file][1]} from {received_files[file][0]} at {received_files[file][2]}.")
                del received_files[file]
            print()
        
        # checking if user has sent any files completely and displaying the details
        if len(sent_files) > 0:
            file_list = list(sent_files.keys())
            for file in file_list:
                print(f"SENT file {sent_files[file][1]} to {sent_files[file][0]} at {sent_files[file][2]}.")
                del sent_files[file]
            print()
    
        # asking the user to enter one of the available commands
        message = input("Enter one of the following commands (BCM, ATU, SRB, SRM, RDM, OUT, UPD):")
        message = message.strip()
        while "  " in message: # removing any and all double spaces from the message
            message = message.replace("  ", " ")
        
        # calling the function to check whether the message format is valid or not
        if is_message_format_invalid(username, message):
            print('Incorrect command entered. Please select one of the available commands.\n')
            continue
    
        command = message.split(' ')[0] # getting the command name from the message entered by the user
        
        # for commands BCM, ATU, SRB, SRM and RDM, just sending messages 
        # and displaying the received responses from the server
        if command in ['BCM', 'ATU', 'SRB', 'SRM', 'RDM']:
            send_message = username + ' ' + message
            clientSocket.sendall(send_message.encode())
            
            data = clientSocket.recv(1024)
            receivedMessage = data.decode()
            print(receivedMessage)    
    
        # for the command OUT, sending message to the server t0 log out the user
        # and displaying the received responses from the server
        # also terminating the UDP server thread and breaking this while loop
        elif command == 'OUT':
            send_message = username + ' ' + message
            clientSocket.sendall(send_message.encode())
            
            data = clientSocket.recv(1024)
            receivedMessage = data.decode()
            print(receivedMessage)
            
            close_client = True # updating global variable to terminated UDP server thread
            break
    
        elif command == 'UPD':
            # getting user and file name to be send
            user_to_send = message.split(' ')[1]
            file_to_send = message.split(' ')[2]
            
            # checking if the file to be sent exists or not
            file_exists = os.path.exists(file_to_send)
            if(not file_exists):
                print("Provided file ({file_to_send}) does not exist in the current directory.\n")
                continue
            
            # first calling server with ATU command to get list of all active users
            send_message = username + ' ' + 'ATU'
            clientSocket.sendall(send_message.encode())
            
            data = clientSocket.recv(1024)
            receivedMessage = data.decode()
            
            # checking the list of active users and extracting username and their server IP and port number
            active_users.clear()
            atu_user_list = receivedMessage.split('\n')
            for users in atu_user_list:
                if len(users) > 0:
                    user_details = users.split(')')[0]
                    user_name = user_details.split('(')[0]
                    user_server = user_details.split('(')[1].split(',')[0]
                    user_port = int(user_details.split('(')[1].split(' ')[1])
                    active_users[user_name] = (user_server, user_port)
            
            # checking if the user is active to which file needs to be sent
            if(user_to_send not in active_users):
                print(f"Cannot send file. User {user_to_send} is not online at the moment.\n")
                continue
            
            # if all previous checks are successful, starting the UDP client thread 
            # to send the user details and file to the other client via UDP
            udpClientThread = UDPClient(active_users[user_to_send][0],active_users[user_to_send][1], username, user_to_send, file_to_send)
            udpClientThread.start()
        
        else:
            print('Incorrect command entered. Please select one of the available commands.\n')
    
    # close the socket
    clientSocket.close()

except Exception as e: # to finally catch any other exceptions while processing the command
    print("Got the below error during processing command issued by the client:")
    print(e)
