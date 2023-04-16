<<<<<<< HEAD
# Online Shopping System using OTP and password validator

## Online shopping system that allows users to register and login with two security techniques by ensuring that passwords meet certain complexity requirements, and generates a one-time password for authentication


## Introduction:

In relation to the previous assignment, this project aims to demonstrate solutions for cyber security issues that may arise for an online shopping system. As previously mentioned in the Online Shopping System proposal, one of the main security concerns outlined in the STRIDE threat modelling framework was Spoofing. Spoofing refers to the fraudulent practice of impersonating another entity, individual, or system with the intention of deceiving or misleading a user; Cybercriminals may attempt to gain access to sensitive information or carry out unauthorized actions by using false credentials to impersonate legitimate users (Shostack, 2014, p. 64). 
To mitigate this risk, this project implements two-factor authentication (2FA) using Python. The two methods demonstrated in this project are One Time Password (OTP) and setting Password complexity requirment. 


## One Time Password:

To overcome the main issues associated with relying on passwords and to ensure authentication and authorisation, the method of two-factor authentication was developed. This approach involves using two distinct components, commonly referred to as factors, namely the login credentials such as the username and password as well as a One Time Password, a dynamic code that can be obtained by the user usually via SMS (Andrews, 2018). OTP operates on the principle that every user's account is connected to a mobile phone, as a result, ideally only the user should receive SMS messages sent to the phone number associated with their account. The association of a specific device, such as a mobile phone, to a particular online account endows SMS OTP with considerable strength as an integral component of a multi-factor authentication and authorization system.

## soltuion 2

## code decomposition
### Installing libraries:
Libraries such as pyotp and password_validator need to be installed for the application to run.
<style>
    img{
        width: 500px;
    }
</style>

<span class="image fit"><img src="images/install_libraries.PNG" alt="" /></span>

### Importing libraries:
This program uses PyOTP and password_validator libraries to generate OTP codes and validate password complexity.

<span class="image fit"><img src="images/lib.PNG" alt="" /></span>


### Creating variables for imported libraries:
The PyOTP library uses a OTP variable to generate random OTP codes, while the Password Validator library uses a complexity variable to define the password complexity requirements.

<span class="image fit"><img src="images/libv.PNG" alt="" /></span>

### Registration function and Password validation definiation:
The Register function in the program prompts the user to input a username and password, validates the password complexity requirements using the password_validator library, and stores the username and password in pass.txt if the password meets the requirements.

<span class="image fit"><img src="images/regf.PNG" alt="" /></span>


### Login function:
The Login function in the program prompts the user to input their username and password, compares it to the information stored in a pass.txt, and grants access if the information matches or denies access if it does not match.

 <span class="image fit"><img src="images/lfun.PNG" alt="" /></span>


### Main program body and OTP definition:
The program asks the user to choose between signing up for a new account or logging into an existing account by prompting them to enter either "signup" or "login", it also contains OTP verification to ensure secure user authentication during login.

<span class="image fit"><img src="images/motp.PNG" alt="" /></span>


<<<<<<< HEAD
## program demonstration video
=======

#create otp verible to generate a code
otp = pyotp.TOTP('base32secret3232')
#create complexity verible to set our password target
complexity = PasswordValidator()
#initialise the requirment for sound password
complexity.min(8).max(15).has().lowercase().has().uppercase().has().digits()




## testing
>>>>>>> 4d2295f (hello)

<img src="images/video.gif">

## usage

1. The user launches the application and is presented with the option to either register or login.

2. If the user is a new user, they select the register option and enter their desired username and password, ensuring that the password meets certain complexity requirements.

3. If the registration is successful, the user is informed and prompted to log in with their new credentials.

4. The user selects the login option and enters their username and password.

5. The system validates the username and password, and if they are correct, welcomes the user to the online shopping system.

6. The user is then prompted to enter a one-time password that is generated by the system.

7. The system validates the one-time password and if it matches, grants the user access to the shopping system.

8. If the user enters an incorrect one-time password, the system denies access and prompts the user to enter a new one.
=======
# Online Shopping System using OTP and password validator

## using two seciruty techniques to strengthen the security of customer data 

intro

## solution 1

## soltuion 2

## code 

Importing libraries 
<style>
    img{
        width: 500px;
    }
</style>
<span class="image fit"><img src="images/lib.PNG" alt="" /></span>


 Creating variables for imported libraries

<span class="image fit"><img src="images/libv.PNG" alt="" /></span>

 Registration function and Password validation definiation

<span class="image fit"><img src="images/regf.PNG" alt="" /></span>


 Login function

 <span class="image fit"><img src="images/lfun.PNG" alt="" /></span>


Main program body and OTP definition

<span class="image fit"><img src="images/motp.PNG" alt="" /></span>


## testing

<img src="images/video.gif">

## usage
>>>>>>> ab01893c0f2ee7dee2aa810063cd1df2ab4a7c10
