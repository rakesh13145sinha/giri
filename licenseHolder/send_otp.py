from sendotp import sendotp
import requests
#access_key = "301307Avh9j3eGT55db92087"  
#access_key  ='359397A31iCLUqH9m60824c3bP1'
#authkey='359397A31iCLUqH9m60824c3bP1'
# authkey="364668A3kfs0Kel3Ld60fa4eaaP1"
# access_key = "WxSMoQhUSAZ" 

# def sending_otp(otp,phone):
# 	otpobj =  sendotp.sendotp(access_key,	"""{{otp}} Use this OTP for confirmation please donot share with anyone.""")
# 	res = otpobj.send("91"+phone,'MEDPLD',otp)
# 	return res

#!/usr/bin/python
import requests
import sys
import urllib
import urllib.parse
import random

#Generate Random Number
# = random.randint(100000,999999)
#Store Phone Number
#phone = "91XXXXXXXXXX"
#Contstruc Message String
#Encode message

#Construct API URL to send SMS
#url = "https://smsapi.24x7sms.com/api_2.0/SendSMS.aspx?APIKEY=WxSMoQhUSAZ&MobileNo="+phone+"&SenderID=SQUROW&Message=" + message + "&ServiceName=TEMPLATE_BASED"
#Run API
#r = requests.get(url)
#Display API response
#print (r.text)
#print ("SMS SENT...")

def sending_otp(otp,phone):
	message = str(otp) + " is the verification code to access your Buildcron account. This verification code is valid for 5 mins. Please do not share it with anyone. Thanks, Squarow consultants pvt. ltd.";

	message = urllib.parse.quote(message, safe='')
	url = "https://smsapi.24x7sms.com/api_2.0/SendSMS.aspx?APIKEY=WxSMoQhUSAZ&MobileNo="+"91"+phone+"&SenderID=SQUROW&Message=" + message + "&ServiceName=TEMPLATE_BASED"
	#Run API
	r = requests.get(url)
	
	return r.text

