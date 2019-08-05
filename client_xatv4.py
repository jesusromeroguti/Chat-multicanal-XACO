import sys
import socket
import threading
import pickle

#Funcion que envia los mensajes
#El usuario introduce el mensaje por teclado y se envia por el socket
def send():
        while True:
                mesg = raw_input()
                clientSocket.send(mesg)
                
#Funcion que recibe los mensajes y los muestra por pantalla al usuario
def receive():
        while True:
                data = clientSocket.recv(1024)
                #data = pickle.loads(data)
                print('\n' + str(data))

if __name__ == "__main__":
        #Creamos el socket
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #Datos de conexion
        host = '192.168.1.35' #IP del servidor al que te quieras conectar
        port = 12000

        #Realizamos la conexion con los datos mediante el socket
        clientSocket.connect((host, port))
        print("Conectando con el host...")
        user_name = raw_input("Introduce tu nombre de usuario: ")
        clientSocket.send(user_name)

        '''Creamos los hilos para realizar la conexion full-duplex
           Para realizar dicha conexion necesitamos dos threads.
           - Thread que envie los datos
           - Thread que reciba los datos
           De esta manera podremos enviar y recibir datos simultaneamente'''

        thread_send = threading.Thread(target = send)
        thread_send.start()

        thread_recv = threading.Thread(target = receive)
        thread_recv.start()

        #clientSocket.close()
