import socket
import os
import sqlite3
import hashlib
import urllib.parse

conn = sqlite3.connect('login.db')

ROUTES = {}

#TODO: Add session cookies for user authentication


def route(path):
    def decorator(func):
        ROUTES[path] = func
        return func
    return decorator

def get_file(filename, content_type="text/html"):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return f"HTTP/1.1 200 OK\nContent-Type: {content_type}\n\n{content}"
    except Exception:
        return "HTTP/1.1 500 INTERNAL SERVER ERROR\n\nError loading file: " + filename
    
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


def parse_form_data(request):
    """Extracts form data from the HTTP request body and returns a dict."""
    try:
        body = request.split('\r\n\r\n', 1)[1]
    except (IndexError, AttributeError):
        return {}
    # Decode URL-encoded form data
    return dict(urllib.parse.parse_qsl(body))

# Utility function to hash passwords
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

# This route serves the CSS file
@route("/style.css")
def css():
    return get_file("style.css", content_type="text/css")

# This route serves the JavaScript file
@route("/script.js")
def js():
    return get_file("script.js", content_type="application/javascript")

@route("/favicon.ico")
def favicon():
    return get_image("favicon.ico", content_type="image/x-icon")


# REST API ROUTES


# This route serves login requests
@route("/api/login")
def login(request):
    params = parse_form_data(request)
    username = params.get('username')
    password = params.get('password')
    # Check if username and password are provided
    if not username or not password:
        return "HTTP/1.1 400 BAD REQUEST\n\nMissing username or password."
   
    # Validate credentials against the database

    # hash the password
    cursor = conn.cursor()
    cursor.execute("SELECT salt, password_hash FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    if not result:
        return "HTTP/1.1 401 UNAUTHORIZED\n\nLogin failed: Invalid username or password."
    salt, stored_hash = result
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
    # Extract body from the request (after double newline)
    try:
        body = request.split('\r\n\r\n', 1)[1]
    except (IndexError, AttributeError):
        return "HTTP/1.1 400 BAD REQUEST\n\nMissing request body."

    # Parse form data: username=...&password=...
    params = dict(param.split('=') for param in body.split('&') if '=' in param)
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
