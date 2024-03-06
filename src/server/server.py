import socket
import threading
import time
import uuid
import commands as cmds
import game
import json
HOST = '127.0.0.1'
PORT = 5000
FORMAT = 'utf-8'
ADDR = (HOST, PORT)


connections = {}
games = []

# Function that handles the second parallel client
# Only when 2 clients are connected simultaneously, this function will handle the second client
def handle_client(conn: socket.socket, addr):
    print('[CLIENT CONNECTED] on address: ', addr)  # Printing connection address
    token = uuid.uuid4()
    username = ""
    connections[addr] = (conn,token)
    conn.send("{}".format(token).encode(FORMAT))

    while True:
        try:
            cmd = conn.recv(4096)
            req = cmd.decode(FORMAT).split(" ")
            sendall = False
            if req[0] != connections[addr][1]:
                break
            req = req[1::]
            # login
            if req[0] == "login":
                if cmds.login(req):
                    data = "logged"
                    username = req[1]
                else: 
                    data = "not_found"

            # sign up
            elif req[0] == "signup":
                if cmds.signup(req):
                    data = "signed_up"
                else:
                    data = "usr_unavl"

            # new game
            elif req[0] == "new_game":
                game_id = len(games)
                games.append(cmds.new_game(req,game_id))
                data = "crtd_gm {}".format(game_id)

            # list available games
            elif req[0] == "aval_games":
                data = cmds.aval_games(games)

            # req to join game
            elif req[0] == "join_game":
                id = cmds.join_game(req)
                if id > 0:
                    data = "jnd_gm {}".format(id)
                else:
                    data = "unable_jn"

            # ask to spec game
            elif req[0] == "spec":
                g : game.Game = games[int(req[1])]
                g.add_spectator(conn)
                data = "spec_succ"

            # players makes a move
            elif req[0] == "move":
                g : game.Game = games[int(req[1])]
                g.move(req[2],req[3])
                data = "board {}".format(json.dump(g.board))

            # respond to client/s
            if not sendall: conn.send(data.encode(FORMAT))
            else:
                all = list(g.players.values())
                all.append(g.spectators)
                for conn in all:
                    conn.send(data.encode(FORMAT))
        except:
            print("[CLIENT CONNECTION INTERRUPTED] on address: ", addr)


# Function that starts the server
def start_server():
    server_socket.bind(ADDR)  # binding socket with specified IP+PORT tuple

    print(f"[LISTENING] server is listening on {HOST}")
    server_socket.listen()  # Server is open for connections

    while True:
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}\n")  # printing the amount of threads working

        connection, address = server_socket.accept()  # Waiting for client to connect to server (blocking call)

        thread = threading.Thread(target=handle_client, args=(connection, address))
        thread.start()


if __name__ == '__main__':
    IP = socket.gethostbyname(socket.gethostname())

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("[STARTING] server is starting...")
    start_server()

    print("THE END!")

