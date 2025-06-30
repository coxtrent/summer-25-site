#TODO: Add session cookies for user authentication
import socket
import os
import sqlite3
import hashlib
import urllib.parse

conn = sqlite3.connect('login.db')

ROUTES = {}
# the above code imports necessary libraries, connects to the database, and initializes a dictionary to store route handlers.



# This function is a decorator that registers a function as a route handler for a specific route.
# It allows us to define which function should be called when a specific URL route is requested.
def route(path):
    def decorator(func):
        ROUTES[path] = func
        return func
    return decorator

# This function retrieves a file from the server's directory and returns its content as an HTTP response.
def get_file(filename, content_type="text/html"):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return f"HTTP/1.1 200 OK\nContent-Type: {content_type}\n\n{content}"
    except Exception:
        return "HTTP/1.1 500 INTERNAL SERVER ERROR\n\nError loading file: " + filename

# This function retrieves a binary image file and returns it as an HTTP response.
def get_image(filename, content_type="image/png"):
    """Serve binary image files (e.g., .ico, .png, .jpg)."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, filename)
        with open(file_path, "rb") as f:
            content = f.read()
        header = f"HTTP/1.1 200 OK\nContent-Type: {content_type}\n\n".encode("utf-8")
        return header + content
    except Exception:
        return b"HTTP/1.1 500 INTERNAL SERVER ERROR\n\nError loading file: " + filename.encode("utf-8")

# This function parses the form data from the HTTP request body and returns it as a Python dictionary.
def parse_form_data(request):
    """Extracts form data from the HTTP request body and returns a dict."""
    try:
        body = request.split('\r\n\r\n', 1)[1]
    except (IndexError, AttributeError):
        return {}
    # Decode URL-encoded form data
    return dict(urllib.parse.parse_qsl(body))

# Utility functions to hash passwords. 
# A hash is a one-way encryption. 
# The same password always makes the same hash, but you cannot reverse it to get the original password.
# Use salted hashes. 
# Every password should get hashed with a unique "salt.""
# Imagine every person in the database as having a unique, custom seasoning.
# Every password is like a dish. Even if two users have the same dish, 
# they will have different tastes because they are seasoned differently.
# If a password is "password123", one user's salt might be "KRLXST"
# So we literally combine them into "password123KRLXST" and then hash that.
# If another user has password "password123" but a different salt "AYOOO",
# we combine them into "password123AYOOO" and hash that.
# This way, even if two users have the same password, their hashes will be different.
# This makes it harder for attackers to crack the passwords, even if they get access to the database.
def hash_password(password):
    """Generate a random salt and hash the password. Returns (salt_hex, hash_hex)."""
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
    return salt.hex(), hashed.hex()

def hash_password_with_salt(password,salt):
    """Hash the password with the given salt."""
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 100_000)
    return hashed.hex()

# PAGE ROUTES 

# This route serves the home page
@route("/")
def home():
    return get_file("index.html")

# This route serves the about page
@route("/about")
def about():
    return get_file("about.html")

# This route serves the login page
@route("/login")
def login_page():
    return get_file("login.html")


# ROUTES FOR STATIC FILES
# Static files are files that do not change and are served directly to the user, such as CSS, JavaScript, and images.

# This route serves the CSS file
@route("/style.css")
def css():
    return get_file("style.css", content_type="text/css")

# This route serves the JavaScript file
@route("/script.js")
def js():
    return get_file("script.js", content_type="application/javascript")

# This route serves the favicon
# The favicon is the small icon that appears in the browser tab.
@route("/favicon.ico")
def favicon():
    return get_image("favicon.ico", content_type="image/x-icon")


# REST API ROUTES


# This route serves login requests
@route("/api/login")
def login(request):
    # This part extracts (parses) the data from the request
    params = parse_form_data(request)
    username = params.get('username')
    password = params.get('password')
    # Check if username and password are provided
    if not username or not password:
        return "HTTP/1.1 400 BAD REQUEST\n\nMissing username or password."
   

    # Attempt to login by asking database for user-pass hash combo

    # connect to database
    cursor = conn.cursor()
    # Get this user's salt
    cursor.execute("SELECT salt, password_hash FROM users WHERE username=?", (username,))
    # Fetch the result
    # If the user does not exist, this will return None, a type of Python object that is basically "nothing"
    result = cursor.fetchone()
    if not result:
        # If the result is None, it means the user does not exist. 
        # Don't tell the user if it's the username or password that is wrong, just say "login failed"
        # This is a security measure to prevent attackers from knowing if the username exists.
        # This prevents brute force attacks where an attacker tries to guess the username and password.
        return "HTTP/1.1 401 UNAUTHORIZED\n\nLogin failed: Invalid username or password."
    # If the user exists, we get the salt and password hash from the database
    salt, stored_hash = result
    # Now we hash the password with the salt we got from the database
    password_hash = hash_password_with_salt(password, salt)
    if password_hash != stored_hash:
        return "HTTP/1.1 401 UNAUTHORIZED\n\nLogin failed: Invalid username or password."
    return "HTTP/1.1 200 OK\n\nLogin successful!"
    
# This route will log the user out, but we will add cookies/sessions for this to work.
@route("/api/logout")
def logout():
    # In a real application, you would handle session management here
    return "HTTP/1.1 200 OK\n\nYou have been logged out successfully."

# This route adds a new user to the database
@route("/api/create_user")
def create_user(request):
    # Extract the form data from the request
    params = parse_form_data(request)
    username = params.get('username')
    password = params.get('password')
    first_name = params.get('first_name')
    last_name = params.get('last_name')
    # Check if all fields are provided
    if not username or not password or not first_name or not last_name:
        return "HTTP/1.1 400 BAD REQUEST\n\nMissing required fields."

    cursor = conn.cursor()
    salt, password_hash = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, salt, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
                       (username, salt, password_hash, first_name, last_name))
        conn.commit()
        return "HTTP/1.1 201 CREATED\n\nUser created successfully."
    except sqlite3.IntegrityError:
        return "HTTP/1.1 409 CONFLICT\n\nUsername already exists."

# Router function
# This decides which function to call based on the request route
def handle_request(request):
    try:
        path = request.split(" ")[1]
    except IndexError:
        path = "/"
    
    handler = ROUTES.get(path)
    if handler:
        # Pass the request to /api/login, otherwise call with no arguments
        if "/api" in path:
            return handler(request)
        else:
            return handler()
    else:
        return "HTTP/1.1 404 NOT FOUND\n\nPage not found."
    

# this function starts listening for requests
def start_server(host='localhost', port=8080):
    # These lines start listening 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Serving on http://{host}:{port}")

    # Now the server is ready to listen
    while True:
        client_socket, addr = server_socket.accept() # Server waits on this line for a client to connect
        request = client_socket.recv(1024).decode('utf-8')
        print(f"\nReceived request:\n{request}")

        response = handle_request(request)
        if isinstance(response, bytes):
            client_socket.sendall(response)
        else:
            client_socket.sendall(response.encode('utf-8'))
        client_socket.close()

if __name__ == "__main__":
    start_server()

""" What happens when you login?
1. user enters info and clicks login in HTML
    -> browser sends a request to /api/login with ur username and pass USING JAVASCRIPT
        -> server uses URL to route the request to the login function USING PYTHON
            -> login function sends the request to the database USING SQL
                -> database checks if the username and password match
                    -> if they match, return a success message
                    -> if they don't match, return a failure message
"""







# generalizing sections of code to abstract away details 
# but also explained the code in more detail
# provide some notes, maybe some slides, or a video to explain the code
