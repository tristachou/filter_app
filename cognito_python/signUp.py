import boto3
import hmac, hashlib, base64 

username= "testuser"
password= "MySuperSecret99!"
email= "Your email goes here"
client_id = ""  # Obtain from the AWS console
client_secret = ""  # Obtain from the AWS console

def secretHash(clientId, clientSecret, username):
    message = bytes(username + clientId,'utf-8') 
    key = bytes(clientSecret,'utf-8') 
    return base64.b64encode(hmac.new(key, message, digestmod=hashlib.sha256).digest()).decode() 

def signup():
    client = boto3.client("cognito-idp", region_name="ap-southeast-2")
    try:
        response = client.sign_up(
            ClientId=client_id,
            Username=username,
            Password=password,
            SecretHash=secretHash(client_id, client_secret, username),
            UserAttributes=[{"Name": "email", "Value": email}]
        )
        return response
    except Exception as e:
        print(f"Error during sign-up: {e}")
        return None


signup_response = signup()
print("Sign-up successful:", signup_response)
