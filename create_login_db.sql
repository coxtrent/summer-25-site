CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    salt TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL
);

INSERT INTO users (username, salt, password_hash, first_name, last_name) 
VALUES ('genius', 'bdc9cc659d18c4ef2376db55e4d525ed', '3d434871f50194a23db5e4b64846a75bc93aa6d347730f1882f289319b922a1f', 'James', 'Green');
-- Where is the password?

-- We don't store passwords directly. Instead, we store a hash of the password.
-- Hashing is a one-way encryption process that always turns the same password into the same hash.
-- This way, even if someone gets access to the database, they can't see the actual passwords

-- We also use a unique salt for each user.
-- A salt is a random string added to the password before hashing.
-- This means that two users with the same password will have different hashes.
-- But the salt is unique to the user, so it will still generate the same hash when that user enters the right password.
-- This makes it much harder for attackers to crack the passwords, even if they have access to the database.