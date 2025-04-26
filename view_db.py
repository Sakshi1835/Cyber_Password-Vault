import sqlite3

def view_database():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    cursor.execute("SELECT username, website, password, decrypted_password FROM users")
    rows = cursor.fetchall()

    if rows:
        print(f"{'Username':<20} {'Website':<20} {'Encrypted Password':<40} {'Decrypted Password':<20}")
        print("-" * 110)
        for row in rows:
            username, website, encrypted_password, decrypted_password = row
            print(f"{username:<20} {website:<20} {str(encrypted_password):<40} {decrypted_password:<20}")
    else:
        print("No data found in the database.")

    conn.close()

if __name__ == "__main__":
    view_database()
