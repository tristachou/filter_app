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


def authenticate():
    client = boto3.client("cognito-idp", region_name="ap-southeast-2")
    try:
        response = client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password,
                "SECRET_HASH": secretHash(client_id, client_secret, username)
            },
            ClientId=client_id  # match signUp.py
        )
        tokens = response["AuthenticationResult"]
        # Optionally verify tokens here using jose or cognito public keys
        return tokens
    except Exception as e:
        print(f"Error during authentication: {e}")
        return None

authenticate_response = authenticate()
print("Authentication successful:", authenticate_response)
