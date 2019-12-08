#!/usr/bin/env python3
"""
This python script can be run against a webpage to get all the comments present in the page.
The hope is that this will potentially get some information that could be used in reconnaissance.
"""

###############
# Imports
###############

import argparse
import os
from datetime import datetime
import sys
import requests
from bs4 import BeautifulSoup


# GOOD: --> and <!--

def parse_comments(content):
    """
    This function takes in a parameter (content) and returns a list of lists.
    The parameter passed in must be the result of a requests.get that has been passed
    to Beautiful Soup "html.parser" and then split on a newline.
    The returned list of lists has an integer in the first element of the internal list
    that indicates the line number the comment was found on.
    The second element is the comment itself in string format.
    """

    comments = []
    continuing = False

    for line in enumerate(content):
        # If we're continuing a multiline comment and the end of the comment isn't in this line
        if continuing and line[1].find('-->') == -1:
            # Append the string of this line to the string part of the last comment in the list
            comments[-1][1] += '\n' + str(line[1])

        # If we're continuing a multiline comment and the end of the comment is in this line
        elif continuing and line[1].find('-->') != -1:
            # Append the string of this line to the string part of the last comment in the list
            continuing = False
            # Get the slice before the end comment in case there's HTML
            # after the comment on the same line
            comments[-1][1] += '\n' + str(line[1][:(line[1].find('-->') + 3)])

        # If it's a comment in a single line, add it to the list of comments
        # The comment start tag and the end tag
        elif str(line[1]).find('<!--') != -1 and line[1].find('-->') != -1:
            comments.append([line[0], line[1]])

        # If there's a comment beginning in a single line, add it to the list
        # and set continue to true
        # The comment start tag with no end (multiline comment)
        elif line[1].find('<!--') != -1 and line[1].find('-->') == -1:
            continuing = True
            comments.append([line[0], '\n' + str(line[1])])

    return comments

def get_content(url):
    """
    This function makes an HTTP GET request for the url specified.
    The parameter returned is the result of a requests.get that has been passed
    to Beautiful Soup "html.parser" and then split on a newline.
    """
    # Get the webpage with a GET request
    try:
        response = requests.get(url, timeout=5)
    # Prepend https:// to the url if the user didn't provide one
    except requests.exceptions.MissingSchema:
        response = requests.get("https://" + url, timeout=5)
    except ConnectionRefusedError:
        print("The script could not connect. Ensure your prefix is correct (e.g. http://)")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("The script could not connect. Ensure your prefix is correct (e.g. http://)")
        sys.exit(1)

    # Make it fancy looking with BeautifulSoup
    content = BeautifulSoup(response.content, "html.parser")

    # Make it a list of strings that are split on the newline
    content = str(content).split('\n')

    return content

def write_output(comments, args):
    """
    This function takes two arguments - the comments list created by the parse_comments function
    above and the configparser parsed arguments object.
    It either writes output to stdout
    """
    # Get the date for use in all the choices below
    now = datetime.now()
    now = now.strftime("%H:%M:%S")

    # If the output isn't specified, write to stdout
    if not args.output:
        print("Comments from run on " + str(now))
        print("URL: " + args.url)
        for item in comments:
            print("Line number " + str(item[0]) + ": " + item[1])

    # If the output is specified and isn't mysql, write to a file
    elif args.output == "mysql":
        print("WARNING: MYSQL support not yet implemented - writing to STDOUT")
        print("Comments from run on " + str(now))
        print("URL: " + args.url)
        for item in comments:
            print("Line number " + str(item[0]) + ": " + item[1])

    else:
        # If the file exists, append to it
        if os.path.exists(args.output):
            f = open(args.output, 'a')
        # If the file doesn't exist, make it new
        else:
            f = open(args.output, 'w')
        # Write the comments to the file
        f.write("\n\nComments from run on " + str(now) + '\n')
        f.write("URL: " + args.url + '\n\n')
        for item in comments:
            f.write("Line number " + str(item[0]) + ": " + item[1] + '\n')

def main():
    """
    This script takes in an argument of a URL and then scrapes all comments out of that URL.
    Pretty simple.
    """

    ###############
    # Command line arguments
    ###############

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="The URL to parse. If no protocol is specified, defaults to https", required=True)
    parser.add_argument("-o", "--output", help="The plce to direct output to. If left blank, script will output to stdout. \nOther options:\n\tmysql - save to a database (not implemented), \n\tfilename - create or append to a file", required=False)
    args = parser.parse_args()


    ###############
    # Get the content
    ###############

    # Get the content of the webpage
    content = get_content(args.url)

    # Parse that content for comments
    comments = parse_comments(content)

    # Write the output
    write_output(comments, args)

if __name__ == "__main__":
    main()
