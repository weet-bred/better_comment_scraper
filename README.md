# better_comment_scraper

<h1>comment_scraper.py</h1>

<p>This script can do a few things:</p>
<ul>
<li>Parse a webpage at a URL for HTML comments</li>
<li>Store those comments in a text file or MySQL database</li>
<li>Parse other webpages on the same site that are linked to the first page or subsequent pages</li>
</ul>

<h4>Basically, it's a cool comment parser with a few decent storage options and some really crummy spidering functionality.</h4>
<p>The hope is that this tool could be used to find things that are hidden in webpages that should be removed. For example:</p>
<ul>
  <li>Employee names</li>
  <li>IP addresses</li>
  <li>Testing data</li>
</ul>
<p>Usage is really simple. Here are your options:</p>
<ul>
  <li>General</li>
  <ul>
    <li>-u, --url: The URL to parse and/or start spidering from.</li>
    <li>-o, --output: Where to store output. If blank, output goes to STDOUT. If "mysql", output goes to the database specified in the other MySQL options below. If anything else, output goes to a file of that name.</li>
    <li>-n, --number: The number of sites to "spider." The script will follow up to this many links if they're available. If not specified, defaults to 1.</li>
  </ul>
  <li>MySQL</li>
  <ul>
    <li>-H, --mysql_host: The database host.</li>  
    <li>-U, --mysql_user: The user to connect to the database as.</li>
    <li>-D, --mysql_db:   The database to connect to.</li>
    <li>-P, --mysql_pass: The password for the user to connect as.</li>
    <li>-p, --prompt_pass: Promt for the password to connect to the database with instead of providing on the command line</li>
  </ul>
</ul>
<h3>Example:</h3>
<p>To store comments from a locally hosted web app to a locally hosted database with the username "username" and the database "comments":</p>
<code>./comment_scraper.py -o mysql -n 10 -u http://127.0.0.1 -H "localhost" -U username p -D comments</code>
<br>
<h3>Setup:</h3>
<ul>
  <li>Python Setup</li>
  <ul>
    <li>Feel free to use a virtualenv</li>
    <li><code>pip install -r requirements.txt</code></li>  
  </ul>
  <li>Database Setup</li>
  <ul>
    <li>Install a database server: <code>sudo apt install mariadb-server</code></li>
    <li>Log in to the database: <code>sudo mysql</code></li>
    <li>Create a database user: <code>CREATE USER username IDENTIFIED BY password;</code></li>
    <li>Create a database to user: <code>CREATE DATABASE comments;</code></li>
    <li>Give the user privileges: <code>GRANT ALL PRIVILEGES ON comments.* TO 'username'@'%';</code></li>
    <li>Flush privileges: <code>FLUSH PRIVILEGES;</code></li>
  </ul>
</ul>
