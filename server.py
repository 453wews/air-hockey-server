import socket
import threading
import time
import os

players = []
player_id = 0
lock = threading.Lock()

def handle_client(conn, addr, pid):
    print(f"Player {pid} connected")
    try:
        conn.send(f"CONNECTED:{pid}\n".encode())
        
        with lock:
            if len(players) < 2:
                conn.send("WAITING\n".encode())
        
        # Ждем второго игрока
        while True:
            with lock:
                if len(players) >= 2:
                    break
            time.sleep(1)
        
        conn.send("MATCH_START:true\n".encode())
        print(f"Match started for player {pid}")
        
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            with lock:
                for p in players:
                    if p[0] != conn:
                        try:
                            p[0].send(data.encode())
                        except:
                            pass
    except:
        pass
    finally:
        with lock:
            players.remove((conn, pid))
        print(f"Player {pid} disconnected")

def start_server():
    port = int(os.environ.get("PORT", 8889))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(2)
    print(f"🏒 AIR HOCKEY SERVER STARTED on port {port}")
    
    global player_id
    while True:
        conn, addr = server.accept()
        player_id += 1
        with lock:
            players.append((conn, player_id))
        thread = threading.Thread(target=handle_client, args=(conn, addr, player_id))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    start_server()