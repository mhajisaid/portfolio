#importing Pyotp library to give us random otp number
import pyotp
#importing password_validator library to validate password complexity
from password_validator import PasswordValidator


#create otp verible to generate a code
otp = pyotp.TOTP('base32secret3232')
#create complexity verible to set our password target
complexity = PasswordValidator()
# initialise the requirment for sound password
complexity.min(8).max(15).has().lowercase().has().uppercase().has().digits()


#create register function to define how user registers new account
def Register():
#while loop to bring us back incase password dont match with confirm password
 while True: 
    #username variable so user can input name
    username = input('> Enter Username: ')
    #password variable so user can input password 
    password = input('> Enter Password: ')
    # complexity check if the password meets the complexity requirment
    complexity.validate(password)
    # confirm password variable so user can confirm password
    confirm_password = input('> Confirm Password: ')
    # complexity check if the password meets the complexity requirment
    complexity.validate(confirm_password)
    # if stament to check if the password meets complexity requriment 
    if complexity.validate(confirm_password) == True:
        #if statement to check if password is same as confirm password
        if password == confirm_password :
            #open pass.txt in appen mode and store user username and password
            password_file = open('pass.txt', 'a')
            password_file.write(f'{username} --> {confirm_password}' "\n")
            password_file.close()
            #output to tell us if the user created the account successfuly
            print('> Account Created Successfully!')
            break
            #else if statment if the password dont match up with confirm password
        elif password != confirm_password:
            # output if the both passwords dont match 
            print('> Error, Passwords do not match')
            continue
    else:
        # output if your password dont match complexity requirement 
        print("Password dose not meet complexity requirement! please try again")


#create Login function to define how user login after the account is created
def Login():
    while True:
        #username object so user can input name
        username = input('> Enter username: ')
        #password object so user can input name
        password = input('> Enter Password: ')
        #open pass.txt in read mode and to read username and password
        with open('pass.txt', 'r') as password_file:  
            #for loop to inspect password file line by line  
            for line in password_file:
                line = line.strip()
                # Split each line into separate username and password strings
                line_parts = line.split(' --> ')
                file_username = line_parts[0]
                file_password = line_parts[1]
                # Check if the username and password match
                if username == file_username and password == file_password:
                    #output Welcome user application
                    print("\nHi" + username + "  Welcome to the Online Shopping System! \n" )  
                    return
                else:
                    #if the username or password incorrect output invalid username or paaword. Try again    
                    print('> Invalid username or password. Try again!')


print('>Enter signup to register')
print('> Enter login to login')


while True:
    # input function to ask user if they want to signup or login
    signup_or_login = input('> Do you want to signup or login: ')
    #if user input signup then call up the register function
    if signup_or_login == 'signup':
        Register()
    #else if user input login then call up the login function
    elif signup_or_login == 'login':
        Login() 

        while True: 
            # if the user completes the login steps successfully then open otp.txt or create file if the file is not there
            otp_file = open('otp.txt', 'a')
            # write otp generate code onto otp file 
            otp_file.write(f'One Time Password: {otp.now()}' "\n")
            #close otp file 
            otp_file.close()
            #create code veriable to input otp code 
            code = input('> Please Enter Your One Time Password:')           
            # if statment to check the input code matches the generated code
            if otp.verify(code) == True:
                #output access granted if the code entred is correct if you take too long to input the code the system will generate new code
                print('> Access Granted!!!')
                break
            else:
                #output access denied if the code entred is incorrect 
                print('> Access Denied!!!')
            continue 

    else:
        # error output to tell user to entier signup or login
        print('> Error, enter a valid input: (signup or login)')
        break
    continue