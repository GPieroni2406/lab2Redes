import socket
from time import sleep
import threading
import sys
import logging
import re

def Server(server):
    clientsList = []

    sktUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sktUDP.bind(('127.0.0.1', 65534))

    print(f'Se creo el socket UDP')

    threading.Thread(target=sendData, args=(sktUDP, clientsList)).start()
    threading.Thread(target=addConections, args=(server,clientsList)).start()

    while True:
        sleep(1)

def addConections(server,clientsList):
     print(f'Aceptando clientes')
     while True:
        try:
            client, addr = server.accept()
            print(f'Se acepta el cliente {addr}')
            threading.Thread(target=clientConection, args=(client, clientsList)).start()
        except socket.timeout:
            pass



def sendData(sktUDP,clientsList):
    print(f'Recibiendo datagramas por UDP')
    try:
        datagram, (ip, port) = sktUDP.recvfrom(65000)
        print(f'El datagrama transmitido es {datagram}')
        print(f'Se muestra la lista clientlist {clientsList}')
        print(f'Enviando datagramas a todos los clientes por UDP')
        for c in clientsList:
            if c[2]:
                sktUDP.sendto(datagram, (c[0], c[1]))
    except socket.timeout:
        print(f'El socket sufrió timeout al recibir el datagrama')
        pass
    except socket.error as e:
        print(f'El socket sufrió un error de tipo {e} al recibir el datagrama')




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
            print(f'Agregando cliente a los conectados')
            patron = r'\d+'
            resultado = re.search(patron, data)
            if resultado:
                numero = resultado.group()
            clientPort = int(numero)
            print(f'El puerto elegido es {numero}')
            if not any([c for c in clientsList if c[0] == clientIp]):
                clientsList.append((clientIp, clientPort, True))
            print(f'La lista actual de conectados es {clientsList}')

        if "DESCONECTAR" in data:
            print(f'Desconectando cliente')
            clientsList[:] = [c for c in clientsList if c[0] != clientIp]
            
            message = "OK\n"
            while message:
                sent = client.send(message.encode())
                message = message[sent:]

            client.close()
            break

        if "INTERRUMPIR" in data:
            print(f'Interrumpiendo conexion del cliente')
            for index, (ip, port, ready) in enumerate(clientsList):
                if ip == clientIp:
                    clientsList[index] = (ip, port, False)

        if "CONTINUAR" in data:
            print(f'Reanudando conexion del cliente')
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
        print("Debe escribir : python Server.py <ServerIP> <ServerPort>")
        sys.exit(1)

    ServerIP = sys.argv[1]
    ServerPort = int(sys.argv[2])
    master = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    master.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    master.bind((ServerIP, ServerPort))
    master.listen(1)
    print(f'Se creo el socket TCP, bindeado en : {ServerIP} y {ServerPort}')
    Server(master)