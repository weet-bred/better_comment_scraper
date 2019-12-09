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
import re
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

def write_output(comments, args, url):
    """
    This function takes two arguments - the comments list created by the parse_comments function
    above and the configparser parsed arguments object.
    It either writes output to stdout
    """
    import mysql.connector
    # Get the date for use in all the choices below
    now = datetime.now()
    date = datetime.now().date()
    now = now.strftime("%H:%M:%S")

    # If the output isn't specified, write to stdout
    if not args.output:
        print("Comments from run on " + str(date) + ' ' + str(now))
        print("URL: " + url)
        for item in comments:
            print("Line number " + str(item[0]) + ": " + item[1])

    # MYSQL - HECK YES
    elif args.output == "mysql":

        # Make a MYSQL connector object and connect to the DB
        mydb = mysql.connector.connect(host=args.mysql_host, user=args.mysql_user, passwd=args.mysql_pass, database=args.mysql_db)
        # Make a cursor object and get a list of the tables
        mycursor = mydb.cursor()
        mycursor.execute("SHOW TABLES;")

        # Check if the url has an IP
        ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', url )
        if ip:
            table_name = ip[0].replace('.','_')
        # Strip the URL appropriately to get the proper table name
        else:
            stripped_url = args.url
            stripped_url = stripped_url[stripped_url.find('/') +2:]
            stripped_url = stripped_url.split('.')[0]
            table_name = stripped_url

        # Check if that table actually exists
        found = False
        for x in mycursor:
            if str(x).find(table_name) != -1:
                found = True

        # Create the table if necessary
        if not found:
            mycursor.execute("CREATE TABLE {} (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, url TEXT NOT NULL, line_no INT NOT NULL, date_found DATE NOT NULL, comment TEXT NOT NULL)".format(table_name))

        # INSERT THE DATA
        for line in comments:
            #line[1] = line[1].replace('"', "'")
            sql = "INSERT INTO {} (url, line_no, date_found, comment) VALUES (%s, %s, %s, %s);".format(table_name)
            val = (str(url), str(line[0]), str("12-9-19"), str(line[1]))
            mycursor.execute(sql, val)
            print(mycursor.rowcount, "record inserted")
            mydb.commit()

    # If the output is specified and isn't mysql, write to a file
    else:
        # If the file exists, append to it
        if os.path.exists(args.output):
            f = open(args.output, 'a')
        # If the file doesn't exist, make it new
        else:
            f = open(args.output, 'w')
        # Write the comments to the file
        f.write("Comments from run on " + str(date) + ' ' + str(now))
        #f.write("\n\nComments from run on " + str(now) + '\n')
        f.write("URL: " + url + '\n\n')
        for item in comments:
            f.write("Line number " + str(item[0]) + ": " + item[1] + '\n')

def get_links(content, url, links):
    """
    This function takes in a parameter (content) and returns a list of lists.
    The parameter passed in must be the result of a requests.get that has been passed
    to Beautiful Soup "html.parser" and then split on a newline.
    This returns a list of links that can be grabbed and parsed.
    """
    for line in content:
        # If you find a link, add the link to the list
        if line.find('<a href=') != -1:
            # Slice just the link out of the line
            potential_link = (line[line.find('<a href=') + 9:line.find('</a>') -1])
            potential_link = potential_link[:(potential_link.find('>'))]
            potential_link = potential_link[:(potential_link.find('"'))]
            # Discard relative links and empty ones
            if potential_link != '':
                if str(potential_link[0]) != '#':
                    # Only keep links on the same domain
                    if potential_link.find(url.strip("http://").strip("https://")) != -1 or potential_link[0] == '/' and potential_link.find(url.strip("http://").strip("https://")) not in links:
                        # If it's a redirect to just a relative location, make it absolute
                        if potential_link[0] == '/':
                            potential_link = url + potential_link
                        # Add it to the list
                        links.append(potential_link)

    return links



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
    parser.add_argument("-n", "--number", help="The number of links to follow for crawling.", required=True)
    parser.add_argument("-H", "--mysql_host", help="If using mysql backend, the host that the database is on.", required=False)
    parser.add_argument("-U", "--mysql_user", help="If using mysql backend, the user to connect to the database as.", required=False)
    parser.add_argument("-P", "--mysql_pass", help="If using mysql backend, the password to connect with.", required=False)
    parser.add_argument("-D", "--mysql_db", help="If using mysql backend, the database to connect to.", required=False)

    args = parser.parse_args()
    url = args.url
    iterations = 0
    links = [url]

    if not args.number:
        args.number = 1


    ###############
    # Get the content
    ###############

    while iterations < int(args.number) and iterations < len(links):

        # Look at the current link
        url = links[iterations]

        # Get the content of the webpage
        content = get_content(url)

        # Parse that content for comments
        comments = parse_comments(content)

        # Write the output
        write_output(comments, args, url)

        # Get link to spider
        links = get_links(content, url, links)

        #print(links)
        # Increment the counter
        iterations += 1


if __name__ == "__main__":
    main()
