import sqlite3
import json
import os

class AgentBacklog:
    """
    A SQLite-based storage system that strictly maps to the agent JSON envelope.
    """
    
    def __init__(self, db_path="enterprise_backlog.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """
        Creates the database with columns matching the strict JSON schema exactly.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Every key in your schema is now a top-level column.
            # Dicts/Lists (context, payload) will be stored as JSON text.
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    sender TEXT,
                    recipient TEXT,
                    task_type TEXT,
                    context TEXT,
                    payload TEXT,
                    status TEXT,
                    error TEXT
                )
            ''')
            conn.commit()

    def record_interaction(self, message):
        """
        Extracts data according to the strict schema and inserts it into the DB.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Extract fields with safe fallbacks
                msg_id = message.get("id")
                timestamp = message.get("timestamp")
                sender = message.get("sender")
                recipient = message.get("recipient")
                task_type = message.get("task_type")
                status = message.get("status")
                error = message.get("error", "")
                
                # Convert the nested dictionaries into JSON strings for SQLite storage
                context_str = json.dumps(message.get("context", {}))
                payload_str = json.dumps(message.get("payload", {}))
                
                cursor.execute('''
                    INSERT OR IGNORE INTO interactions 
                    (id, timestamp, sender, recipient, task_type, context, payload, status, error)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (msg_id, timestamp, sender, recipient, task_type, context_str, payload_str, status, error))
                
                conn.commit()
                
        except sqlite3.Error as e:
            print(f"[DATABASE ERROR] Failed to record interaction: {e}")

    def get_agent_history(self, agent_name, limit=50):
        """
        Retrieves the backlog for a specific agent and reconstructs the strict JSON format.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row 
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM interactions
                    WHERE sender = ? OR recipient = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (agent_name, agent_name, limit))
                
                rows = cursor.fetchall()
                reconstructed_messages = []
                
                for row in rows:
                    # Rebuild the dictionary exactly as the schema dictates
                    message = {
                        "id": row["id"],
                        "timestamp": row["timestamp"],
                        "sender": row["sender"],
                        "recipient": row["recipient"],
                        "task_type": row["task_type"],
                        # Parse the JSON strings back into Python dictionaries
                        "context": json.loads(row["context"]),
                        "payload": json.loads(row["payload"]),
                        "status": row["status"],
                        "error": row["error"]
                    }
                    reconstructed_messages.append(message)
                    
                return reconstructed_messages
                
        except sqlite3.Error as e:
            print(f"[DATABASE ERROR] Failed to retrieve history: {e}")
            return []
            
    def clear_backlog(self):
        """Utility method to wipe the database for fresh testing."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            self._initialize_db()