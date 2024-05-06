import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import xml.etree.ElementTree as ET
import Physics
import random

current_turn = None

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = self.path.split("?")[0]
        if parsed_path == '/':
            self.send_response(302)
            self.send_header('Location', '/shoot.html')
            self.end_headers()
        elif parsed_path == "/shoot.html":
            self._serve_html_file("shoot.html")
        elif parsed_path == "/fetch_svg":
            self.gsvg()
        elif parsed_path == '/current_turn':
            global current_turn
            if current_turn is None:
                current_turn = random.choice(['Player 1', 'Player 2'])
            response_data = {'current_turn':current_turn}
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        elif parsed_path == "/get_players":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            players = {'player1Name': 'Player 1', 'player2Name': 'Player 2'}  # Default player names
            self.wfile.write(json.dumps(players).encode('utf-8'))
        elif parsed_path.endswith(".svg"):
            self._serve_static_file(parsed_path, 'image/svg+xml')
        elif parsed_path == "/favicon.ico":  # Handle favicon request
            self.send_response(204)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed_post_data = json.loads(post_data)

        # Process the velocity data if it's being sent
        if self.path == '/send_data':
            velocity_x = parsed_post_data.get('velocityX')
            velocity_y = parsed_post_data.get('velocityY')
            player_names = parsed_post_data.get('playerNames')
            
            if velocity_x is not None and velocity_y is not None and player_names is not None:
                self.process_velocity(velocity_x, velocity_y)
                self.player1_name = player_names.get('player1Name')
                self.player2_name = player_names.get('player2Name')
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.send_header('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
                self.end_headers()
                self.wfile.write(b"Initial velocity received and processed successfully.")
                
                svg_data = parsed_post_data.get('svg', '')    
                try:
                    velocity_x = -(float(velocity_x)) *10
                    velocity_y = -(float(velocity_y))*10
                    root = ET.fromstring(svg_data)
                    table = Physics.Table()  # Assuming this is a list to store the table balls
                    for child in root:
                        if child.tag.endswith('circle'):
                            cx = float(child.attrib.get('cx', 0))
                            cy = float(child.attrib.get('cy', 0))
                            r = float(child.attrib.get('r', 0))
                            fill = child.attrib.get('fill', '')
                            if r < 30:
                                if fill == 'WHITE':
                                    table += (Physics.StillBall(0,Physics.Coordinate(cx,cy)))
                                else:    
                                    ball_number = Physics.BALL_COLOURS.index(fill)
                                    table += (Physics.StillBall(ball_number, Physics.Coordinate(cx, cy)))
                    db = Physics.Database()
                    tableidd = db.getLastTableID() or 0
                    if(tableidd == 0):
                        db.writeTable(table)
                    tableid = db.getLastTableID()
                    tablee = db.readTable(tableid)             
                    game = Physics.Game(gameID=None, gameName="8Ball", player1Name=self.player1_name, player2Name=self.player2_name)
                    game.shoot("8-Ball", game.current, tablee, velocity_x, velocity_y)
                    game.switch()
                    self.switch_turns()
                    
                except ET.ParseError as e:
                    print(f"Error parsing SVG data: {e}")
                    self.send_error(400, "Bad Request: Invalid SVG data")
         
            else:
                self.send_error(400, "Bad Request: Missing velocity or player name data")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")
        

    def _serve_html_file(self, file_name):
        try:
            with open(file_name, 'rb') as file:
                content = file.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def _serve_static_file(self, file_path, content_type):
        try:
            with open(file_path[1:], 'rb') as file:
                content = file.read()
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

    def process_velocity(self, velocity_x, velocity_y):
        print('Received initial velocity X:', velocity_x)
        print('Received initial velocity Y:', velocity_y)
        with open('velocity_data.txt', 'a') as file:
            file.write(f"Velocity X: {velocity_x}, Velocity Y: {velocity_y}\n")

    def gsvg(self):
        try:
            svg_list = []  # List to store SVG data for each table
            db = Physics.Database()
            table_id = 0
            table = db.readTable(table_id)

            while table:
                svg_list.append(table.svg())
                table_id += 1
                table = db.readTable(table_id)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(svg_list).encode('utf-8'))
        except Exception as e:
            print(f"Error generating SVG data: {e}")
            self.send_error(500, "Internal Server Error")
            
    def switch_turns(self):
        global current_turn
        if current_turn == 'Player 1':
            current_turn = 'Player 2'
        else:
            current_turn = 'Player 1'

def run_server(port):
    httpd = HTTPServer(('localhost', port), MyHandler)

    print("Server listening on port:", port)
    httpd.serve_forever()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)
    run_server(int(sys.argv[1]))
