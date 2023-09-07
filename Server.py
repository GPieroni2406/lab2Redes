import socket
from time import sleep
import threading
import sys

def Server(server):
    clientsList = []

    sktUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sktUDP.bind(('localhost', 65535))

    threading.Thread(target=sendData, args=(sktUDP, clientsList)).start()
    threading.Thread(target=addConections, args=(server,clientsList)).start()

    while True:
        sleep(1)

def addConections(server,clientsList):
     while True:
        try:
            client, addr = server.accept()
            threading.Thread(target=clientConection, args=(client, clientsList)).start()
        except socket.timeout:
            pass



def sendData(sktUDP,clientsList):
    try:
        datagram, (ip, port) = sktUDP.recvfrom(1024)
        for c in clientsList:
            if c[2]:
                sktUDP.sendto(datagram, (c[0], c[1]))
    except socket.timeout:
        pass




def clientConection(client, clientsList):
    clientIp, _ = client.getpeername()
    data = ""

    while True:
        buffer = client.recv(1024).decode()
        if not buffer:  # Si el buffer está vacío, el cliente se ha desconectado
            client.close()
            break

        data += buffer

        if "CONECTAR" in data:
            clientPort = int(data.split('<')[1].split('>')[0])
            if not any([c for c in clientsList if c[0] == clientIp]):
                clientsList.append((clientIp, clientPort, True))

        if "DESCONECTAR" in data:
            clientsList[:] = [c for c in clientsList if c[0] != clientIp]
            
            message = "OK\n"
            while message:
                sent = client.send(message.encode())
                message = message[sent:]

            client.close()
            break

        if "INTERRUMPIR" in data:
            for index, (ip, port, ready) in enumerate(clientsList):
                if ip == clientIp:
                    clientsList[index] = (ip, port, False)

        if "CONTINUAR" in data:
            for index, (ip, port, ready) in enumerate(clientsList):
                if ip == clientIp:
                    clientsList[index] = (ip, port, True)

        if any(word in data for word in ["CONTINUAR", "DESCONECTAR", "INTERRUMPIR", "CONECTAR"]):
            message = "OK\n"
            while message:
                sent = client.send(message.encode())
                message = message[sent:]


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Debe escribir : python server.py <ServerIP> <ServerPort>")
        sys.exit(1)

    ServerIP = sys.argv[1]
    ServerPort = int(sys.argv[2])
    master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    master.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    master.bind((ServerIP, ServerPort))
    server = master.listen(1)
    
    Server(server)