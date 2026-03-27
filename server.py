import socket
import threading
import time
import os

players = []
player_id = 0
lock = threading.Lock()

def handle_client(conn, addr, pid):
    print(f"Player {pid} connected from {addr}")
    try:
        conn.send(f"CONNECTED:{pid}\n".encode())
        
        with lock:
            if len(players) < 2:
                conn.send("WAITING\n".encode())
        
        waited = 0
        while True:
            with lock:
                if len(players) >= 2:
                    break
            time.sleep(1)
            waited += 1
            if waited > 60:
                conn.send("TIMEOUT\n".encode())
                conn.close()
                return
        
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
    except Exception as e:
        print(f"Error: {e}")
    finally:
        with lock:
            for i, p in enumerate(players):
                if p[0] == conn:
                    players.pop(i)
                    break
        print(f"Player {pid} disconnected")

def start_server():
    # Порт из переменной окружения Render
    port = int(os.environ.get("PORT", 8889))
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(2)
    
    # ЭТА СТРОКА ПОКАЖЕТ ПОРТ В ЛОГАХ!
    print(f"SERVER STARTED ON PORT: {port}")
    print(f"Connection string: air-hockey-server-1.onrender.com:{port}")
    
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
