
import time
import sys

def please_convert():
    str = input('How can I help you? ')
    time.sleep(0.001)
    
    #print("Input is", str)
    
    # Removing extra spaces
    while '  '  in str:
        str = str.replace("  ", " ")    
    if str[0] == ' ':
        str = str.replace(" ", "", 1)        
    if str[-1] == ' ':
        str = str [:len(str)-1]
        
    #print("Input is", str)
    
    # Checking for valid format of the input string
    input_str = str[:15]
    input_method = str[15:]
    
    #print("input_str is", input_str)
    #print("input_method is", input_method)
    
    status = 1
    
    if input_str.lower() == 'exit':
        sys.exit(0)
    
    if input_str != 'Please convert ':
        print("I don't get what you want, sorry mate!")
        status = 0
        #sys.exit(0)
        
    if status == 1:
        no_of_spaces = 0
        for i in range(len(input_method)):
            if input_method[i] == ' ':
                no_of_spaces += 1
        
        # Comparing input formats as per all 3 methods
        if no_of_spaces == 0:
            convert_method_1(input_method)
        elif no_of_spaces == 2:
            if input_method[0] != ' ' and input_method[-1] != ' ' and ' using ' in input_method:
                input_2_strings = input_method.split(' using ')
                input_str1 = input_2_strings[0]
                input_str2 = input_2_strings[1]
                convert_method_2(input_str1, input_str2)
            else:
                print("I don't get what you want, sorry mate!")
        elif no_of_spaces == 1:
            if input_method[-10:] == ' minimally':
                input_str = input_method[:-10]
                convert_method_3(input_str)
            else:
                print("I don't get what you want, sorry mate!")
        else:
            print("I don't get what you want, sorry mate!")
            
        #print("Sure! It is", arabic)

def convert_method_1(input_string):
    # Method 1 input formatting check passed
    #print(input_string)
    formula_values = {'I':1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}  
    formula = {1: 'I', 5: 'V', 10: 'X', 50: 'L', 100: 'C', 500: 'D', 1000: 'M'}      
    if (method_1_validity_check(input_string, formula_values)):
        if input_string.isnumeric():
            roman_output = arabic_to_roman(input_string, formula)
            print("Sure! It is", roman_output) 
        else:
            arabic_output = roman_to_arabic(input_string, formula_values) # convert value for correct input
            print("Sure! It is", arabic_output) 
    else:
        print("Hey, ask me something that's not impossible to do!") # validity check failed
        

def method_1_validity_check(input_string, values):
    if input_string.isnumeric() : # to check validity of arabic input # CHANGE int(), not reliable
        if input_string[0] == '0':
            #print("Failed at Pass 1")
            return False
        elif int(input_string) > 3999:
            #print("Failed at Pass 2")
            return False
        else:
            return True # indicating input string is an integer
    for i in range(len(input_string)):
         if input_string[i] not in ('I', 'V', 'X', 'L', 'C', 'D', 'M'):
             #print("Failed at Pass 3")
             return False       
    for i in range(len(input_string)-3):
        if (input_string[i] == input_string[i+1] == input_string[i+2] == input_string[i+3]) \
        and input_string[i] in ('I', 'X', 'C', 'M'): # Can't repeat more than 3 times
            #print("Failed at Pass 4")
            return False
    for i in range(len(input_string)-1):
        if (input_string[i] == input_string[i+1]) and input_string[i] in ('V', 'L', 'D'): # Can't repeat
            #print("Failed at Pass 5")
            return False
    #for i in range(len(input_string)-1):
        if input_string[i] == 'I' and input_string[i+1] not in ('I', 'V', 'X'): # Must be there
            #print("Failed at Pass 6")
            return False        
        if input_string[i] == 'X' and input_string[i+1] not in ('I', 'V', 'X', 'L', 'C'): # Must be there
            #print("Failed at Pass 7")
            return False 
        if input_string[i] == 'V' and input_string[i+1] in ('X', 'L', 'C', 'D', 'M'): # Must NOT be there
            #print("Failed at Pass 9")
            return False 
        if input_string[i] == 'L' and input_string[i+1] in ('C', 'D', 'M'): # Must NOT be there
            #print("Failed at Pass 10")
            return False 
        if input_string[i] == 'D' and input_string[i+1] in ('M'): # Must NOT be there
            #print("Failed at Pass 11")
            return False 
    
    for i in range(1, len(input_string)-1):
        if ( (input_string[i-1] == input_string[i+1]) and (values[input_string[i-1]] < values[input_string[i]]) ):
            #print("Failed at Pass 12") # Smaller value should NOT be there on both side of a bigger value
            return False                                                                                           
    
    return True # returns no if no validations failed
        

def arabic_to_roman(arabic, formula):
    # formula = {1: 'I', 5: 'V', 10: 'X', 50: 'L', 100: 'C', 500: 'D', 1000: 'M'}      
    # formula_values = {'I':1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}  
    
    if int(arabic) > 3999:
        print("Hey, ask me something that's not impossible to do!") # validity check failed
        sys.exit(0)
    
    keys = []
    for e in formula:
        keys.append(e)
    roman_output = ''
    arabic_numbers = []
    for i in range(len(arabic)):
        arabic_numbers.append( int(arabic[i]) * pow(10,len(arabic)-1-i) )
    
    for i in range(len(arabic_numbers)):
        if arabic_numbers[i] != 0:
            base = pow(10, len(str(arabic_numbers[i])) - 1 )
            
            if base == keys[-1]:
                roman_output += ( int((arabic_numbers[i]/base)) * formula[base] )
            else:
                if (arabic_numbers[i]/base) in (1, 2, 3):
                    roman_output += ( int((arabic_numbers[i]/base)) * formula[base] )
                elif (arabic_numbers[i]/base) == 4:
                    roman_output += formula[base] + formula[base*5]
                elif (arabic_numbers[i]/base) in (5, 6, 7, 8):
                    roman_output += formula[base*5] + ( (int((arabic_numbers[i]/base)) - 5) * formula[base] ) 
                elif (arabic_numbers[i]/base) == 9:
                    roman_output += formula[base] + formula[base*10]
                            
        #print(base, roman_output)
    
    return roman_output
    
    
def roman_to_arabic(roman, formula):
    arabic_output = []
    i = 0
    while i < len(roman):
        #print(i, arabic_value, formula[roman[i]])
        if i == len(roman) - 1:
            arabic_output.append(formula[roman[i]])
        elif formula[roman[i]] >= formula[roman[i+1]]:
            arabic_output.append(formula[roman[i]])
        else:
            arabic_output.append( (formula[roman[i+1]] - formula[roman[i]]) )
            if (i+2) < len(roman):
                i += 1
            else:
                break
        #print(arabic_output)
        if len(arabic_output) > 1:
            if arabic_output[-1] > arabic_output[-2]:
                print("Hey, ask me something that's not impossible to do!") # validity check failed
                sys.exit(0)
            
        i += 1 # next loop for calculating value of next numeral
        
    final_arabic_value = sum(arabic_output)
    
    # One last reverse check
    formula_reverse = {1: 'I', 5: 'V', 10: 'X', 50: 'L', 100: 'C', 500: 'D', 1000: 'M'}
    if roman != arabic_to_roman(str(final_arabic_value), formula_reverse):
        print("Hey, ask me something that's not impossible to do!") # validity check failed
        sys.exit(0)        
    return final_arabic_value 
    

    
def convert_method_2(input_str1, input_str2):
    if (method_2_validity_check(input_str1, input_str2)):
        if input_str1.isnumeric():
            roman_output = convert_using_to_roman(input_str1, input_str2)
            print("Sure! It is", roman_output) 
        else:
            arabic_output = convert_using_to_arabic(input_str1, input_str2) # convert value for correct input
            print("Sure! It is", arabic_output) 
    else:
        print("Hey, ask me something that's not impossible to do!") # validity check failed
    

def method_2_validity_check(input_str1, input_str2):
    if input_str2.isalpha(): # check 2nd string
        for i in range(len(input_str2)-1): # distinct check
            if input_str2[i] in input_str2[i+1:]:
                return False
    else:
        return False
    
    if input_str1.isalpha():
        for i in range(len(input_str1)): # checks if all characters of str1 are in str2 or not
            if input_str1[i] not in input_str2:
                return False
    
    if input_str1.isnumeric() and input_str1[0] != '0':
        return True
    elif input_str1.isalpha():
        return True
    else:
        return False
            
    return True # Returns True if no conditions failed

def convert_using_to_roman(arabic, formula_set):
    
    formula = {}
    maximum_number_allowed = 0
    
    for i in range(len(formula_set)-1, -1, -1):
        if (len(formula_set)-1-i) % 2 == 0:
            formula[int(pow(10, (len(formula_set)-1-i)/2))] = formula_set[i]
            maximum_number_allowed = int(4 * (int(pow(10, (len(formula_set)-1-i)/2))) - 1)
        if (len(formula_set)-1-i) % 2 == 1:
            formula[5 * (int( pow( 10, (len(formula_set)-1-i)//2) ) ) ] = formula_set[i]
            maximum_number_allowed = int(1.8 * (5 * (int( pow( 10, (len(formula_set)-1-i)//2) ) ) ) - 1)
    
    if int(arabic) > maximum_number_allowed:
        print("Hey, ask me something that's not impossible to do!") # validity check failed
        sys.exit(0)
        
    keys = []
    for e in formula:
        keys.append(e)
    roman_output = ''
    arabic_numbers = []
    
    for i in range(len(arabic)):
        arabic_numbers.append( int(arabic[i]) * pow(10,len(arabic)-1-i) )
    
    for i in range(len(arabic_numbers)):
        if arabic_numbers[i] != 0:
            base = pow(10, len(str(arabic_numbers[i])) - 1 )
            
            if base == keys[-1]:
                roman_output += ( int((arabic_numbers[i]/base)) * formula[base] )
            else:
                if (arabic_numbers[i]/base) in (1, 2, 3):
                    roman_output += ( int((arabic_numbers[i]/base)) * formula[base] )
                elif (arabic_numbers[i]/base) == 4:
                    roman_output += formula[base] + formula[base*5]
                elif (arabic_numbers[i]/base) in (5, 6, 7, 8):
                    roman_output += formula[base*5] + ( (int((arabic_numbers[i]/base)) - 5) * formula[base] ) 
                elif (arabic_numbers[i]/base) == 9:
                    roman_output += formula[base] + formula[base*10]
                            
    return roman_output

def convert_using_to_arabic(roman, formula_set):
    formula = {}   
    for i in range(len(formula_set)-1, -1, -1):
        if (len(formula_set)-1-i) % 2 == 0:
            formula[formula_set[i]] = int(pow(10, (len(formula_set)-1-i)/2))
        if (len(formula_set)-1-i) % 2 == 1:
            formula[formula_set[i]] =  5 * (int( pow( 10, (len(formula_set)-1-i)//2) ) )
            
    arabic_output = []
    i = 0
    while i < len(roman):
        #print(i, arabic_value, values[roman[i]])
        if i == len(roman) - 1:
            arabic_output.append(formula[roman[i]])
        elif formula[roman[i]] >= formula[roman[i+1]]:
            arabic_output.append(formula[roman[i]])
        else:
            arabic_output.append( (formula[roman[i+1]] - formula[roman[i]]) )
            if (i+2) < len(roman):
                i += 1
            else:
                break
        if len(arabic_output) > 1:
            if arabic_output[-1] > arabic_output[-2]:
                print("Hey, ask me something that's not impossible to do!") # validity check failed
                sys.exit(0)            
        i += 1 # next loop for calculating value of next numeral
        
    final_arabic_value = sum(arabic_output)
    
    # One last reverse check
    if roman != convert_using_to_roman(str(final_arabic_value), formula_set):
        print("Hey, ask me something that's not impossible to do!") # validity check failed
        sys.exit(0)        
    return final_arabic_value 
    
    

def convert_method_3(roman):
    if (method_3_validity_check(roman)):
        convert_minimally(roman)
    else:
        print("Hey, ask me something that's not impossible to do!") # validity check failed

def method_3_validity_check(roman):
    if roman.isalpha():
        return True
    else:
        return False

def convert_minimally(roman):
    formula = []
    formula_set = ''
    
    i = len(roman) - 1
    count = 1
    while i > -1:
        j = i-1
        while roman[j] == roman[i]:
            j -= 1
            if j < 0: 
                j = 0
                break
            
        if j < 0: 
            j = 0
            
        k = j-1
        if k < 0: 
            k = 0
        l = k-1
        if l < 0: 
            l = 0
        while roman[l] == roman[k]:
            l -= 1
            if l < 0: 
                l = 0
                break
        
        if l < 0: 
                l = 0
        
        #print(f'Pass {count}: 1- {roman[j:i+1]} 2- {roman[l:k+1]} 3- {roman[:l]}')
        #print("i:", i, roman[i], "   j:",  j, roman[j], "   k:", k, roman[k], "   l:", l, roman[l])
        
        if k < j and roman[l] != roman[k]:   # have two sets to compare
            
            status1 = True
            
            for e in roman[j:i+1]:
                if e in roman[:j]: # compare first different set with all other characters
                    status1 = False
                    
            if status1 == True:               # if first set has unique characters
                if i-j == 1:
                    if roman[i] in roman[i+1:]:     # implies: it is of form VI (LX)
                        formula.append(roman[i])    
                        formula.append(roman[j]) 
                    else:
                        formula.append(roman[j])    # implies: first set is of form IV
                        formula.append(roman[i])     
                else:
                    formula.append(roman[i])    # implies: first set is of form VII.
                    formula.append(roman[j])        
            else:                             # if characters of first set are in rest
                if roman[i] in roman[:j] and roman[j] in roman[:j] and j<i:
                    print("Hey, ask me something that's not impossible to do!") # both sets have same characters
                    #print("Failure 1")
                    sys.exit(0)
                elif roman[i] not in roman[:j] and roman[j] in roman[:j]:  # 2nd character of 1st set is not in rest
                    formula.append(roman[i])     # implies: first set only contains one character of form I..
                    formula.append('_')          # implies: for both i-j >= 1
                    j = j + 1  
                elif roman[i] == roman[k] and roman[l] not in roman[:l]:   # 2nd char of 1st set equals to 2nd char of 2nd set
                    formula.append(roman[j])     # implies: 1st set is of form IX and 2nd set is of from LX..
                    formula.append('_')
                    formula.append(roman[i]) 
                    formula.append(roman[l])             
                    j = l
                elif roman[i] == roman[k] and roman[l] in roman[:l]:   # 2nd char of 1st set equals to 2nd char of 2nd set
                    formula.append(roman[j])     # implies: 1st set is of form IX and 2nd set is of from X..
                    formula.append('_')
                    formula.append(roman[k]) 
                    formula.append('_')           
                    j = l + 1
                elif roman[i] == roman[l] and roman[k] not in roman[:k]:       # 2nd char of 1st set equals to 1st char of 2nd set
                    formula.append(roman[j])     # implies: 1st set is of form IX and 2nd set is of form XL
                    formula.append('_')
                    formula.append(roman[i]) 
                    formula.append(roman[k])             
                    j = l
                    
                elif roman[i] == roman[l] and roman[k] in roman[:k]:       # 2nd char of 1st set equals to 1st char of 2nd set
                    formula.append(roman[j])     # implies: 1st set is of form IX and 2nd set is of form XC
                    formula.append('_')
                    formula.append(roman[i]) 
                    formula.append('_')             
                    j = l
                    
                elif roman[j] in roman[:j]:      # 1st set only contains one character (i)
                    formula.append(roman[i])
                    formula.append('_')
                    j = j+1
        elif k < j and roman[l] == roman[k]: # 2nd set has same character(s)  
            if roman[i] not in roman[:j] and roman[j] == roman[k]:  # 2nd character of 1st set is not in rest
                    formula.append(roman[i])     # implies: 1st set only contains one character
                    formula.append('_')          # implies: 2nd only has one char
                    formula.append(roman[l])     # imlpies: 1st set is of from I.. and 2nd is X..
                    formula.append('_')
                    j = l
            elif roman[i] not in roman[:j] and roman[j] != roman[k]  and i-j==1:  # 2nd character of 1st set is not in rest
                if roman[i] in roman[i+1:]:      # implies: it is of form VI (LX)
                    formula.append(roman[i])     # implies: 1st set only contains two characters which are not in 2nd set
                    formula.append(roman[j])     # implies: 2nd only has one char
                    formula.append(roman[l])     # imlpies: 1st set is of from VI and 2nd is X..
                    formula.append('_')
                    j = l
                else:                            # implies: it is of form IV
                    formula.append(roman[j])     # implies: 1st set only contains two characters which are not in 2nd set
                    formula.append(roman[i])     # implies: 2nd only has one char
                    formula.append(roman[l])     # imlpies: 1st set is of from IV and 2nd is X..
                    formula.append('_')
                    j = l
            elif roman[i] not in roman[:j] and roman[j] != roman[k]  and i-j>1:  # 2nd character of 1st set is not in rest
                    formula.append(roman[i])     # implies: 1st set contains more than two characters which are not in 2nd set
                    formula.append(roman[j])     # implies: 2nd only has one char
                    formula.append(roman[l])     # imlpies: 1st set is of from VII. and 2nd is X..
                    formula.append('_')
                    j = l
            elif roman[i] == roman[k]:  # 2nd character of 1st set equals to character of 2nd set
                    formula.append(roman[j])     # implies: 1st set contains two characters
                    formula.append('_')          # implies: 2nd only has one char
                    formula.append(roman[i])     # imlpies: 1st set is of from IX and 2nd is X..
                    formula.append('_')
                    j = l  
        else:                                   # have only final set                
            if roman[i] == roman[j]:            # final set has only 1 unique char
                formula.append(roman[i])        # implies: it is of form I..
                j = 0
            elif i-j == 1:                      # final set has only 2 char
                if roman[i] in roman[i+1:]:     # implies: it is of form VI (LX)
                    formula.append(roman[i])        
                    formula.append(roman[j])
                else:                           # implies: it is of form IV
                    formula.append(roman[j])        
                    formula.append(roman[i])
            elif i-j > 1:                       # final set has more than 2 char
                formula.append(roman[i])        # implies: it is of form VII.
                formula.append(roman[j])            
        
        #print("i:", i, roman[i], "   j:",  j, roman[j], "   k:", k, roman[k], "   l:", l, roman[l])
        count += 1
        i = j-1
    
    for e in range(len(formula)-1, -1, -1):
        formula_set += formula[e]
    if formula_set[0] == '_':
        formula_set = formula_set[1:]
        
    for e in roman:
        if e not in formula_set:
            print("Hey, ask me something that's not impossible to do!") # checking if all roman characters
            #print("Failure 2")
            sys.exit(0)                                                 # exists in formula set or not
    
    for i in range(len(formula_set)):
        if formula_set[i] != '_' and formula_set[i] in formula_set[i+1:]:
            print("Hey, ask me something that's not impossible to do!") # checking if formula set has 
            #print("Failure 3")
            sys.exit(0)                                                 # unique characters
    
    arabic_output = convert_using_to_arabic(roman, formula_set) # convert value for correct input        
    roman_output = convert_using_to_roman(str(arabic_output), formula_set) # reverse checking        
        
    if roman_output == roman:            
        print(f"Sure! It is {arabic_output} using {formula_set}" ) 
    else:
        print("Hey, ask me something that's not impossible to do!") # reverse comparison check failed
        #print("Reverse failure")
    
# main    
while(True):
    please_convert()


