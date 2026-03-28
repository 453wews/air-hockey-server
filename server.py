import socket
import threading
import time
import os
import sys

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
        
        # Ждем второго игрока
        waiting_time = 0
        while True:
            with lock:
                if len(players) >= 2:
                    break
            time.sleep(1)
            waiting_time += 1
            if waiting_time > 60:
                conn.send("TIMEOUT\n".encode())
                conn.close()
                return
            # Отправляем статус ожидания
            try:
                conn.send("WAITING\n".encode())
            except:
                return
        
        # Начинаем матч
        conn.send("MATCH_START:true\n".encode())
        print(f"Match started for player {pid}")
        
        # Пересылка сообщений между игроками
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break
                
                print(f"Player {pid} sent: {data}")
                
                with lock:
                    for p in players:
                        if p[0] != conn:
                            try:
                                p[0].send(data.encode())
                                print(f"Forwarded to player {p[1]}")
                            except Exception as e:
                                print(f"Forward error: {e}")
            except Exception as e:
                print(f"Receive error: {e}")
                break
                
    except Exception as e:
        print(f"Handler error: {e}")
    finally:
        with lock:
            for i, p in enumerate(players):
                if p[0] == conn:
                    players.pop(i)
                    break
        print(f"Player {pid} disconnected. Total players: {len(players)}")
        try:
            conn.close()
        except:
            pass

def start_server():
    port = int(os.environ.get("PORT", 8889))
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(10)
    
    print("=" * 50)
    print(f"🏒 AIR HOCKEY SERVER STARTED")
    print(f"📡 PORT: {port}")
    print(f"🌐 WAITING FOR PLAYERS...")
    print("=" * 50)
    sys.stdout.flush()
    
    global player_id
    while True:
        try:
            conn, addr = server.accept()
            player_id += 1
            with lock:
                players.append((conn, player_id))
            print(f"✅ Player {player_id} connected. Total: {len(players)}")
            sys.stdout.flush()
            
            thread = threading.Thread(target=handle_client, args=(conn, addr, player_id))
            thread.daemon = True
            thread.start()
        except Exception as e:
            print(f"Accept error: {e}")
            sys.stdout.flush()

if __name__ == "__main__":
    start_server()
