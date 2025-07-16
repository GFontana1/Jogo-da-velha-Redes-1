import socket
import threading

HOST = '0.0.0.0'
PORT = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)

clients = {}
board = [[None] * 3 for _ in range(3)]
current_player = ['X']
lock = threading.Lock()

def broadcast(message):
    for client in clients:
        try:
            client.sendall(message.encode())
        except:
            pass

def send_board_update(simbolo, linha, coluna):
    msg = f"ATUALIZA {simbolo},{linha},{coluna}\n"
    broadcast(msg)

def verificar_vitoria():
    # Verifica linhas
    for linha in board:
        if linha[0] == linha[1] == linha[2] and linha[0] is not None:
            return linha[0]
    # Verifica colunas
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] is not None:
            return board[0][col]
    # Verifica diagonais
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2]
    return None

def verificar_empate():
    return all(all(c is not None for c in linha) for linha in board)

def handle_client(conn, addr):
    simbolo = None

    with lock:
        if 'X' not in clients.values():
            simbolo = 'X'
        elif 'O' not in clients.values():
            simbolo = 'O'
        else:
            conn.sendall(b"ESPECTADOR\n")
            conn.close()
            return
        clients[conn] = simbolo

    conn.sendall(f"SEU_SIMBOLO {simbolo}\n".encode())

    if simbolo == current_player[0]:
        conn.sendall(b"SUA_VEZ\n")
    else:
        conn.sendall(b"AGUARDE\n")

    buffer = ""
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            buffer += data
            while '\n' in buffer:
                linha, buffer = buffer.split('\n', 1)

                if linha.startswith("JOGADA"):
                    _, pos = linha.split()
                    linha_idx, col_idx = map(int, pos.split(','))
                    with lock:
                        if simbolo == current_player[0] and board[linha_idx][col_idx] is None:
                            board[linha_idx][col_idx] = simbolo
                            send_board_update(simbolo, linha_idx, col_idx)

                            vencedor = verificar_vitoria()
                            if vencedor:
                                broadcast(f"VITORIA {vencedor}\n")
                            elif verificar_empate():
                                broadcast("VITORIA EMPATE\n")
                            else:
                                current_player[0] = 'O' if current_player[0] == 'X' else 'X'
                                for c in clients:
                                    if clients[c] == current_player[0]:
                                        c.sendall(b"SUA_VEZ\n")
                                    else:
                                        c.sendall(b"AGUARDE\n")

                elif linha.startswith("REINICIAR"):
                    with lock:
                        board[:] = [[None] * 3 for _ in range(3)]
                        current_player[0] = 'X'
                        for c in clients:
                            c.sendall(b"AGUARDE\n")
                        for c in clients:
                            if clients[c] == 'X':
                                c.sendall(b"SUA_VEZ\n")
        except:
            break

    with lock:
        del clients[conn]
    conn.close()

print(f"Servidor TCP ouvindo em {HOST}:{PORT}...")
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()