import boto3

import hmac, hashlib, base64 

username= "testuser"
password= "MySuperSecret99!"
email= "Your email goes here"
client_id = ""  # Obtain from the AWS console
client_secret = ""  # Obtain from the AWS console
confirmation_code = "" #Obtain from the verification email

def secretHash(clientId, clientSecret, username):
    message = bytes(username + clientId,'utf-8') 
    key = bytes(clientSecret,'utf-8') 
    return base64.b64encode(hmac.new(key, message, digestmod=hashlib.sha256).digest()).decode() 

def confirm():
    client = boto3.client("cognito-idp", region_name="ap-southeast-2")
    try:
        response = client.confirm_sign_up(
            ClientId=client_id,
            Username=username,
            ConfirmationCode=confirmation_code,
            SecretHash=secretHash(client_id, client_secret, username)
        )
        return response
    except Exception as e:
        print(f"Error during confirmation: {e}")
        return None

confirm_response = confirm()
print("Confirmation successful:", confirm_response)