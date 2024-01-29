from yahoofantasy import Context
import streamlit as st
import pandas as pd
import numpy as np
import requests,base64

def refreshAuthorizationToken(refreshToken:str) -> dict:
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

        return dobj
    
    print("Something went wrong when getting refresh token...try getting the initial access token again!")

    return None

st.title('fantasy baseball lets goooo')

# Plug in your ID & SECRET here from yahoo when you create your app. Make sure you have the correct scope set for fantasy API ex: "read" or "read/write"
CLIENT_ID = "dj0yJmk9YUpWbEg5MGkzTEdYJmQ9WVdrOVZ6ZEZWRlZIVTNBbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PTgx"
CLIENT_SECRET = "703ad715785dd8def4237cc84c1527109eb7c4a5"

# Special auth header for yahoo.
AUTH_HEADER = base64.b64encode(bytes(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8"))).decode("utf-8")

auth = {
    "access_token": "XdA.uEycvV4qNJFluwELonnA_lq29f13vaIszY6pEGMYivUeyOnW7X13IDbbFW4LKcxkIR4wdmc4BdKTlBJ9_fjTBfOov7s5BAzW5lAVULtSl.eyIVYRBfIep9fXPT8rRSPpKNc6wejZws1rgmUC99LsqQeSoKRewcRar2JhAaf86gY8TtSMIu8M_ZlJiQ60DWt96qUHEU4U85uOLR2svuIqYyHCZSCr9DVWk0QJ0aCqa0fqlg1UG8cluNNyVrxmI7QdXAMS1Vso6nWbqODWrHLaN8YRocDEJ8E_d4FGOT.dy5wqNly4WG7IiIrp0YbUGCycUCUCgT4JAjsWi1prYNLfQEAepHBauAwvjS6KT_wu46_bn7xGCTMOd6zI1w_yXG0cIgbQ4EfuBkC8aZ8gHuOg0V9P4oQMdJwHVyGc.D2a5VbXjuB2xmhqNjiyXDX.YoYNygBh934NbZ1x6po8rhShPLR0AUdyVH1mUfLXYpBr2y58hQDK1c3SAO2XQZQD_LWnjhsLk1Pzos.3phFOrUJ83QI5x0J7q1oOjf0qeTdOEGfoJH0FdWkgTesN8oz8euw._Gib559KQTt.You_whl_D.KONKesDo.OAiaK8WSkw91iCl3rU7YPY2HAgPEoMG7PqGjDvMUO5NvWqs0Vpr_E9q7qoxlP7K03B_ayy50wnY9xBR3ma.7d7MU5fGOWH_2dFNaHs_DXdWZqUGi7rhkaobE.33hjTFXRYBEHYptfGxfgu1p1vsloY8E_zyjdWbScRvHm97aXBZ8IPHeBmsI6LEF_Wx_CKw2As8jS5XBNvDuouxDh0acC2nrjFL9jVmwNgcQ89m3aEiBtSAcVn3LZokiEPNZPrjTT95YY15k1ANJunBuGqGRAX23mm4gnHZgVZxXOK4KBUrOGKePPOsIXRZvK9SOg6yNr3xxwCbLaSZrwrA--",
    "refresh_token": "AAsms2X6O_k.EP.XOxX8bazEcnGn~000~DD6cKVWWxFJBrDi8q9h5AF9kVy.0hno-",
    "expires_in": 3600,
    "token_type": "bearer"
}

# Anytime the context is used, I would wrap it in a try except block in case it needs to get a new token.
try:

    ctx = Context(persist_key="oauth2",client_id=CLIENT_ID,client_secret=CLIENT_SECRET,refresh_token=auth["refresh_token"])
    leagues: list = ctx.get_leagues("mlb", 2023)

except Exception:

    # Get refresh token
    auth = refreshAuthorizationToken(auth["refresh_token"])
    ctx = Context(persist_key="oauth2",client_id=CLIENT_ID,client_secret=CLIENT_SECRET,refresh_token=auth["refresh_token"])
    leagues: list = ctx.get_leagues("mlb", 2023)

print("MLB: ",leagues)

if leagues:
    # Get all baseball leagues I belonged to in 2019
    for league in leagues:
        
        print("~~~~~~~~ LEAGUE ~~~~~~~~")
        print(f"{league.id} - {league.name} ({league.league_type})")

        # Can't really tell what this is doing since I dont have any fantasy data..
        df = pd.DataFrame({'team':[], 'cat':[], 'stat':[]})
        df2 = pd.DataFrame({'team':[], 'cat':[], 'stat':[]})

        week_18 = league.weeks()[17]

        for matchup in week_18.matchups:

            for team1_stat, team2_stat in zip(matchup.team1_stats, matchup.team2_stats):

                df.loc[len(df)] = [matchup.team1.name, team1_stat.display, team1_stat.value]
                df2.loc[len(df2)] = [matchup.team2.name, team2_stat.display, team2_stat.value]

        df_combined = pd.concat([df,df2])
        df_wide = pd.pivot(df_combined, index='team', columns='cat', values='stat')

        cols = ['H/AB', 'R', 'HR', 'RBI', 'SB', 'OBP', 'IP', 'ERA', 'WHIP', 'K', 'QS', 'SV+H']

        df_new = df_wide[cols]

        st.write(df_wide)
        st.write(df_new)