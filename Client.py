import socket
import threading
import sys
import re

def Client(serverIP, serverPort, vlcPort):
    master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #master.bind(('127.0.0.1', 0))
    print(f'bindea sockettcp')
    sktUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        master.connect((serverIP, serverPort))
        print(f'se conecta al servidor prendido')
    except socket.error as e:
        print(f'no consigue conectarse, por {e}' )
        master.close()
        return
    threading.Thread(target=consoleData, args=(sktUDP,vlcPort,master)).start()

def consoleData(sktUDP,vlcPort,master):
        buff = ""
        print(f'Se abre hilo de conexión TCP con servidor')
        while True:
            data = input()
            if "CONECTAR" in data:
                patron = r'\d+'
                resultado = re.search(patron, data)
                if resultado:
                    numero = resultado.group()
                clientPort = int(numero)
                sktUDP.bind(('127.0.0.1', clientPort))
                threading.Thread(target=transmissionVLC, args=(sktUDP, vlcPort)).start()

            if "DESCONECTAR" in data:
                sktUDP.close()
                break
            
            while data:
                try:
                    sent = master.send(data.encode())
                    data = data[sent:]
                except socket.error as e:
                    master.close()
                    return

            if any(word in data for word in ["DESCONECTAR", "CONECTAR", "INTERRUMPIR", "CONTINUAR"]):
                try:
                    data = master.recv(1024).decode()
                    buff += data
                except socket.error as e:
                    master.close()
                    return
                
                if "OK" not in data:
                    break


def transmissionVLC(sktUDP, vlcPort):
    while True:
        try:
            data, addr = sktUDP.recvfrom(65000)
            sktUDP.sendto(data, ('127.0.0.1', vlcPort))
            print(f'El datagrama recibido es {data}')
        except socket.error as e:
            sktUDP.close()
            break
        
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python cliente.py <ServerIP> <ServerPort> <PuertoVLC>")
        sys.exit(1)

    ServerIP = sys.argv[1]
    ServerPort = int(sys.argv[2])
    PuertoVLC = int(sys.argv[3])
    print(f'Entra def cliente')
    Client(ServerIP, ServerPort, PuertoVLC)