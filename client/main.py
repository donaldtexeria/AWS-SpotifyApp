#
# Client-side python app for benford app, which is calling
# a set of lambda functions in AWS through API Gateway.
# The overall purpose of the app is to process a PDF and
# see if the numeric values in the PDF adhere to Benford's
# law. This version adds authentication with user names, 
# passwords, and login tokens.
#
# Authors:
#   << YOUR NAME >>
#
#   Prof. Joe Hummel (initial template)
#   Northwestern University
#   CS 310
#

import requests
import json
import urllib.parse

import uuid
import pathlib
import logging
import sys
import os
import base64
import time

from configparser import ConfigParser
from getpass import getpass


############################################################
#
# classes
#
class User:

  def __init__(self, row):
    self.userid = row[0]
    self.username = row[1]
    self.pwdhash = row[2]


class Job:

  def __init__(self, row):
    self.jobid = row[0]
    self.userid = row[1]
    self.status = row[2]
    self.originaldatafile = row[3]
    self.datafilekey = row[4]
    self.resultsfilekey = row[5]


###################################################################
#
# web_service_get
#
# When calling servers on a network, calls can randomly fail. 
# The better approach is to repeat at least N times (typically 
# N=3), and then give up after N tries.
#
def web_service_get(url):
  """
  Submits a GET request to a web service at most 3 times, since 
  web services can fail to respond e.g. to heavy user or internet 
  traffic. If the web service responds with status code 200, 400 
  or 500, we consider this a valid response and return the response.
  Otherwise we try again, at most 3 times. After 3 attempts the 
  function returns with the last response.
  
  Parameters
  ----------
  url: url for calling the web service
  
  Returns
  -------
  response received from web service
  """

  try:
    retries = 0
    
    while True:
      response = requests.get(url)
        
      if response.status_code in [200, 400, 480, 481, 482, 500]:
        #
        # we consider this a successful call and response
        #
        break;

      #
      # failed, try again?
      #
      retries = retries + 1
      if retries < 3:
        # try at most 3 times
        time.sleep(retries)
        continue
          
      #
      # if get here, we tried 3 times, we give up:
      #
      break

    return response

  except Exception as e:
    print("**ERROR**")
    logging.error("web_service_get() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return None
    

############################################################
#
# prompt
#
def prompt():
  """
  Prompts the user and returns the command number

  Parameters
  ----------
  None

  Returns
  -------
  Command number entered by user (0, 1, 2, ...)
  """
  try:
      print()
      print(">> Enter a command:")
      print("   0 => end")
      print("   1 => make playlist based on your mood")
      print("   2 => make playlist based on your top artists")
      print("   3 => get text sentiment")

      cmd = input()

      if cmd == "":
        cmd = -1
      elif not cmd.isnumeric():
        cmd = -1
      else:
        cmd = int(cmd)

      return cmd

  except Exception as e:
      print("**ERROR")
      print("**ERROR: invalid input")
      print("**ERROR")
      return -1


############################################################
#
# users
#
def create_mood_playlist(baseurl, access_token, user_id):
  """
  Prints out all the users in the database

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    print("tell me about your day>")
    s = input()
    path = "/sentiment"
    url = baseurl + path
    body = {
        "text": s
    }

    # res = requests.get(url)
    res = requests.post(url, json=body)

    #
    # let's look at what we got back:
    #
    if res.status_code == 200: #success
      pass
    else:
      # failed:
      print("**ERROR: failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and extract users:
    #
    sentiment = res.json()
    
    print("name your playlist>")
    s = input()
    api = "/playlist/mood"
    url = baseurl + api
    body = {
        "access_token": access_token,
        "user_id": user_id,
        "sentiment": sentiment,
        "playlist_name": s
    }
    res = requests.post(url, json=body)
    if res.status_code != 200:
      print("failed")
    p_id = res.json()
    print(f"Created playlist called \'{s}\' with id: \'{p_id}\'")

    #
    # let's map each row into a User object:
    #
    return

  except Exception as e:
    logging.error("**ERROR: create_mood_playlist() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

def create_top_artists_playlist(baseurl, access_token, user_id):
    print("name your playlist>")
    s = input()
    path = "/playlist/top-artists-songs"
    url = baseurl + path
    body = {
        "access_token": access_token,
        "user_id": user_id,
        "playlist_name": s
    }
    res = requests.post(url, json=body)
    if res.status_code == 200: #success
      pass
    else:
      # failed:
      print("**ERROR: failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return
    p_id = res.json()
    print(f"Created playlist called \'{s}\' with id: \'{p_id}\'")

def get_text_sentiment(baseurl):
    print("Input text>")
    s = input()
    path = "/sentiment"
    url = baseurl + path
    body = {
        "text": s
    }

    # res = requests.get(url)
    res = requests.post(url, json=body)

    #
    # let's look at what we got back:
    #
    if res.status_code == 200: #success
      pass
    else:
      # failed:
      print("**ERROR: failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and extract users:
    #
    sentiment = res.json()
    print(f"The provided text has {sentiment} sentiment")
############################################################
#
# jobs
#

############################################################
#
# check_url
#
def check_url(baseurl):
  """
  Performs some checks on the given url, which is read from a config file.
  Returns updated url if it needs to be modified.

  Parameters
  ----------
  baseurl: url for a web service

  Returns
  -------
  same url or an updated version if it contains an error
  """

  #
  # make sure baseurl does not end with /, if so remove:
  #
  if len(baseurl) < 16:
    print("**ERROR: baseurl '", baseurl, "' is not nearly long enough...")
    sys.exit(0)

  if baseurl == "https://YOUR_GATEWAY_API.amazonaws.com":
    print("**ERROR: update config file with your gateway endpoint")
    sys.exit(0)

  if baseurl.startswith("http:"):
    print("**ERROR: your URL starts with 'http', it should start with 'https'")
    sys.exit(0)

  lastchar = baseurl[len(baseurl) - 1]
  if lastchar == "/":
    baseurl = baseurl[:-1]
    
  return baseurl

def get_access_token(client_id, client_secret):
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    })

    if auth_response.status_code == 200:
        auth_data = auth_response.json()
        return auth_data['access_token']
    else:
        raise Exception(f"Failed to retrieve access token: {auth_response.text}")
  

############################################################
# main
#
try:
  print('** Welcome to SpotifyApp with Authentication **')
  print()
  

  # eliminate traceback so we just get error message:
  sys.tracebacklimit = 0

  #
  # we have two config files:
  # 
  #    1. benfordapp API endpoint
  #    2. authentication service API endpoint
  #
  #
  
  #print("Getting Spotify Access Token")
  configur = ConfigParser()
  config = ConfigParser()
  
  spotify_config_file = 'spotify_client_config.ini'
  print("First, enter name of spotify config file to use...")
  print("Press ENTER to use default, or")
  print("enter config file name>")
  s = input()

  if s == "":  # use default
    pass  # already set
  else:
    spotify_config_file = s
  if not pathlib.Path(spotify_config_file).is_file():
      print("**ERROR: spotify config file '", spotify_config_file, "' does not exist, exiting")
      sys.exit(0)
  configur.read(spotify_config_file)
  baseurl = configur.get('CLIENT', 'webservice')
  
  baseurl = check_url(baseurl)
  
  
  config.read("spotify_config.ini")
  client_id = config["SPOTIFY"]["client_id"]
  client_secret = config["SPOTIFY"]["client_secret"]
  redirect_uri = config["SPOTIFY"]["redirect_uri"]
  scope = 'user-library-read user-library-modify playlist-read-private playlist-modify-private playlist-modify-public user-read-private user-read-email user-top-read'
  auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}&redirect_uri={urllib.parse.quote(redirect_uri)}&scope={urllib.parse.quote(scope)}"
  
  print("open the link below to authorize your spotify account. On redirect, enter the code in the url")
  print(auth_url)
  
  print("\nEnter auth code>")
  auth_code = input()
  
  headers = {
    'Authorization': 'Basic ' + base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode('utf-8')
  }
  data = {
    'grant_type': 'authorization_code',
    'code': auth_code,
    'redirect_uri': redirect_uri
  }
  token_url = 'https://accounts.spotify.com/api/token'
  response = requests.post(token_url, headers=headers, data=data)
        
    # Request headers
  headers = {
      "Content-Type": "application/x-www-form-urlencoded"
  }
  token_data = response.json()

# Extract access token and refresh token (optional)
  access_token = token_data.get('access_token')
  if not access_token:
    print("Error:", token_data)
      
  #print("Getting my user id!")
  path = "/me/top/artists"
  spot_url = "https://api.spotify.com/v1"
  headers = {"Authorization": f"Bearer {access_token}"}
  url = spot_url + path
  url = "https://api.spotify.com/v1/me"
  
  
  response = requests.get(url, headers=headers)
  user_id = 0
  if response.status_code == 200:
      my_data = response.json()
      user_id = my_data['id']
  else:
      print("Failed to get artists data")
      print("error:", response.status_code, response.text)
 
  #
  # initialize login token:
  #

  #
  # main processing loop:
  #
  cmd = prompt()

  while cmd != 0:
    #
    if cmd == 1:
      create_mood_playlist(baseurl, access_token, user_id)

      #
      # logout
      #
      token = None
    elif cmd == 2:
        create_top_artists_playlist(baseurl, access_token, user_id)
    elif cmd == 3:
        get_text_sentiment(baseurl)
    else:
      print("** Unknown command, try again...")
    #
    cmd = prompt()

  #
  # done
  #
  print()
  print('** done **')
  sys.exit(0)

except Exception as e:
  logging.error("**ERROR: main() failed:")
  logging.error(e)
  sys.exit(0)
