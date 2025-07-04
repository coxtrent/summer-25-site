# Hidden Genius Project Example Website

A lightweight example website for the Hidden Genius Project's final website project.

## Table of Contents

- [Installation + Terminal Refresher](#installation--terminal-refresher)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)


## Installation + Terminal Refresher
**Open VS Code, Press Cmd+Shift+P, and type "Shell Command: Install 'code' command in PATH".**<br>
Click that, follow any prompts, and now you can open VS Code from any terminal. More on that later.

Open a terminal. Remember, Terminal is just text-only Finder/File Explorer (but better).<br>
You can see the folder you're in, a.k.a. your **present working directory** (PWD), by typing `pwd` and pressing Enter:
```bash
pwd
```
Terminal will spit out something like this:
```
/Users/trentonmichael
```

Check what's inside the folder. Type `ls` and press enter to use Terminal's **list** command:
```bash
ls
```
Now it'll show something like this:
```bash
Applications		genius_update.py	Pictures
Desktop			Google Drive		playground
Documents		Library			Public
Downloads		Movies			server.py
eventhandling		Music			test
example_site		networking_activity	Unity
```
Now, copy this project; or, in Git terms, **clone this repository**.
```bash
git clone https://github.com/coxtrent/summer-25-site.git
```
You should now see it in your current directory. Type `ls` again and you'll see a folder named `summer-25-site` listed.<br>
Then, navigate into the directory with the cloned repo. Change your **current directory** with `cd` followed by the directory name.
```bash
cd summer-25-site
```
Now do `ls` one more time and you should see all the same files listed on this GitHub webpage.<br>

Type `code .` into terminal. This will open the `pwd` in VS Code.
```bash
code .
```

## Usage 
1. Create the database<br>
`.sql` files are NOT DATABASES; they only contain code for doing database things (making them, changing them, etc).<br>
Run this in a terminal in your VS Code project.
```bash
sqlite3 login.db < create_login_db.sql
```
You only have to do this once.<br>
If you want to reset the database, run the code below to remove the database, then run the code above to make it again.
```bash
rm login.db
```
2. Run the server with Python.
```python
python3 server.py
```

3. Test the website<br>
Click around. It's a pretty basic site right now. The only user in the database has the username 'genius' and the password 'revealed'. If you login with anything else, you'll notice the page will give you an error message. If you use this password, you'll notice it doesn't behave as you'd expect. That's where cookies/sessions come in. We will discuss how to set this up in training.