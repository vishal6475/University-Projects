# IMPORT ANY REQUIRED MODULE

class MazeError(Exception):
    def __init__(self, message):
        self.message = message
        

class Maze:
    def __init__(self, filename):
        self.fileName = filename
        self.maze_file = open(filename, "r")
        self.maze_input = self.maze_file.read()
        self.maze_file.close()
        
        # to check for input error
        self.check_input_error()
        
        # to check for maze criterion
        self.check_maze_error()
    
    def check_input_error(self):
        
        if len(self.maze_input) == 0:
            raise MazeError('Incorrect input.')
            
        # checks if file contains any number
        # otherwise subsequent checks may fail due to index out of range error
        does_file_contains_any_number = False
        for v in self.maze_input: 
            if v in ('0', '1', '2', '3'):
                does_file_contains_any_number = True
        if does_file_contains_any_number == False:
            raise MazeError('Incorrect input.')
            
        # checks for correct input characters
        for v in self.maze_input: 
            if v not in (' ', '\n', '0', '1', '2', '3'):
                raise MazeError('Incorrect input.')
        
        # Removes unwanted spaces and newline characters- to get correct maze values
        while " " in self.maze_input:
            self.maze_input = self.maze_input.replace(" ", "")
        while "\n\n" in self.maze_input:
            self.maze_input = self.maze_input.replace("\n\n", "\n")
        if self.maze_input[0] == '\n':
            self.maze_input = self.maze_input.replace('\n', '', 1) # removes 1st \n
        if self.maze_input[-1] == '\n':
            self.maze_input = self.maze_input[:len(self.maze_input)-1] # removes 1st \n
            
            
        # check for number of rows between 2 and 41
        if self.maze_input.count('\n') > 40 or self.maze_input.count('\n') < 1:
            raise MazeError('Incorrect input.')
        
        self.get_grid() # to get the grid structure for maze values
        
        # check for number of columns between 2 and 31
        if self.col_count < 2 or self.col_count > 31:
            raise MazeError('Incorrect input.')
            
        # checks if each row contains same number of elements
        for i in range(self.row_count):
            if len(self.grid[i]) != self.col_count:
                raise MazeError('Incorrect input.')
        
        
    # if input is of correct format, checks if maze conditions are fulfilled
    def check_maze_error(self):
        
        # last digit of any row cannot by 1 or 3
        for i in range(self.row_count):
            if self.grid[i][self.col_count-1] in ('1', '3'):
                raise MazeError('Input does not represent a maze.')
        
        # any digit of last row cannot by 2 or 3
        for j in range(self.col_count):
            if self.grid[self.row_count-1][j] in ('2', '3'):
                raise MazeError('Input does not represent a maze.')
    
    # to create grid values of points for the maze from the input file data
    def get_grid(self):
        self.grid = [[] for _ in range(41)]        
        self.row_count = self.col_count = 0
        line = ""
        for v in self.maze_input:
            if v.isnumeric():
                line += v
            if v == '\n':
                self.col_count = 0
                if len(line) > 0:
                    self.grid[self.row_count] = line
                    self.row_count += 1               
                line = ""
        if line != "":
            self.grid[self.row_count] = line
            self.row_count += 1
        self.col_count = len(self.grid[0])
        
    
    # to analyze maze and calculate all the details 
    def analyse(self):
        
        # call function to calculate number of gates
        self.find_gates()
        
        # call function to create a grid to represent all the cells in the maze
        self.get_maze()
        
        # assign numbers to distinct areas in the maze
        self.area_count = -1
        for i in range(self.maze_rows):
            for j in range(self.maze_cols):
                if self.visited[i][j] == 0:
                    self.area_count += 1
                    self.area[i][j] = self.area_count
                    self.get_area(i, j)
                
        # call function to find which areas are accessible
        self.get_accessible_area()
        
        # calls function to find number of inaccessible points
        self.get_inaccessible_points()
        
        # call function to create a grid to identify and store data for distinct walls
        self.get_walls()
        
        # call function to create and store data for cul-de-sacs
        self.create_cul_de_sac_grid()
        
        # to identify entry-exit paths in the maze
        self.get_entry_exit_path_count()
        
        # print the final stats of the maze in expected format        
        self.print_final_stats()
             
        
    # to find the number of gates in the maze
    def find_gates(self):
        
        self.gate_count = 0
        # for checking top and bottom gates
        for j in range(self.col_count - 1): 
            if self.grid[0][j] in ('0', '2'):
                self.gate_count += 1
            if self.grid[self.row_count-1][j] in ('0'):
                self.gate_count += 1
                
        # for checking left and right gates
        for i in range(self.row_count - 1): 
            if self.grid[i][0] in ('0', '1'):
                self.gate_count += 1
            if self.grid[i][self.col_count-1] in ('0'):
                self.gate_count += 1
        
    # creates a grid array (self.maze) to represent each cell in the maze
    def get_maze(self):
        self.maze_rows = self.row_count-1
        self.maze_cols = self.col_count-1
        self.maze = [[[] for _ in range(self.maze_cols)] for _ in range(self.maze_rows)]  
        # finds values of cells on the basis of 3 nodes: 2 top nodes and 1 bottom left node
        # and assigns a hexadecimal value for different combinations
        for i in range(self.maze_rows):
            for j in range(self.maze_cols):
                top = left = right = bottom = 0 # means no line present
                top = (self.grid[i][j] in ('1', '3'))
                left = (self.grid[i][j] in ('2', '3'))
                right = (self.grid[i][j+1] in ('2', '3'))
                bottom = (self.grid[i+1][j] in ('1', '3'))
                if (top == 0 and left == 0 and right == 0 and bottom == 0):
                    self.maze[i][j] = '0'
                elif (top == 0 and left == 0 and right == 0 and bottom == 1):
                    self.maze[i][j] = '1'  
                elif (top == 0 and left == 0 and right == 1 and bottom == 0):
                    self.maze[i][j] = '2'  
                elif (top == 0 and left == 0 and right == 1 and bottom == 1):
                    self.maze[i][j] = '3'  
                elif (top == 0 and left == 1 and right == 0 and bottom == 0):
                    self.maze[i][j] = '4'  
                elif (top == 0 and left == 1 and right == 0 and bottom == 1):
                    self.maze[i][j] = '5' 
                elif (top == 0 and left == 1 and right == 1 and bottom == 0):
                    self.maze[i][j] = '6' 
                elif (top == 0 and left == 1 and right == 1 and bottom == 1):
                    self.maze[i][j] = '7'  
                elif (top == 1 and left == 0 and right == 0 and bottom == 0):
                    self.maze[i][j] = '8'  
                elif (top == 1 and left == 0 and right == 0 and bottom == 1):
                    self.maze[i][j] = '9'  
                elif (top == 1 and left == 0 and right == 1 and bottom == 0):
                    self.maze[i][j] = 'A'  
                elif (top == 1 and left == 0 and right == 1 and bottom == 1):
                    self.maze[i][j] = 'B' 
                elif (top == 1 and left == 1 and right == 0 and bottom == 0):
                    self.maze[i][j] = 'C'
                elif (top == 1 and left == 1 and right == 0 and bottom == 1):
                    self.maze[i][j] = 'D'
                elif (top == 1 and left == 1 and right == 1 and bottom == 0):
                    self.maze[i][j] = 'E'
                elif (top == 1 and left == 1 and right == 1 and bottom == 1):
                    self.maze[i][j] = 'F'
                    
        # self.area and self.visited will be used to identify different areas of the maze
        # self.area is a grid of same size as maze and contains a number representing each area
        self.area = [[[] for _ in range(self.maze_cols)] for _ in range(self.maze_rows)] 
        self.visited = [[[] for _ in range(self.maze_cols)] for _ in range(self.maze_rows)] 
        for i in range(self.maze_rows):
            for j in range(self.maze_cols):
                self.area[i][j] = 0
                self.visited[i][j] = 0
    
    ### Plagiarism Comment: I have used a similar method of below type in my program for Quiz 6
    ### and both of these programs are created by me only. I have used recursion technique
    ### to find and categorize all cells connected to each other
    # divides the maze into distinct areas
    def get_area(self, m, n):
        if self.visited[m][n] == 0: # only checks unvisited cells
            self.visited[m][n] = 1 # sets to visited         
        
            if m != 0: # don't check this case for TOPmost row
                # checks if no edge at top of cell-> can go to top
                # (m-1, n) is the cell on top of (m, n)
                if self.maze[m][n] in ('0','1','2','3','4','5','6','7'):
                    if self.visited[m-1][n] == 0: # only goes to non-visited cells
                        self.area[m-1][n] = self.area[m][n] # set area of new cell same as current
                        self.get_area(m-1, n)
                        
            if n != 0: # don't check this case for LEFTmost column
                # checks if no edge at left of cell-> can go to left
                # (m, n-1) is the cell on left of (m, n)
                if self.maze[m][n] in ('0','1','2','3','8','9','A','B'):
                    if self.visited[m][n-1] == 0:
                        self.area[m][n-1] = self.area[m][n]
                        self.get_area(m, n-1)
                        
            if n != self.maze_cols-1: # don't check this case for RIGHTmost column
                # checks if no edge at right of cell-> can go to right
                # (m, n+1) is the cell on right of (m, n)
                if self.maze[m][n] in ('0','1','4','5','8','9','C','D'):
                    if self.visited[m][n+1] == 0:
                        self.area[m][n+1] = self.area[m][n]
                        self.get_area(m, n+1)
                        
            if m != self.maze_rows-1: # don't check this case for BOTTOMmost row
                # checks if no edge at bottom of cell-> can go to bottom
                # (m+1, n) is the cell on bottom of (m, n)
                if self.maze[m][n] in ('0','2','4','6','8','A','C','E'):
                    if self.visited[m+1][n] == 0:
                        self.area[m+1][n] = self.area[m][n]
                        self.get_area(m+1, n)
            
    # checks which areas of the maze are accessible
    def get_accessible_area(self):
        self.gate_cells = [] # to store points of gate cells
        for j in range(1, self.maze_cols-1): # for top row
            if self.maze[0][j] in ('0','1','2','3','4','5','6','7'):
                self.gate_cells.append((0,j))
                
        for i in range(1, self.maze_rows-1): # for left column
            if self.maze[i][0] in ('0','1','2','3','8','9','A','B'):
                self.gate_cells.append((i, 0))
                
        for i in range(1, self.maze_rows-1): # for right column
            if self.maze[i][self.maze_cols-1] in ('0','1','4','5','8','9','C','D'):
                self.gate_cells.append((i, self.maze_cols-1))
                
        for j in range(1, self.maze_cols-1): # for bottom row
            if self.maze[self.maze_rows-1][j] in ('0','2','4','6','8','A','C','E'):
                self.gate_cells.append((self.maze_rows-1, j))
                
        if self.maze[0][0] in ('0','1','2','3','4','5','6','7','8','9','A','B'): # top-left
            self.gate_cells.append((0, 0))
            
        if self.maze[0][self.maze_cols-1] in ('0','1','2','3','4','5','6','7','8','9','C','D'): # top-right
            self.gate_cells.append((0, self.maze_cols-1))
            
        if self.maze[self.maze_rows-1][0] in ('0','2','4','6','8','A','C','E', '1','3','9','B'): # bottom-left
            self.gate_cells.append((self.maze_rows-1, 0))
            
        if self.maze[self.maze_rows-1][self.maze_cols-1] in ('0','2','4','6','8','A','C','E', '1','5','9','D'): 
            self.gate_cells.append((self.maze_rows-1, self.maze_cols-1)) # bottom-right
                
        # list self.area_status will tell whether each area is accessible or not
        self.area_status = [0 for _ in range(self.area_count + 1)] # 0 means NOT accessible        
        
        # sets status to 1 for areas that are accessible
        for e, v in self.gate_cells:
            self.area_status[self.area[e][v]] = 1 # 1 means accessible
        
        self.accessible_area_count = 0        
        for e in self.area_status:
            if e == 1:
                self.accessible_area_count += 1
            
    # counts number of cells/points in INaccessible areas
    def get_inaccessible_points(self):
        self.inaccessible_points = 0
        for i in range(self.maze_rows):
            for j in range(self.maze_cols):
                # checks if the cell is accessible or not and update count for inaccessible cells
                if self.area_status[self.area[i][j]] == 0: 
                    self.inaccessible_points += 1
                    
                    
    # creates a grid self.walls that will assign a number to each distinct wall
    def get_walls(self):
        self.walls = [[[] for _ in range(self.col_count)] for _ in range(self.row_count)] 
        self.walls_visited = [[[] for _ in range(self.col_count)] for _ in range(self.row_count)] 
        for i in range(self.row_count):
            for j in range(self.col_count):
                self.walls[i][j] = -1
                self.walls_visited[i][j] = 0 # 0 means not visited
                
        # assign numbers to distinct walls in the maze
        self.wall_count = -1
        for i in range(self.row_count):
            for j in range(self.col_count):
                if self.walls_visited[i][j] == 0:
                    if (self.grid[i][j] in ('1', '2', '3')): # points connected to walls
                        self.wall_count += 1
                        self.walls[i][j] = self.wall_count
                        self.get_set_of_walls(i, j)
                    else:
                        self.walls_visited[i][j] = 1 # for unconnected node                        
        self.wall_count += 1 # adding 1 as wall numbers start from 0
        
    ### Plagiarism Comment: I have used a similar method of below type in my program for Quiz 6
    ### and both of these programs are created by me only. I have used recursion technique
    ### to find all sets of walls connected to each other
    # updates grid self.walls to assign a number to each distinct wall
    def get_set_of_walls(self, m, n):
        if self.walls_visited[m][n] == 0: # only checks unvisited cells
            self.walls_visited[m][n] = 1                       
        
            if m != 0: # don't check this case for TOP row
                # checks if current node (m, n) is connected to top node (m-1, n)
                if self.grid[m-1][n] in ('2','3'):
                    if self.walls_visited[m-1][n] == 0: # only checks unvisited nodes
                        # assigns number to next (top) node same as current one
                        self.walls[m-1][n] = self.walls[m][n] 
                        self.get_set_of_walls(m-1, n)
                        
            if n != 0: # don't check this case for LEFT column
                # checks if current node (m, n) is connected to left node (m, n-1)
                if self.grid[m][n-1] in ('1', '3'):
                    if self.walls_visited[m][n-1] == 0:
                        self.walls[m][n-1] = self.walls[m][n]
                        self.get_set_of_walls(m, n-1)
                        
            if n != self.col_count-1: # don't check this case for RIGHT column
                # checks if current node (m, n) is connected to right node (m, n+1)
                if self.grid[m][n] in ('1', '3'):
                    if self.walls_visited[m][n+1] == 0:
                        self.walls[m][n+1] = self.walls[m][n]
                        self.get_set_of_walls(m, n+1)
                        
            if m != self.row_count-1: # don't check this case for BOTTOM row
                # checks if current node (m, n) is connected to bottom node (m+1, n)
                if self.grid[m][n] in ('2','3'):
                    if self.walls_visited[m+1][n] == 0:
                        self.walls[m+1][n] = self.walls[m][n]
                        self.get_set_of_walls(m+1, n)
                        
                        
    # functions to create and store data for cul-de-sacs
    def create_cul_de_sac_grid(self):
        # creating grids to represent cul_de_sacs data
        self.cul_de_sacs = [[0 for _ in range(self.maze_cols)] for _ in range(self.maze_rows)] 
        self.cul_visited = [[0 for _ in range(self.maze_cols)] for _ in range(self.maze_rows)] 
        
        # to populate initial cul-de-sacs in grid self.cul_de_sacs
        for i in range(self.maze_rows):
            for j in range(self.maze_cols):
                if self.area_status[self.area[i][j]] == 1: # ignore inaccessible
                    if self.maze[i][j] in ('7','B','D','E'):
                        self.cul_de_sacs[i][j] = 1
        
        # to populate all cul-de-sacs in grid self.cul_de_sacs connected to initial cul-de-sacs
        for i in range(self.maze_rows):
            for j in range(self.maze_cols):
                # only checks unvisited cells and where initial cul_de_sac is present
                if (self.cul_visited[i][j] == 0 and self.cul_de_sacs[i][j] == 1): 
                    self.get_cul_de_sacs(i, j)
        
        # creating grid to store distinct numbers for each cul-de-sac area
        self.area_cul_de_sacs = [[-1 for _ in range(self.maze_cols)] for _ in range(self.maze_rows)] 
                                 
        # divide all cul-de-sacs into distinct areas
        self.cul_de_sacs_count = -1        
        for i in range(self.maze_rows):
            for j in range(self.maze_cols):
                # only checks cells where cul-de-sac is present and area_cul_de_sacs NOT visited
                if (self.cul_de_sacs[i][j] == 1 and self.area_cul_de_sacs[i][j] == -1): 
                    self.cul_de_sacs_count += 1
                    self.area_cul_de_sacs[i][j] = self.cul_de_sacs_count
                    self.get_accessible_cul_de_sacs(i, j)
                         
        # adding 1 as numbers start from 0
        self.accessible_cul_de_sacs_count = self.cul_de_sacs_count+1 
        

    # to identify all the cul-de-sacs in the maze 
    def get_cul_de_sacs(self, m, n):
        
        side_count = 0            
        # Check TOP empty: go to Top but not for top row
        if self.maze[m][n] in ('0','1','2','3','4','5','6','7'):
            if m == 0:
                side_count += 1
                next_m = -1    # can't go outside maze from outer layer, so assigning -1
                next_n = -1
            # only checks if next cell is not visited, ignores cells where cul-de-sac is there
            elif self.cul_de_sacs[m-1][n] == 0: 
                side_count += 1
                next_m = m-1
                next_n = n
            
        # Check LEFT empty- not for left column            
        if self.maze[m][n] in ('0','1','2','3','8','9','A','B'):
            if n == 0:
                side_count += 1
                next_m = -1
                next_n = -1
            elif self.cul_de_sacs[m][n-1] == 0: 
                side_count += 1
                next_m = m  
                next_n = n-1
            
        # Check RIGHT empty- not for right column                
        if self.maze[m][n] in ('0','1','4','5','8','9','C','D'):
            if n == self.maze_cols-1:
                side_count += 1
                next_m = -1
                next_n = -1
            elif self.cul_de_sacs[m][n+1] == 0: 
                side_count += 1
                next_m = m
                next_n = n+1
                            
        # Check BOTTOM empty- not for bottom row                
        if self.maze[m][n] in ('0','2','4','6','8','A','C','E'):
            if m == self.maze_rows-1:
                side_count += 1
                next_m = -1
                next_n = -1
            elif self.cul_de_sacs[m+1][n] == 0: 
                side_count += 1
                next_m = m+1
                next_n = n
                
        # cul-de-sac is there if there is only 1 path out of cell
        if side_count == 1:
            self.cul_de_sacs[m][n] = 1 # 1- cul-de-sac present, 0- no cul-de-sac         
            self.cul_visited[m][n] = 1               
            if next_m != -1:
                self.get_cul_de_sacs(next_m, next_n)
            
            
    ### Plagiarism Comment: I have used a similar method of below type in my program for Quiz 6
    ### and both of these programs are created by me only. I have used recursion technique
    ### to find all accessible cul-de-sacs that are connected to each other
    # assigns distinct numbers to each cul-de-sac area in the maze
    def get_accessible_cul_de_sacs(self, m, n):
            
        if m != 0: # don't check this case for TOP row
            if self.maze[m][n] in ('0','1','2','3','4','5','6','7'):
                # only checks cells with cul-de-sacs and for which area is not updated/visited
                if self.cul_de_sacs[m-1][n] == 1 and self.area_cul_de_sacs[m-1][n] == -1:
                    self.area_cul_de_sacs[m-1][n] = self.area_cul_de_sacs[m][n]
                    self.get_accessible_cul_de_sacs(m-1, n)
                        
        if n != 0: # don't check this case for LEFT column
            if self.maze[m][n] in ('0','1','2','3','8','9','A','B'):
                if self.cul_de_sacs[m][n-1] == 1 and self.area_cul_de_sacs[m][n-1] == -1:
                    self.area_cul_de_sacs[m][n-1] = self.area_cul_de_sacs[m][n]
                    self.get_accessible_cul_de_sacs(m, n-1)
                        
        if n != self.maze_cols-1: # don't check this case for RIGHT column
            if self.maze[m][n] in ('0','1','4','5','8','9','C','D'):
                if self.cul_de_sacs[m][n+1] == 1 and self.area_cul_de_sacs[m][n+1] == -1:
                    self.area_cul_de_sacs[m][n+1] = self.area_cul_de_sacs[m][n]
                    self.get_accessible_cul_de_sacs(m, n+1)
                        
        if m != self.maze_rows-1: # don't check this case for BOTTOM row
            if self.maze[m][n] in ('0','2','4','6','8','A','C','E'):
                if self.cul_de_sacs[m+1][n] == 1 and self.area_cul_de_sacs[m+1][n] == -1:
                    self.area_cul_de_sacs[m+1][n] = self.area_cul_de_sacs[m][n]
                    self.get_accessible_cul_de_sacs(m+1, n)
    
    
    # to identify entry-exit paths in the maze
    def get_entry_exit_path_count(self):
        # to get number of entry-exit paths
        #print(self.gate_cells)
        self.gate_cells = set(self.gate_cells) # removes duplicate values
        self.entry_exit_paths = 0
        self.entry_exit_gate_cells = [] # to store gate cells on entry-exit paths only
        for i, j in self.gate_cells: # checks path from each gate
            self.get_entry_exit_paths(i, j, -1, -1) 
        self.entry_exit_paths= int(self.entry_exit_paths/2) # all paths considered twice
        
    
    # to identify any entry-exit path in the maze
    def get_entry_exit_paths(self, m, n, prev_m, prev_n):
        
        side_count = 0
        next_m = -1
        next_n = -1
            
        # Check TOP empty: go to Top but not for top row
        if self.maze[m][n] in ('0','1','2','3','4','5','6','7'):
            if m == 0:
                side_count += 1
            # cannot go to a cell with cul-de-sac
            elif self.cul_de_sacs[m-1][n] == 0: 
                side_count += 1
                if prev_m != m-1 or prev_n != n: # checks that next cell is not previous
                    next_m = m-1
                    next_n = n
            
        # Check LEFT empty- not for left column            
        if self.maze[m][n] in ('0','1','2','3','8','9','A','B'):
            if n == 0:
                side_count += 1
            elif self.cul_de_sacs[m][n-1] == 0: 
                side_count += 1
                if prev_m != m or prev_n != n-1:
                    next_m = m  
                    next_n = n-1
            
        # Check RIGHT empty- not for right column                
        if self.maze[m][n] in ('0','1','4','5','8','9','C','D'):
            if n == self.maze_cols-1:
                side_count += 1
            elif self.cul_de_sacs[m][n+1] == 0: 
                side_count += 1
                if prev_m != m or prev_n != n+1:
                    next_m = m
                    next_n = n+1
                            
        # Check BOTTOM empty- not for bottom row                
        if self.maze[m][n] in ('0','2','4','6','8','A','C','E'):
            if m == self.maze_rows-1:
                side_count += 1
            elif self.cul_de_sacs[m+1][n] == 0: 
                side_count += 1
                if prev_m != m+1 or prev_n != n:
                    next_m = m+1
                    next_n = n
                                     
        # path is there for a cell if there is only one entry and exit 
        if side_count == 2:
            # path ends if a gate cell is reached and is not same as previous cell
            if (m,n) in self.gate_cells and prev_m != -1: 
                self.entry_exit_paths += 1
                self.entry_exit_gate_cells.append((m,n)) # store the gate cell        
            # checks for path with only 1 cell- gate cell, no previous or next cell
            elif (m,n) in self.gate_cells and prev_m == -1 and next_m == -1:
                self.entry_exit_paths += 2
                self.entry_exit_gate_cells.append((m,n))
            else:
                self.get_entry_exit_paths(next_m, next_n, m, n) # moves to next cell
            
            
    # to print the final stats of the maze
    def print_final_stats(self):
        
        # to display number of gates
        if self.gate_count == 0:
            print("The maze has no gate.")
        elif self.gate_count == 1:
            print("The maze has a single gate.")
        else:
            print(f"The maze has {self.gate_count} gates.")            
            
        # to display number of walls        
        if self.wall_count == 0:
            print("The maze has no wall.")
        elif self.wall_count == 1:
            print("The maze has walls that are all connected.")
        else:
            print(f"The maze has {self.wall_count} sets of walls that are all connected.")
            
        # to display count of inaccessible inner points
        if self.inaccessible_points == 0:
            print("The maze has no inaccessible inner point.")
        elif self.inaccessible_points == 1:
            print("The maze has a unique inaccessible inner point.")
        else:
            print(f"The maze has {self.inaccessible_points} inaccessible inner points.")
        
        # to display count of accessible areas
        if self.accessible_area_count == 0:
            print("The maze has no accessible area.")
        elif self.accessible_area_count == 1:
            print("The maze has a unique accessible area.")
        else:
            print(f"The maze has {self.accessible_area_count} accessible areas.")
            
        # to display count of accessible cul-de-sacs
        if self.accessible_cul_de_sacs_count == 0:
            print("The maze has no accessible cul-de-sac.")
        elif self.accessible_cul_de_sacs_count == 1:
            print("The maze has accessible cul-de-sacs that are all connected.")
        else:
            print(f"The maze has {self.accessible_cul_de_sacs_count} sets of accessible cul-de-sacs that are all connected.")
         
        # to display number of entry-exit paths        
        if self.entry_exit_paths == 0:
            print("The maze has no entry-exit path with no intersection not to cul-de-sacs.")
        elif self.entry_exit_paths == 1:
            print("The maze has a unique entry-exit path with no intersection not to cul-de-sacs.")
        else:
            print(f"The maze has {self.entry_exit_paths} entry-exit paths with no intersections not to cul-de-sacs.")
            
            
            
########################### methods for maze.display() only ###########################    


    # to identify any entry-exit path in the maze
    def get_entry_exit_path_cells(self, m, n, prev_m, prev_n):
        
        side_count = 0
        next_m = -1
        next_n = -1
            
        # Check TOP empty: go to Top but not for top row
        if self.maze[m][n] in ('0','1','2','3','4','5','6','7'):
            if m == 0:
                side_count += 1
            # cannot go to a cell with cul-de-sac
            elif self.cul_de_sacs[m-1][n] == 0: 
                side_count += 1
                if prev_m != m-1 or prev_n != n: # checks that next cell is not previous
                    next_m = m-1
                    next_n = n
            
        # Check LEFT empty- not for left column            
        if self.maze[m][n] in ('0','1','2','3','8','9','A','B'):
            if n == 0:
                side_count += 1
            elif self.cul_de_sacs[m][n-1] == 0: 
                side_count += 1
                if prev_m != m or prev_n != n-1:
                    next_m = m  
                    next_n = n-1
            
        # Check RIGHT empty- not for right column                
        if self.maze[m][n] in ('0','1','4','5','8','9','C','D'):
            if n == self.maze_cols-1:
                side_count += 1
            elif self.cul_de_sacs[m][n+1] == 0: 
                side_count += 1
                if prev_m != m or prev_n != n+1:
                    next_m = m
                    next_n = n+1
                            
        # Check BOTTOM empty- not for bottom row                
        if self.maze[m][n] in ('0','2','4','6','8','A','C','E'):
            if m == self.maze_rows-1:
                side_count += 1
            elif self.cul_de_sacs[m+1][n] == 0: 
                side_count += 1
                if prev_m != m+1 or prev_n != n:
                    next_m = m+1
                    next_n = n
                                     
        # path is there for a cell if there is only one entry and exit 
        if side_count == 2:
            self.area_entry_exit[m][n] = 1
            if next_m != -1:
                self.get_entry_exit_path_cells(next_m, next_n, m, n) # moves to next cell
            
            
    # to find which paths we can go to and from for entry-exit path cells
    def get_entry_exit_path_orientation(self):
                    
        # finds orientation of entry-exit cells based on where they can lead to
        for i in range(self.maze_rows):
            for j in range(self.maze_cols):
                if self.area_entry_exit[i][j] == 1:
                   
                    top = left = right = bottom = 0 # means no line present
                    
                    if i == 0:
                        top = (self.grid[i][j] in ('1', '3'))
                    else:
                        top = (self.grid[i][j] in ('1', '3') or self.cul_de_sacs[i-1][j] == 1)
                    
                    if j == 0:
                        left = (self.grid[i][j] in ('2', '3'))
                    else:
                        left = (self.grid[i][j] in ('2', '3') or self.cul_de_sacs[i][j-1] == 1)
                    
                    if j == self.maze_cols-1:
                        right = (self.grid[i][j+1] in ('2', '3'))
                    else:
                        right = (self.grid[i][j+1] in ('2', '3') or self.cul_de_sacs[i][j+1] == 1)
                    
                    if i == self.maze_rows-1:
                        bottom = (self.grid[i+1][j] in ('1', '3'))
                    else:
                        bottom = (self.grid[i+1][j] in ('1', '3') or self.cul_de_sacs[i+1][j] == 1)
                        
                    if (top == 0 and left == 0 and right == 0 and bottom == 0):
                        self.area_entry_exit[i][j] = '0'
                    elif (top == 0 and left == 0 and right == 0 and bottom == 1):
                        self.area_entry_exit[i][j] = '1'  
                    elif (top == 0 and left == 0 and right == 1 and bottom == 0):
                        self.area_entry_exit[i][j] = '2'  
                    elif (top == 0 and left == 0 and right == 1 and bottom == 1):
                        self.area_entry_exit[i][j] = '3'  
                    elif (top == 0 and left == 1 and right == 0 and bottom == 0):
                        self.area_entry_exit[i][j] = '4'  
                    elif (top == 0 and left == 1 and right == 0 and bottom == 1):
                        self.area_entry_exit[i][j] = '5' 
                    elif (top == 0 and left == 1 and right == 1 and bottom == 0):
                        self.area_entry_exit[i][j] = '6' 
                    elif (top == 0 and left == 1 and right == 1 and bottom == 1):
                        self.area_entry_exit[i][j] = '7'  
                    elif (top == 1 and left == 0 and right == 0 and bottom == 0):
                        self.area_entry_exit[i][j] = '8'  
                    elif (top == 1 and left == 0 and right == 0 and bottom == 1):
                        self.area_entry_exit[i][j] = '9'  
                    elif (top == 1 and left == 0 and right == 1 and bottom == 0):
                        self.area_entry_exit[i][j] = 'A'  
                    elif (top == 1 and left == 0 and right == 1 and bottom == 1):
                        self.area_entry_exit[i][j] = 'B' 
                    elif (top == 1 and left == 1 and right == 0 and bottom == 0):
                        self.area_entry_exit[i][j] = 'C'
                    elif (top == 1 and left == 1 and right == 0 and bottom == 1):
                        self.area_entry_exit[i][j] = 'D'
                    elif (top == 1 and left == 1 and right == 1 and bottom == 0):
                        self.area_entry_exit[i][j] = 'E'
                    elif (top == 1 and left == 1 and right == 1 and bottom == 1):
                        self.area_entry_exit[i][j] = 'F'
                
        
    
    # to write the commands into tex file to generate pdf    
    def display(self):
        
        # call function to create a grid to represent all the cells in the maze
        self.get_maze()
        
        # assign numbers to distinct areas in the maze
        self.area_count = -1
        for i in range(self.maze_rows):
            for j in range(self.maze_cols):
                if self.visited[i][j] == 0:
                    self.area_count += 1
                    self.area[i][j] = self.area_count
                    self.get_area(i, j)
                
        # call function to find which areas are accessible
        self.get_accessible_area()
        
        # call function to create and store data for cul-de-sacs
        self.create_cul_de_sac_grid()
        
        # to identify entry-exit paths in the maze
        self.get_entry_exit_path_count()
        
        newFile = self.fileName [:-4] + ".tex" # removing '.txt' from original filename
        
        # write the commands in tex file to generate pdf
        f = open(newFile, "w")
        f.write("\\documentclass[10pt]{article}\n")
        f.write("\\usepackage{tikz}\n")
        f.write("\\usetikzlibrary{shapes.misc}\n")
        f.write("\\usepackage[margin=0cm]{geometry}\n")
        f.write("\\pagestyle{empty}\n")
        f.write("\\tikzstyle{every node}=[cross out, draw, red]\n")
        f.write("\n")
        f.write("\\begin{document}\n")
        f.write("\n")
        f.write("\\vspace*{\\fill}\n")
        f.write("\\begin{center}\n")
        f.write("\\begin{tikzpicture}[x=0.5cm, y=-0.5cm, ultra thick, blue]\n")
        
        # to draw walls
        f.write("% Walls\n")
        
        # to add horizontal walls
        i = j = 0 
        while((i == self.row_count and j == 0) is False):
            if self.grid[i][j] in ('1', '3'): # checks for horizontal line
                count = 1
                while (self.grid[i][j+count] in ('1', '3')):
                    count += 1
                f.write(f"    \\draw ({j},{i}) -- ({j+count},{i});\n")
                j += count
            j += 1 # moves to next point to check
            if j == self.col_count: # reached at the end of a row
                i += 1      # moves to next row
                j = 0       # set column pointer to start of row
        
        # to add vertical walls
        i = j = 0 
        while((i == 0 and j == self.col_count) is False):
            if self.grid[i][j] in ('2', '3'): # checks for vertical line
                count = 1
                while (self.grid[i+count][j] in ('2', '3')):
                    count += 1
                f.write(f"    \\draw ({j},{i}) -- ({j},{i+count});\n")
                i += count
            i += 1 # moves to next point to check
            if i == self.row_count: # reached at the end of a column
                j += 1      # moves to next column
                i = 0       # set row pointer to start of column  
            
        
        # to draw pillars
        f.write("% Pillars\n")
        for i in range(self.row_count):
            for j in range(self.col_count):
                wall_count = 0
                if self.grid[i][j] in ('1', '2', '3'): # checks if no wall coming from this node
                    wall_count = 1
                if i != 0: # checks for wall from top node to current
                    if self.grid[i-1][j] in ('2', '3'):
                        wall_count = 1
                if j != 0: # checks for wall from left node to current
                    if self.grid[i][j-1] in ('1', '3'):
                        wall_count = 1
                if wall_count == 0:
                    f.write(f"    \\fill[green] ({j},{i}) circle(0.2);\n")
                    
        
        # to draw inner points in accessible cul-de-sacs
        f.write("% Inner points in accessible cul-de-sacs\n")
        for i in range(self.maze_rows):
            for j in range(self.maze_cols):
                if self.cul_de_sacs[i][j] == 1: # checks if cell contains cul-de-sac
                    f.write(f"    \\node at ({j+0.5},{i+0.5}) ")
                    f.write("{};\n")
                    
        
        # to draw entry-exit paths
        f.write("% Entry-exit paths without intersections\n")
        
        # creating grid to store numbers for each cell in an entry-exit path
        self.area_entry_exit = [[0 for _ in range(self.maze_cols+1)] for _ in range(self.maze_rows+1)] 
                  
        for i, j in self.entry_exit_gate_cells:
            self.get_entry_exit_path_cells(i, j, -1, -1)
          
        self.get_entry_exit_path_orientation()
        
        # to add cells in horizontal entry-exit paths
        i = j = 0 
        while((i == self.maze_rows and j == 0) is False):
            if self.area_entry_exit[i][j] in ('3', '5', '9', 'A', 'C'): # checks for horizontal line
                count = 1
                while (self.area_entry_exit[i][j+count] in ('3', '9', 'A')):
                    count += 1                      
                if count == 1: # for only 1 horizontal cell in first or last column
                    if j == 0 and self.grid[i][j] in ('0','1'):
                        f.write(f"    \\draw[dashed, yellow] ({j-0.5},{i+0.5}) -- ({j+count-0.5},{i+0.5});\n")
                    elif j == self.maze_cols-1 and self.grid[i][j+1] in ('0','1'):
                        f.write(f"    \\draw[dashed, yellow] ({j+0.5},{i+0.5}) -- ({j+count+0.5},{i+0.5});\n")
                else:
                    # both sides open 
                    if (j==0 and self.grid[i][j] in ('0','1')) and ((j+count-1)==self.maze_cols-1 and self.grid[i][j+count] in ('0','1')):
                        f.write(f"    \\draw[dashed, yellow] ({j-0.5},{i+0.5}) -- ({j+count+0.5},{i+0.5});\n")
                    # only left side open 
                    elif (j==0 and self.grid[i][j] in ('0','1')) and ((j+count-1)!=self.maze_cols-1 or self.grid[i][j+count] in ('2','3')):
                        f.write(f"    \\draw[dashed, yellow] ({j-0.5},{i+0.5}) -- ({j+count-0.5},{i+0.5});\n")
                    # only right side open 
                    elif (j!=0 or self.grid[i][j] in ('2','3')) and ((j+count-1)==self.maze_cols-1 and self.grid[i][j+count] in ('0','1')):
                        f.write(f"    \\draw[dashed, yellow] ({j+0.5},{i+0.5}) -- ({j+count+0.5},{i+0.5});\n")
                    # both sides closed 
                    else:
                        f.write(f"    \\draw[dashed, yellow] ({j+0.5},{i+0.5}) -- ({j+count-0.5},{i+0.5});\n")
                j += count-1
            j += 1 # moves to next point to check
            if j == self.maze_cols: # reached at the end of a row
                i += 1      # moves to next row
                j = 0       # set column pointer to start of row
        
        # to add cells in horizontal entry-exit paths
        i = j = 0 
        while((i == 0 and j == self.maze_cols) is False):
            if self.area_entry_exit[i][j] in ('3', '5', '6', 'A', 'C'): # checks for vertical line
                count = 1
                while (self.area_entry_exit[i+count][j] in ('3', '5', '6')):
                    count += 1                      
                if count == 1: # for only 1 horizontal cell in first or last column
                    if i == 0 and self.grid[i][j] in ('0','2'):
                        f.write(f"    \\draw[dashed, yellow] ({j+0.5},{i-0.5}) -- ({j+0.5},{i+count-0.5});\n")
                    elif i == self.maze_rows-1 and self.grid[i+1][j] in ('0','2'):
                        f.write(f"    \\draw[dashed, yellow] ({j+0.5},{i+0.5}) -- ({j+0.5},{i+count+0.5});\n")
                else:
                    # both sides open 
                    if (i==0 and self.grid[i][j] in ('0','2')) and ((i+count-1)==self.maze_rows-1 and self.grid[i+count][j] in ('0','2')):
                        f.write(f"    \\draw[dashed, yellow] ({j+0.5},{i-0.5}) -- ({j+0.5},{i+count+0.5});\n")
                    # only left side open 
                    elif (i==0 and self.grid[i][j] in ('0','2')) and ((i+count-1)!=self.maze_rows-1 or self.grid[i+count][j] in ('1','3')):
                        f.write(f"    \\draw[dashed, yellow] ({j+0.5},{i-0.5}) -- ({j+0.5},{i+count-0.5});\n")
                    # only right side open 
                    elif (i!=0 or self.grid[i][j] in ('1','3')) and ((i+count-1)==self.maze_rows-1 and self.grid[i+count][j] in ('0','2')):
                        f.write(f"    \\draw[dashed, yellow] ({j+0.5},{i+0.5}) -- ({j+0.5},{i+count+0.5});\n")
                    # both sides closed 
                    else:
                        f.write(f"    \\draw[dashed, yellow] ({j+0.5},{i+0.5}) -- ({j+0.5},{i+count-0.5});\n")
                i += count-1
            i += 1 # moves to next point to check
            if i == self.maze_rows: # reached at the end of a row
                j += 1      # moves to next row
                i = 0       # set column pointer to start of row
        
        
        f.write("\\end{tikzpicture}\n")
        f.write("\\end{center}\n")
        f.write("\\vspace*{\\fill}\n")
        f.write("\n")
        f.write("\\end{document}\n")
        f.close()
        
        

