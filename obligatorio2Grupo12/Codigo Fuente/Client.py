import socket
import threading
import sys
import re

def Client(serverIP, serverPort, vlcPort):
    master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f'bindea sockettcp')

    try:
        master.connect((serverIP, serverPort))
        print(f'se conecta al servidor prendido')
    except socket.error as e:
        print(f'no consigue conectarse, por {e}' )
        master.close()
        return
    threading.Thread(target=consoleData, args=(vlcPort,master)).start()

def consoleData(vlcPort,master):
        buff = ""
        print(f'Se abre hilo de conexión TCP con servidor')
        while True:
            data = input()+"\n"
            buff = data
            if "CONECTAR\n"== data:
                data = data.strip("\n")
                data = data + str(vlcPort) + "\n"
                while data:
                    try:
                        sent = master.send(data.encode())
                        data = data[sent:]
                    except socket.error as e:
                        master.close()
                        return
                print(f'Se envia CONECTAR')

            if "DESCONECTAR\n"== data:
                while data:
                    try:
                        sent = master.send(data.encode())
                        data = data[sent:]
                    except socket.error as e:
                        master.close()
                        return
                print(f'Se envia DESCONECTAR')                    
                master.close()
                print(f'Usted se desconecto! Para ver el video inicialice otra conexion.')
                break
            
            if "INTERRUMPIR\n"== data:
                while data:
                    try:
                        sent = master.send(data.encode())
                        data = data[sent:]
                    except socket.error as e:
                        master.close()
                        return
                print(f'Se envia INTERRUMPIR')
            if "CONTINUAR\n"== data:
                while data:
                    try:
                        sent = master.send(data.encode())
                        data = data[sent:]
                    except socket.error as e:
                        master.close()
                        return
                print(f'Se envia CONTINUAR')    
            
                
            if buff == "CONTINUAR\n" or buff=="CONECTAR\n" or buff=="DESCONECTAR\n" or buff=="INTERRUMPIR\n":
                message = ""
                while ("\n" not in message):
                    try:
                        data = master.recv(1024).decode()
                        message += data
                    except socket.error as e:
                        master.close()
                        return
                message = message.strip("\n")
                print(f'Se recibe {message}')
                if "OK" not in message:
                    break
            else :
                print(f'Se esperaba CONECTAR,DESCONECTAR,CONTINUAR,INTERRUMPIR, pero usted mando {buff}. REINTENTE!!!')


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python cliente.py <ServerIP> <ServerPort> <PuertoVLC>")
        sys.exit(1)

    ServerIP = sys.argv[1]
    ServerPort = int(sys.argv[2])
    PuertoVLC = int(sys.argv[3])
    print(f'Entra def cliente')
    Client(ServerIP, ServerPort, PuertoVLC)