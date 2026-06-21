import os
import json
import sqlite3
import mimetypes
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

DB_FILE = "carbonpulse.db"
PORT = 8000
STATIC_DIR = "dist"

def init_db():
    """Initializes the SQLite database and calculations ledger table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            transport REAL NOT NULL,
            energy REAL NOT NULL,
            diet REAL NOT NULL,
            waste REAL NOT NULL,
            total REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print(f"📁 SQLite database '{DB_FILE}' initialized successfully.")

class EcosphereAPIHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS for development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed_url = urlparse(self.path)
        
        # Route API Requests
        if parsed_url.path == '/api/history':
            self.handle_get_history()
            return
            
        # Serve Static Files
        self.serve_static_files(parsed_url.path)

    def do_POST(self):
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == '/api/history':
            self.handle_post_history()
            return
            
        self.send_error(404, "Endpoint not found")

    def do_DELETE(self):
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == '/api/history':
            self.handle_delete_history(parsed_url.query)
            return
            
        self.send_error(404, "Endpoint not found")

    def handle_get_history(self):
        """Retrieves and returns all ledger entries from SQLite database."""
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM calculations ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                history.append({
                    "id": row["id"],
                    "timestamp": row["timestamp"],
                    "transport": row["transport"],
                    "energy": row["energy"],
                    "diet": row["diet"],
                    "waste": row["waste"],
                    "total": row["total"]
                })
            conn.close()
            
            response_data = json.dumps(history).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response_data)))
            self.end_headers()
            self.wfile.write(response_data)
            
        except Exception as e:
            self.send_error(500, f"Database error: {str(e)}")

    def handle_post_history(self):
        """Saves a new calculation entry to the SQLite database ledger."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            entry = json.loads(post_data.decode('utf-8'))
            
            # Validate input properties
            required_fields = ["transport", "energy", "diet", "waste", "total"]
            if not all(field in entry for field in required_fields):
                self.send_error(400, "Missing required calculation values")
                return

            timestamp = datetime.now().isoformat()
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO calculations (timestamp, transport, energy, diet, waste, total)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp, entry["transport"], entry["energy"], entry["diet"], entry["waste"], entry["total"]))
            
            inserted_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            response_payload = json.dumps({
                "id": inserted_id,
                "timestamp": timestamp,
                "status": "success"
            }).encode('utf-8')
            
            self.send_response(201)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response_payload)))
            self.end_headers()
            self.wfile.write(response_payload)
            
        except Exception as e:
            self.send_error(550, f"Error processing database write: {str(e)}")

    def handle_delete_history(self, query_string):
        """Deletes a ledger entry by ID."""
        try:
            params = parse_qs(query_string)
            entry_id = params.get('id', [None])[0]
            
            if not entry_id:
                self.send_error(400, "Missing entry ID parameter")
                return
                
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM calculations WHERE id = ?", (entry_id,))
            conn.commit()
            conn.close()
            
            response_payload = json.dumps({"status": "success", "id": entry_id}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response_payload)))
            self.end_headers()
            self.wfile.write(response_payload)
            
        except Exception as e:
            self.send_error(500, f"Database deletion error: {str(e)}")

    def serve_static_files(self, path):
        """Serves compiled frontend files from dist directory."""
        # Sanitize path to avoid path traversal vulnerability
        clean_path = path.lstrip('/')
        if not clean_path or clean_path == '':
            clean_path = 'index.html'
            
        file_path = os.path.join(STATIC_DIR, clean_path)
        
        # Fallback to index.html for SPA client-side routing
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            file_path = os.path.join(STATIC_DIR, 'index.html')
            
        if not os.path.exists(file_path):
            self.send_error(404, "Static file assets not built. Run 'npm run build' first.")
            return

        # Determine MIME Type
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'

        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                
            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading asset file: {str(e)}")

def run_server():
    init_db()
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, EcosphereAPIHandler)
    print(f"🚀 CarbonPulse API and Asset Server running on http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping CarbonPulse server...")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
