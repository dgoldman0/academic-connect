import sqlite3
from datetime import datetime, timedelta

class DBManager:
    def __init__(self, db_name=":memory:"):
        # Connect to the database
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self._create_tables()

    def _create_tables(self):
        # Create Requests table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Requests (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            request TEXT NOT NULL,
            bot_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create Restricted table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Restricted (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE
        )
        """)
        
        # Commit the changes
        self.conn.commit()

    def isRestricted(self, username):
        self.cursor.execute("SELECT * FROM Restricted WHERE username=?", (username,))
        return self.cursor.fetchone() is not None

    def canAsk(self, username, timeout):
        # Calculate the time before the current time by the timeout duration
        check_time = datetime.now() - timedelta(seconds=timeout)
        self.cursor.execute("""
        SELECT * FROM Requests 
        WHERE username=? AND timestamp>=?
        """, (username, check_time.strftime('%Y-%m-%d %H:%M:%S')))
        
        # Return True if no requests found within the timeout period
        return self.cursor.fetchone() is None
