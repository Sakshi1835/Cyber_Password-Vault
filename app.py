from flask import Flask, render_template, request
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os
import sqlite3
from flask_bcrypt import Bcrypt
from flask import redirect


app = Flask(__name__)
bcrypt = Bcrypt(app)
key = os.urandom(32)


def get_db_connection():
    try: 
        conn = sqlite3.connect("test.db")
        print("Database Connected Successfully")
        return conn
    except Exception as e:
        print(f"Database Connection Failed: {e}")

    """Get a new SQLite connection for the current thread."""
    # return sqlite3.connect(r"C:\Users\Sakshi\OneDrive\Desktop\new project\test.db", check_same_thread=False)

def encrypt_password(message, key):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(message.encode('utf-8'))
    nonce = cipher.nonce
    return ciphertext, tag, nonce

def decrypt_password(ciphertext, key, tag, nonce):
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    decrypted_message = cipher.decrypt_and_verify(ciphertext, tag)
    return decrypted_message.decode('utf-8')


conn = get_db_connection()
conn.execute(
    "CREATE TABLE IF NOT EXISTS users (username VARCHAR(255) NOT NULL, website VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL, decrypted_password VARCHAR(255))"
)
conn.commit()


def get_passwords_from_database():
    """Fetch passwords from the database."""
    conn = get_db_connection()
    results = conn.execute("SELECT username, website, password FROM users").fetchall()
    conn.close()
    return results


@app.route("/")
def index():
    conn = get_db_connection()
    results = get_passwords_from_database()
    conn.close()
    return render_template("index.html", results=results)
    

@app.route("/store_password", methods=["POST"])
def store_password():
    username = request.form.get("user1")
    website = request.form.get("web1")
    password = request.form.get("pass1")
    
    encrypted_password, tag, nonce = encrypt_password(password, key)
    decrypted_password = decrypt_password(encrypted_password, key, tag, nonce)

    conn = get_db_connection()
    conn.execute(   
        "INSERT INTO users (username,website,password,decrypted_password) VALUES (?,?,?,?);",
        (username, website, encrypted_password,decrypted_password),
    )

    conn.commit()
    updated_results = get_passwords_from_database()
    conn.close()

    # Render the template with the updated data
    return render_template("index.html", results=updated_results)

@app.route('/delete_all', methods=['POST'])
def delete_all():
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute('DELETE FROM users')
    # c.execute('VACUUM')   # Deletes all rows
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/view_password', methods=['POST'])
def view_passwords():
    entered_root_password = request.form.get('root1')
    
    root_password = '1234'  

    root_password_hash = bcrypt.generate_password_hash(root_password)
    entered_root_password_hash = bcrypt.generate_password_hash(entered_root_password)

    if root_password == entered_root_password:
        conn = get_db_connection()
        dec_results = conn.execute("SELECT website, username, decrypted_password FROM users").fetchall()
        conn.close()
        return render_template("index.html", results=dec_results)
    else:
        return "Incorrect Root Password"



if __name__ == "__main__":
    app.run(debug=True)
