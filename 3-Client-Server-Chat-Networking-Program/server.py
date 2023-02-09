"""
Using python3 language in this file.
"""
import os
import sys
from socket import *
from threading import Thread
from datetime import datetime

# validating command format to start the server
if len(sys.argv) != 3:
    print("\nInvalid number of arguments for server file.\n")
    print("Correct usage: python3 server.py server_port number_of_consecutive_failed_attempts\n")
    exit(0)
    
elif len(str(sys.argv[2])) != 1:
    print(f"\nInvalid value ({sys.argv[2]}) for number of allowed failed consecutive attempts. Only integer values from 1 to 5 are allowed.\n")
    exit(0)
    
elif str(sys.argv[2]).isnumeric() is False:
    print(f"\nInvalid value ({sys.argv[2]}) for number of allowed failed consecutive attempts. Only integer values from 1 to 5 are allowed.\n")
    exit(0)
    
elif int(sys.argv[2]) < 1 or int(sys.argv[2]) > 5:
    print(f"\nInvalid value ({sys.argv[2]}) for number of allowed failed consecutive attempts. Only integer values from 1 to 5 are allowed.\n")
    exit(0)
   
# storing the server port and allowed failed consecutive attempts number from the command line argumenrs        
serverHost = gethostname() # getting hostname of the machine so that server can run on any network
serverPort = int(sys.argv[1])
serverAddress = (serverHost, serverPort)
FAILED_LIMIT = int(sys.argv[2])

# creating the socket for the server
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(serverAddress)

# initializing the variables and data structures to store in-memory data at the server
user_login_attempts = dict()        # to keep track of failed login attempts for each user
blocked_users = dict()              # to keep track of blocked users

user_seq = int(1)                   # this variable indicates the next user sequence number to be added to the user log file
message_seq = int(1)                # this variable indicates the message sequence number to be added to the public message log file
room_seq = int(1)                   # this variable indicates the next room sequence number to be created for a separate chat room
room_message_seq = dict()           # this dictionary indicates the next message sequence number to be added to the chat room log file for each room
chat_rooms = dict()                 # this dictionary keeps track of all the rooms that have been created for different users

"""
Defining a multi-thread class for client.
An instance of this class will be run in a separate thread
each time a client connects to the server.
"""
class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = False
        
        print("===== New connection created for: ", clientAddress)
        self.clientAlive = True
        
    def run(self):
        message = ''        
        try:        
            while self.clientAlive: # this thread will run only until client is alive
                # receiving message from the client
                data = self.clientSocket.recv(1024)
                message = data.decode()
                
                command = message.split(' ')[1] # to get the command name from the message      

                # finding the command name and calling function for that command              
                if command == 'LOGIN':
                    res_message = self.process_login(message)
                    self.clientSocket.send(res_message.encode())
                    
                elif command == 'PORT':
                    self.register_UDP_port(message)
                    
                elif command == 'BCM':
                    res_message = self.BCM(message)
                    self.clientSocket.send(res_message.encode())
                    
                elif command == 'ATU':
                    res_message = self.ATU(message)
                    self.clientSocket.send(res_message.encode())
                    
                elif command == 'SRB':
                    res_message = self.SRB(message)
                    self.clientSocket.send(res_message.encode())
                    
                elif command == 'SRM':
                    res_message = self.SRM(message)
                    self.clientSocket.send(res_message.encode())
                    
                elif command == 'RDM':
                    res_message = self.RDM(message)
                    self.clientSocket.send(res_message.encode())
                    
                elif command == 'OUT':
                    res_message = self.OUT(message)                    
                    self.clientSocket.send(res_message.encode())
                    self.clientAlive = False
                    
                else: # checking for any invalid command, although this won't happen
                      # as all the command formats are being checked on the client side
                      # and only the valid commands are being sent to the server
                    print("Received invalid command from the client.\n")
                    message = 'Incorrect command entered. Please select one of the available commands.\n'
                    self.clientSocket.send(message.encode())
                    
        # checking for any exceptions in executing command at the server
        except Exception as e:
            print("Error in processing client's command. Got below error:")
            print(e)
            self.clientAlive = False
    
    """
    Function for verifying the login details sent by the client.
    If the users exists in the credentials file and provided correct pasword, 
    they will be logged in. If the user doesn't exist in the credentials file,
    new entry will be created from them by updating the credentials file.
    It also checks for the invalid login attempts and blocks out an user
    for 10 seconds if they exceeds the maximum failed login attempts.
    """
    def process_login(self, message):
        username = message.split(' ')[0]
        password = message.split(' ')[2]
        
        # checking if the user is blocked or not
        if username in blocked_users:
            timeout = 10-((datetime.now()-blocked_users[username]).total_seconds())
            if timeout > 0:
                return 'LOGIN blocked'
            else:
                if username in user_login_attempts:
                    user_login_attempts[username] = 0
                del blocked_users[username]    
            
        login_status = 'Trying'
                    
        # getting the username and pasword from the credentials file
        file = open('credentials.txt', 'r')
        file_content = file.read().split('\n')
        file.close()
                    
        # matching the username and password sent by client to each
        # username and password stored in the credentials file
        for lines in file_content:
            if len(lines.strip()) > 0:
                if username == lines.split(' ')[0]:             # matched to an existing user
                    if password == lines.split(' ')[1]:         # password verified
                        # reseting the invalid attempts
                        if username in user_login_attempts:     
                            user_login_attempts[username] = 0
                        if username in blocked_users:
                            del blocked_users[username]
                        res_message = 'LOGIN success' 
                        login_status = 'success'       
                        print(f"{username} logged in.\n")
                    else: # password not matched
                        login_status = 'Failed'
                        # updating the invalid attempts count
                        if username in user_login_attempts:
                            user_login_attempts[username] += 1
                        else: user_login_attempts[username] = 1
                                
                        # blocking user if the failed attempts exceeds the specified limit
                        if user_login_attempts[username] >= FAILED_LIMIT:
                            res_message = 'LOGIN locked'
                            if username not in blocked_users:
                                blocked_users[username] = datetime.now()                            
                        else:
                            res_message = 'LOGIN failed'                                            
                                    
                        break        
                          
        # if the user doesn't exists, add the user to the credentials file
        if login_status == 'Trying':
            file = open('credentials.txt', 'a')
            file.write(f"{username} {password}\n")                        
            file.close()
            res_message = 'LOGIN success'
                        
        return res_message
    
    """
    Function for storing the user details along with the UDP port number
    in the user log file to keep track of all the active users.
    """
    def register_UDP_port(self, message):
        global user_seq
        # getting username and other arguments from the message sent by the client
        username = message.split(' ')[0]
        udp_port = message.split(' ')[2]
                    
        current_time = datetime.now()
        logged_in_time = current_time.strftime("%d %b %Y %H:%M:%S")  
                    
        # formatting the details to be stored in the file
        line = str(user_seq) + ';' + str(logged_in_time) + ';' + username + ';' + clientAddress[0] + ';' + str(udp_port) + '\n'
        user_seq += 1
                    
        # adding the user details to the log file
        file = open('userlog.txt', 'a')
        file.write(line)                    
        file.close()           
        
    """
    Function for processing the BCM command sent by the client.
    It broadcasts the message sent by the client by updating 
    the message in the messagelog.txt file.
    """
    def BCM(self, message):
        global message_seq
        # getting username and other arguments from the message sent by the client
        username = message.split(' ')[0]
        bcm_message = message.split(' ')[2:]
        bcm_message = ' '.join(bcm_message)
                    
        current_time = datetime.now()
        message_time = current_time.strftime("%d %b %Y %H:%M:%S")  
                    
        # formatting the details to be stored in the file
        line = str(message_seq) + ';' + str(message_time) + ';' + username + ';' + bcm_message + '\n'
        res_message = f'Broadcasted message #{message_seq} at {message_time}.\n'
        print(f'{username} broadcasted message #{message_seq} at {message_time}: {bcm_message}\n')
        message_seq += 1    # increasing message sequence number by 1
                    
        # adding the message to the public message file
        file = open('messagelog.txt', 'a')
        file.write(line)                    
        file.close() 
        
        return res_message
    
    """
    Function for processing the ATU command sent by the client.
    It gets the list of all active users from the user log file
    and sent the details to the client.
    """
    def ATU(self, message):
        # getting username from the message sent by the client
        username = message.split(' ')[0]
        
        # fetching all the user details from the log file
        file = open('userlog.txt', 'r')
        file_content = file.read().split('\n')               
        file.close() 
        
        # checking all the entries in the file and
        # formatting the details to be sent to the user
        new_file_content = list()
        for i in range(len(file_content)):
            if len(file_content[i]) > 0:
                entries = file_content[i].split(';')
                if username != entries[2]:      # doesn't send one's own detail to them
                    line = f"{entries[2]}({entries[3]}, {entries[4]}), active since {entries[1]}." 
                    new_file_content.append(line)
        
        # checking if there are any active users found or not
        if len(new_file_content) > 0:
            res_message = '\n'.join(new_file_content)
            res_message += '\n'
        else:
            res_message = 'No other user is active now.\n'
            
        print(f"{username} issued ATU command.\n")
        
        return res_message
    
    """
    Function for processing the SRB command sent by the client.
    It checks the status of all the users mentioned in the SRB command,
    and if all the users are active and no chat room exists for them,
    it creates a new separate chat room for these users.
    """
    def SRB(self, message):
        global room_seq
        # getting username and other arguments from the message sent by the client
        username = message.split(' ')[0]
        users = message.split(' ')[2:]    
        if username in users: del users[username]        
        
        # to check if a separate chat room already exists
        users_list = users.copy()
        users_list.append(username)
        users_list.sort()
        for room_ids in chat_rooms:
            if chat_rooms[room_ids] == users_list:
                print(f"{username} issued SRB command but the chat room already exists.\n")
                return f'A separate chat room (ID: {room_ids}) already exists for these users.\n'
                break
            
        users_status = dict()
        create_room = 1
        
        # to check if all the users mentioned in the message are active or not
        file = open('userlog.txt', 'r')
        file_content = file.read().split('\n')               
        file.close() 
        
        for i in range(len(file_content)):
            if len(file_content[i]) > 0:                
                entries = file_content[i].split(';')
                if entries[2] in users:
                    users_status[entries[2]] = 'Active'
        
        # checking for those users which exists but are not active
        file = open('credentials.txt', 'r')
        file_content = file.read().split('\n')               
        file.close() 
        
        for i in range(len(file_content)):
            if len(file_content[i]) > 0:                
                user_checking = file_content[i].split(' ')[0]
                if user_checking in users and user_checking not in users_status:
                    users_status[user_checking] = 'Exists'
                    create_room = 0
        
        # checking if any of the mentioned user doesn't exists
        for user in users:
            if user not in users_status:
                users_status[user] = 'Unknown'
                create_room = 0
        
        # room cannot be created if any user doesn't exists or is offline
        if create_room == 0:
            offline = list()
            unknown = list()
            for user in users_status:
                if users_status[user] == 'Exists':
                    offline.append(user)
                elif users_status[user] == 'Unknown':
                    unknown.append(user)            
            
            res_message = 'Server was unable to create a separate room.\n'
            print(f"{username} issued SRB command but the server was unable to create it as some users are offline or doesn't exists.\n")
            if len(unknown) > 0:
                res_message += 'Following users does not exist: ' + ', '.join(unknown) + '\n'
            if len(offline) > 0:
                res_message += 'Following users are offline: ' + ', '.join(offline) + '\n'
        else: # creating a chat room as all users are active
            users.append(username)
            res_message = f'Separate chat room (ID: {room_seq}) has been created.\n'
            res_message += 'Users in this room are: ' + ', '.join(users) + '\n'
            users.sort()                   # sort list of all users by name
            chat_rooms[room_seq] = users   # keeping track of users for which groups have been created
            room_message_seq[room_seq] = 1 # initializing message sequence number for this room to 1
            print(f'{username} created a separate room #{room_seq}.')
            print('Users in this room are: ' + ', '.join(users) + '\n')
            room_seq += 1 # increasing the room sequence number by 1
        
        return res_message
    
    """
    Function for processing the SRM command sent by the client.
    It checks if the provided room ID is valid and if the user
    is part part of the room or not. If there is no issue, then
    it sends the message that chat room by updating the log file.
    """
    def SRM(self, message):
        global room_seq
        # getting username and other arguments from the message sent by the client
        username = message.split(' ')[0]
        room_id = int(message.split(' ')[2])
        
        # checking if the supplied room ID exists or not
        if room_id >= room_seq:
            print(f"{username} issued SRM command but the chat room does not exist.\n")
            return f'This separate chat room (ID: {room_id}) does not exists.\n'
        
        # checking if the user is part of the mentioned chat room
        if username not in chat_rooms[room_id]:
            print(f"{username} issued SRM command for room #{room_id} but {username} is not a member of this room.\n")
            return f'You are not a member of this separate chat room (ID: {room_id}).\n'
        
        chat_message = message.split(' ')[3:]   
        chat_message = ' '.join(chat_message)
        
        current_time = datetime.now()
        message_time = current_time.strftime("%d %b %Y %H:%M:%S")  
                    
        # formatting the details to be stored in the file
        line = str(room_message_seq[room_id]) + ';' + str(message_time) + ';' + username + ';' + chat_message + '\n'
        res_message = f'Posted message #{room_message_seq[room_id]} to room #{room_id} at {message_time}.\n'
        
        # adding the message to the file for that separate chat room
        file = open(f'SR_{room_id}_messageLog.txt', 'a')
        file.write(line)                    
        file.close() 
        
        print(f'{username} sent a message #{room_message_seq[room_id]} to separate room #{room_id} at {message_time}: {chat_message}\n')
        room_message_seq[room_id] += 1 # increasing the message sequence number for this room by 1
        
        return res_message
    
    """
    Function for processing the RDM command sent by the client.
    It checks the public message file or the files for each chat 
    room based on the message type provided in the command. 
    It sends any new messages after the mentioned timestamp to the client.
    """
    def RDM(self, message):
        # getting username and other arguments from the message sent by the client
        username = message.split(' ')[0]
        m_type = message.split(' ')[2]
        m_time = message.split(' ')[3:]
        m_time = ' '.join(m_time)
        res_message = ''
        
        format = "%d %b %Y %H:%M:%S"
        m_date = datetime.strptime(m_time, format)
        
        # checking public messages for the message type b
        if m_type == 'b':
            print(f"{username} issued an RDM command for message type b.\n")
            file_exists = os.path.exists('messagelog.txt') # checking if the public message file exists
            if(file_exists):
                # reading messages from the public message log file
                file = open('messagelog.txt', 'r')
                file_content = file.read().split('\n')               
                file.close() 
                
                # formatting the message details to be sent to the user
                for i in range(len(file_content)):
                    if len(file_content[i]) > 0:
                        entries = file_content[i].split(';')
                        # only checks messages sent after the specified date timestamp
                        if datetime.strptime(entries[1], format) > m_date:
                            if res_message == '':
                                res_message += f'New public messages since {m_time} are:\n'
                            res_message += f"#{entries[0]} by {entries[2]} at {entries[1]}: {entries[3]}\n" 
        
        # checking messages in each separate chat room for the message type s
        if m_type == 's':
            print(f"{username} issued an RDM command for message type s.\n")
            
            # checking all the chat rooms that exists
            for room in range(1, room_seq): 
                if username in chat_rooms[room]:   
                    found_new = 0
                    
                    file_exists = os.path.exists(f'SR_{room}_messageLog.txt')
                    if(file_exists): # checking if the file exists for that chat room
                        # reading messages from the chat room message log file
                        file = open(f'SR_{room}_messageLog.txt', 'r')
                        file_content = file.read().split('\n')               
                        file.close() 
                        
                        # formatting the message details to be sent to the user
                        for i in range(len(file_content)):
                            if len(file_content[i]) > 0:
                                entries = file_content[i].split(';')
                                # only checks messages sent after the specified date timestamp
                                if datetime.strptime(entries[1], format) > m_date:
                                    if res_message == '':
                                        res_message += f'New messages in separate chat rooms since {m_time} are:\n'
                                    if found_new == 0:
                                        res_message += f"For chat room #{room}:\n"
                                    res_message += f"#{entries[0]} by {entries[2]} at {entries[1]}: {entries[3]}\n" 
                                    found_new = 1
                
        
        if res_message == '':
            res_message = 'No new messages found.\n'
        return res_message
    
    """
    Function for processing the OUT command sent by the client.
    This logs out a client from the server by deleting their entry
    from the user log file and decreasing the active user count.
    """
    def OUT(self, message):
        global user_seq
        # getting username from the message sent by the client
        username = message.split(' ')[0]
        
        # getting list of all active users
        file = open('userlog.txt', 'r')
        file_content = file.read().split('\n')               
        file.close() 
        
        # modifying the active users list and removing the supplied user from it
        minus = 0
        new_file_content = list()
        for i in range(len(file_content)):
            if len(file_content[i]) > 0:
                if username == file_content[i].split(';')[2]: minus = 1
                else: # reducing the sequence number of all the users in the file
                      # after the user to be removed by 1
                    new_id = str(int(file_content[i][0]) - minus)
                    line = new_id + file_content[i][1:] 
                    new_file_content.append(line)
            else:
                new_file_content.append(file_content[i])
        
        lines = '\n'.join(new_file_content)
        
        # writing the updated user list details to user log file
        file = open('userlog.txt', 'w')
        file.write(lines)                    
        file.close() 
        print(f"{username} logged out.\n")
        user_seq -= 1  # decreasing the active user count by 1
        
        res_message = f"Good bye {username}!\n"
        return res_message


print("\n===== Server is running now =====")
print("===== Waiting for connection request from clients =====")

while True:
    # server accepting connections fro the client
    serverSocket.listen()
    clientSockt, clientAddress = serverSocket.accept()
    
    # creating and starting a separate thread for eac client
    clientThread = ClientThread(clientAddress, clientSockt)
    clientThread.start()
