"""

Program that handles the initial login for yahoo oauth & getting the refresh token. 
Be sure not to delete the oauth2.json file that is generated because it will be re-used to get the refresh token periodically because the access token expires every 60 minutes.
Plug your client ID that is generated into the url below to get the first-time auth code

https://api.login.yahoo.com/oauth2/request_auth?client_id=dj0yJmk9VEtpWVNNQzd1TVRtJmQ9WVdrOVRUQkpObXRuTjJrbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTcy&redirect_uri=oob&response_type=code&language=en-us

Also be sure to copy & paste your client ID & client SECRET into the places below. Everything is commented to make it easy as possible.


If you made it this far, go ahead and run this program to generate the oauth2.json file & then try to run the main.py!

"""

import requests,json,base64,os

authFilePath: str = os.getcwd() + "/oauth2.json"

# Plug in your ID & SECRET here from yahoo when you create your app. Make sure you have the correct scope set for fantasy API ex: "read" or "read/write"
CLIENT_ID = "dj0yJmk9VEtpWVNNQzd1TVRtJmQ9WVdrOVRUQkpObXRuTjJrbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTcy"
CLIENT_SECRET = "23f4d294641cc580d381c647f8932711f19a50e8"

# One-time auth code on first app run to get intial access token. After that the access token can be re-used to get the refresh token. This auth code can only be used one time!
YAHOO_AUTH_CODE = "su6vayr"

# Special auth header for yahoo.
AUTH_HEADER = base64.b64encode(bytes(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8"))).decode("utf-8")

def getInitialAuthorization() -> dict|None:
    """This function is only used with first-time auth code to get the access token."""

    headers: dict = {
        'Authorization': f"Basic {AUTH_HEADER}",
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
    }

    data: dict = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": 'oob',
        "code": YAHOO_AUTH_CODE,
        "grant_type": 'authorization_code'
    }

    req = requests.post("https://api.login.yahoo.com/oauth2/get_token",headers=headers,data=data,timeout=100)

    if req.status_code == 200:

        dobj: dict = req.json()

        # Dump to file for future usage!
        with open(authFilePath, "w+") as f:
            json.dump(dobj,fp=f,indent=4)

        return dobj

    print("Something went wrong with getting access token...try again!")

    return None

def refreshAuthorizationToken(refreshToken:str) -> dict|None:
    """Uses existing refresh token to get the new access token"""

    headers: dict = {
        'Authorization': f"Basic {AUTH_HEADER}",
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
    }

    data: dict = {
        "redirect_uri": 'oob',
        "grant_type": 'refresh_token',
        "refresh_token": refreshToken
    }

    req = requests.post("https://api.login.yahoo.com/oauth2/get_token",headers=headers,data=data,timeout=100)

    if req.status_code == 200: 

        dobj: dict = req.json()

        # Dump to file for future usage!
        with open(authFilePath, "w+") as f:
            json.dump(dobj,fp=f,indent=4)

        return dobj
    
    print("Something went wrong when getting refresh token...try getting the initial access token again!")

    return None

def loadAccessToken() -> dict|None:
    """Load the access token and get a new one if needed."""

    if not os.path.exists(authFilePath):

        auth: dict = getInitialAuthorization()

    else:

        with open(authFilePath, "r") as f:
            auth: dict = json.load(f)

    return auth


if __name__=='__main__':

    auth = loadAccessToken()

    #with open(authFilePath, "r") as f:
    #    auth = json.load(f)
    #print(refreshAuthorizationToken(auth["refresh_token"]))