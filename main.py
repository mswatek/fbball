from doAuthStuff import getInitialAuthorization,refreshAuthorizationToken,loadAccessToken,CLIENT_ID,CLIENT_SECRET,authFilePath
from yahoofantasy import Context
import streamlit as st
import pandas as pd
import numpy as np

st.title('fantasy baseball')

auth = loadAccessToken()

# Anytime the context is used, I would wrap it in a try except block in case it needs to get a new token.
try:

    ctx = Context(persist_key="oauth2",client_id=CLIENT_ID,client_secret=CLIENT_SECRET,refresh_token=auth["refresh_token"])
    leagues: list = ctx.get_leagues("mlb", 2023)[0]

except Exception:

    # Get refresh token
    auth = refreshAuthorizationToken(auth["refresh_token"])
    ctx = Context(persist_key="oauth2",client_id=CLIENT_ID,client_secret=CLIENT_SECRET,refresh_token=auth["refresh_token"])
    leagues: list = ctx.get_leagues("mlb", 2023)[0]

print("MLB: ",leagues)

df = pd.DataFrame({'team':[], 'cat':[], 'stat':[]})
df2 = pd.DataFrame({'team':[], 'cat':[], 'stat':[]})
week_18 = leagues.weeks()[17]

for matchup in week_18.matchups:
    for team1_stat, team2_stat in zip(matchup.team1_stats, matchup.team2_stats):
        df.loc[len(df)] = [matchup.team1.name, team1_stat.display, team1_stat.value]
        df2.loc[len(df2)] = [matchup.team2.name, team2_stat.display, team2_stat.value]

df_combined = pd.concat([df,df2])
df_wide = pd.pivot(df_combined, index='team', columns='cat', values='stat')

cols = ['H/AB', 'R', 'HR', 'RBI', 'SB', 'OBP', 'IP', 'ERA', 'WHIP', 'K', 'QS', 'SV+H']
df_new = df_wide[cols]

st.write(df_new)