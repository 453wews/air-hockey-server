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
    except Exception as e:
        print(f"Error: {e}")
    finally:
        with lock:
            players.remove((conn, pid))
        print(f"Player {pid} disconnected")

def start_server():
    # Берем порт из переменной окружения, если нет - используем 10000
    port = int(os.environ.get("PORT", 10000))
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind(('0.0.0.0', port))
        server.listen(2)
        
        # ВЫВОДИМ ПОРТ В ЛОГИ - ЭТО ВАЖНО!
        print("=" * 50)
        print(f"✅ SERVER STARTED SUCCESSFULLY")
        print(f"✅ PORT: {port}")
        print(f"✅ ADDRESS: 0.0.0.0:{port}")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ FAILED TO START ON PORT {port}: {e}")
        return
    
    global player_id
    while True:
        try:
            conn, addr = server.accept()
            player_id += 1
            with lock:
                players.append((conn, player_id))
            print(f"👤 Player {player_id} connected")
            thread = threading.Thread(target=handle_client, args=(conn, addr, player_id))
            thread.daemon = True
            thread.start()
        except Exception as e:
            print(f"Error accepting connection: {e}")

if __name__ == "__main__":
    start_server()
