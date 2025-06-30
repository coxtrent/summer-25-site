# Hidden Genius Project Example Website

A lightweight example website for the Hidden Genius Project's final website project.

## Table of Contents

- [README Files](#readmefiles)
- [Installation + GitHub Refresher](#installation--github-refresher)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)


## Installation + GitHub Refresher
3 steps:
1. Clone this project (Remember, GitHub calls a project a "repository" or "repo")

Open a terminal. Remember, Terminal is just text-only Finder/File Explorer (but better).
You can see the folder you're in, a.k.a. your **present working directory** (PWD), by typing `pwd` and pressing Enter:
```bash
trentonmichael@hiddengenius ~  % pwd
/Users/trentonmichael
```
Check what's inside the folder. Type `ls` and press enter to use Terminal's **list** command:
```bash
trentonmichael@hiddengenius ~  % ls

Applications		genius_update.py	Pictures
Desktop			Google Drive		playground
Documents		Library			Public
Downloads		Movies			server.py
eventhandling		Music			test
example_site		networking_activity	Unity
```
```bash
git clone https://github.com/coxtrent/summer-25-site.git
```
You should now see it in your current directory. You can
Then, navigate into the directory with the cloned repo.
```bash
cd summer-25-site
```
2. Create the database
`.sql` files are NOT DATABASES, they only contain code for USING databases.
```sql
sqlite3 login.db < create_login_db.sql
```
3. Run the server
```bash
git clone https://github.com/coxtrent/summer-25-site.git
```
```python
python3 server.py
```





## Usage

Explain how to use your project.

```bash
# Example usage
python main.py
```
## README Files
Always add a README file to your GitHub repositories. It can help other users figure out how to use your project, and can help you remember how to get back into the project if you haven't touched it in awhile.

## Contributing

Guidelines for contributing to the project.

## License

This project is licensed under the [MIT License](LICENSE).