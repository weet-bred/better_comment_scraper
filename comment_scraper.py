#!/usr/bin/env python3
"""
This python script can be run against a webpage to get all the comments present in the page.
The hope is that this will potentially get some information that could be used in reconnaissance.
"""

###############
# Imports
###############

import argparse
import requests
from bs4 import BeautifulSoup

###############
# Command line arguments
###############

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url", help="The URL to parse. If no protocol is specified, defaults to https", required=True)
args = parser.parse_args()


###############
# Get the content
###############

# Get the url from the arguments
url = args.url
comments = []
continuing = False

# Get the webpage with a GET request
try:
    response = requests.get(url, timeout=5)
# Prepend https:// to the url if the user didn't provide one
except requests.exceptions.MissingSchema:
    response = requests.get("https://" + url, timeout = 5)
except ConnectionRefusedError:
    print("The script could not connect. Check your prefix (e.g. http://) and ensure it's correct")
    exit(1)
except requests.exceptions.ConnectionError:
    print("The script could not connect. Check your prefix (e.g. http://) and ensure it's correct")
    exit(1)

# For some reason, this is just numbers, so ya know this boi is gonna use BeautifulSoup
#content = response.content

# Make it fancy looking with BeautifulSoup
content = BeautifulSoup(response.content, "html.parser")

#print(content)

# Make it a list of strings that are split on the newline
content = str(content).split('\n')

for line in enumerate(content):
    #print(line[1])
    """
    #print(line)
    # If we're continuing a multiline comment and the end of the comment isn't in this line
    if continuing and line[1].find('-->') == -1:
        # Append the string of this line to the string part of the last comment in the list
        comments[-1][1].append(line[1])
        print("Found!")

    # If we're continuing a multiline comment and the end of the comment is in this line
    elif continuing and line[1].find('-->') != -1:
        # Append the string of this line to the string part of the last comment in the list
        comments[-1][1].append(line[1][:line.find('-->')])
        continuing = False
        print("Found!")

    """
    # If it's a comment in a single line, add it to the list of comments
    #el
    if line[1].find('<!––') == -1:# and line[1].find('––>') != -1: # The comment start tag and the end tag
        comments.append(line)
        print("Found!")

    """
    # If there's a comment beginning in a single line, add it to the list and set continue to true
    elif line[1].find('<!––') != -1 and line[1].find('-->') == -1: # The comment start tag with no end (multiline comment)
        continuing = True
        comments.append(line)
        print("Found!")
    """

print(comments)
