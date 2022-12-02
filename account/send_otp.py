from sendotp import sendotp
import requests
#access_key = "301307Avh9j3eGT55db92087"  
#access_key  ='359397A31iCLUqH9m60824c3bP1'
#authkey='359397A31iCLUqH9m60824c3bP1'
authkey="364668A3kfs0Kel3Ld60fa4eaaP1"
access_key = "WxSMoQhUSAZ" 

def sending_otp(otp,phone):
	otpobj =  sendotp.sendotp(access_key,	"""{{otp}} Use this OTP for confirmation please donot share with anyone.""")
	res = otpobj.send("91"+phone,'MEDPLD',otp)
	return res