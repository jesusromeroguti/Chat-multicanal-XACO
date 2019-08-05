# coding=utf-8
import socket 
import select 
import sys 
import threading
import pickle

'''
La primera idea era hacer uso de diccionarios para realizar la gestion de los usuarios i los canales. 
Tuve problemas con ello asi que decidi utilizar clases. 

Clase Connection:
	- Instancia un objeto que:
		- Almacena el nombre del usuario y la direccion de la conexión al entrar al servidor.
		- Todas las conexiones las transformo en clases para asi tener la informacion del nombre 
	   		y la direccion de una manera mas sencilla.

Clase Canal:
	- Instancia un objeto que:
		- Guarda el nombre del canal creado.
		- Guarda la lista de los usuarios que contiene el canal.
		- Guarda la lista de las conexiones(direccion) de cada usuario del canal.
	- Tiene varios metodos para manejar los atributos del canal. 
		- Crear el canal default
		- Devolver el nombre del canal
		- Devolver la lista de usuarios
		- Devolver la lista de conexiones
		- Añadir un usuario al canal
		- Borrar un usuario del canal
NOTA: Algunos de estos metodos no los uso porque me daban ciertos problemas. A veces funcionaban bien y otras no
		como no he encontrado solucion preferia hacer las busquedas, añadir usuarios y borrarlos manualmente
		desde la funcion parse ya que al ser un funcion que esta en el mismo fichero que la clase y al no ser
		los atributos de la clase atributos privados puedo acceder sin problema desde otras funciones externas
		a la clase.
'''

class Connection:
	userName = ""
	connection = ""

	def __init__(self, userName, connection):
		self.userName = userName
		self.connection = connection


class Canal:
	nombre = ""
	usuarios = []
	conexiones = []

	def __init__(self, nombre, usuarios, conexiones):
		self.nombre = nombre
		self.usuarios = []
		self.conexiones = []
		self.usuarios.append(usuarios)
		self.conexiones.append(conexiones)
	
	def defaultCanal(self, nombre):
		self.nombre = nombre
		self.usuarios = []
		self.conexiones = []

	def nombreCanal(self):
		return self.nombre

	def addUsuari(self, userName, ip):
		usuarios = self.usuarios
		conexiones = self.conexiones
		usuarios.append(userName)
		conexiones.append(ip)
		self.usuarios = usuarios
		self.conexiones = conexiones
	
	def con(self):
		return self.conexiones
	
	def usuariosCanal(self):
		return self.usuarios
	
	def borrarUsuario(self, usuario, conexion):
		conexiones = self.conexiones
		conexiones.remove(conexion)
		self.conexiones = conexiones
		usuarios = self.usuarios
		usuarios.remove(usuario)
		self.usuarios = usuarios
	
# Funcion antigua que usaba para hacer el envio de los mensajes en la entrega 3 de la practica.
def broadcast(connection, message):
	for client in connection_list:
		if client.connection != connection:
			client.connection.send(message)


# Mensaje de help/ayuda para ver los comando disponibles
help_message = '''
Comandos disponibles:
CREA [nombre_canal] --> Crea un nuevo canal con el nombre introducido.
CANVIA [nombre_canal] --> Cambia al usuario del canal actual al introducido.
MOSTRA_USUARIS [nombre_canal] --> Muestra los usuarios del canal introducido.
MOSTRA_CANALS --> MUESTRA todos los canales.
PRIVAT [nombre_usuario][mensaje] -->Envia un mensaje privado al usuario introducido.
ELIMINA [nombre_canal] -->	Elimina el canal introducido.
MOSTRA_TOTS --> Muestra una lista de los canales y los usuarios que contiene cada canal.
				
** NOTA ** Si no introducies ningun comando envias el mensaje a todos los usuarios del canal actual
** CANAL PRINCIPAL ** Existe un canal principal y por defecto que no se puede borrar. Esta canal se llama [default]'''


''' 
Función que se llama desde cada Thread, es decir para cada usuario. 
Parametros ---> message: Mensaje enviado por el usuario. Puede ser un comando o un mensaje para el chat
				connection: Conexion del cliente proveniente del socket. El servidor guarda todas las conexiones de los clientes
				userName: Nombre del usuario para identificarlo
Funcionalidad: Esta función sirve para gestionar los mensajes enviados por los usuarios.
			   Si son mensajes los reenvia a todos los usuarios que esten en el mismo canal.
			   Si son comandos ejecuta la funcionalidad especifica de cada comando en concreto
'''
def parse(message, connection, userName):
	comando = message.split()[0]
	if comando == "help" or comando == "/h" or comando == "ayuda" or comando == "help()" or comando == "HELP":
		connection.connection.send(help_message)
		print("El usuario " + userName + " ha solicitado la funcion help") 
	# Comando que muestra todos los canales y los usuarios que tiene cada canal en el chat
	if comando == "MOSTRA_TOTS":
		# Hace un recorrido por la lista de canales y muestra por pantalla el nombre del canal.
		for canal in canales:
			connection.connection.send("Canal: " + canal.nombre + " ")
			connection.connection.send("Usuarios: ")
			# Hace un recorrido por la lista de usuarios de cada canal y los muestra por pantalla.
			for usuario in canal.usuarios:
				connection.connection.send(" " + usuario + " ")
		print("El usuario " + userName + " ha ejecutado el comando MOSTRA_TOTS")
	# Comando que muestra la lista de canales existentes en el chat
	if comando == "MOSTRA_CANALS":
		# Hace un recorrido por la lista de canales y los muestra por pantalla.
		for canal in canales:
			connection.connection.send(canal.nombre + " ")
	# Comando que crea un canal dado un nombre como parametro si no existe ya.	
	elif comando == "CREA":
		nombre_canal = message.split()[1]
		# Si en la lista de canales solo existe el canal por defecto
		# Creo un nuevo canal y lo añado a la lista de canales.
		if len(canales) == 1 and canales[0].nombre == "default":
			# Creo el canal.
			nuevo_canal = Canal(nombre_canal, userName, connection.connection)
			canales.append(nuevo_canal)
			# Borra el usuario y la conexion del canal default para que no esten duplicados
			for canal in canales:
				if canal.nombre == "default":
					canal.usuarios.remove(userName)
					canal.conexiones.remove(connection.connection)
			#Fin del borrar usuario y canal
			connection.connection.send("Canal creado correctamente")
			print("Se ha creado el canal --> " + nombre_canal)
		# Si ya hay mas de un canal en la lista de canales. Miramos si el canal que se quiere crear existe ya o no.
		else:
			# Comprovamos si existe el canal.
			b = False
			for canal in canales:
				if canal.nombre == nombre_canal:
					b = True
				else:
					b = False
			# No existe pues lo creamos. 
			if b == False:
				# Quitamos a los usuarios del canal actual para cambialos al nuevo canal.
				for canal in canales:
					if canal.nombre == "default":
						if userName in canal.usuarios:
							canal.usuarios.remove(userName)
							canal.conexiones.remove(connection.connection)
					for usuario in canal.usuarios:
						if usuario == userName:
							canal.usuarios.remove(userName)
							canal.conexiones.remove(connection.connection)
				# Creamos el nuevo canal.
				nuevo_canal = Canal(nombre_canal, userName, connection.connection)
				canales.append(nuevo_canal)
				connection.connection.send("Canal creado correctamente")
				print("Se ha creado el canal ---> " + nombre_canal)
			# Existe, mandamos un mensaje al usuari conforme si existe y no puedo crearlo pero se puede cambiar a el.
			else:
				connection.connection.send("El canal ya existe. Para entrar en el canal --> CANVIA [nombre canal]")
	# Comando que canvia al usuario del canal actual al canal dado como parametro.
	elif comando == "CANVIA":
		# Hace un recorrido a la lista de canales.
		# Cuando encontramos el usuario lo quitamos de la lista de usuarios  y de la lista de conexiones del canal donde este.
		for canal in canales:
			for usuario in canal.usuarios:
				if usuario == userName:
					canal.usuarios.remove(userName)
					canal.conexiones.remove(connection.connection)
			'''if userName in canal.usuarios:
				canal.usuarios.remove(usuario)
				canal.conexiones.remove(connection.connection)'''
		# Lo añadimos a la lista de usuarios y conexiones del canal al que se quiere cambiar.
		nombre_canal = message.split()[1]
		for canal in canales:
			if canal.nombre == nombre_canal:
				canal.usuarios.append(userName)
				canal.conexiones.append(connection.connection)
				connection.connection.send("Has cambiado de canal. Canal actual --> " + nombre_canal)
		print( 'El usuario ' + userName + ' se ha cambiado al canal --> ' + nombre_canal)
	# Comando que muestra los usuarios de un canal dado como parametro
	elif comando == "MOSTRA_USUARIS":
		nombre_canal = message.split()[1]
		# Recorremos la lista de canales en busca del canal pasado como argumento.
		for canal in canales:
			if nombre_canal == canal.nombre:
				# Si el canal esta vacio imprimimos mensaje por pantalla.
				if len(canal.usuarios) == 0:
					connection.connection.send("No hay usuarios en el canal")
				# Si no esta vacio recorremos la lista de usuarios del canal y los imprimimos por pantalla.
				else:
					for usuario in canal.usuarios:
						connection.connection.send(usuario + " ")
		print("El usuario " + userName + " ha ejecutado el comando --> MOSTRA_USUARIS para el canal " + nombre_canal)
	# Comando que envia un mensaje privado al usuario dado como parametro (este en el canal que este).
	elif comando == "PRIVAT":
		# Guardamos el usuario a quien quiere enviar el mensaje.
		usuari_privat = message.split()[1]
		# Guardamos el mensaje que se quiere enviar.
		mensaje = message.split()[2:]
		# Recorremos la lista de conexiones y buscamos el usuario. Una vez encontrado le enviamos el mensaje.
		for usuario in connection_list:
			if usuario.userName == usuari_privat:
				mesg = "<" + userName + "> "
				usuario.connection.send(mesg)
				for m in mensaje:
					usuario.connection.send(m + " ")
	# Comando que elimina un canal dado como parametro.
	elif comando == "ELIMINA":
		nombre_canal = message.split()[1]
		# Comprovamos si el canal existe
		b = False
		for canal in canales:
			if canal.nombre == nombre_canal:
				if nombre_canal == "default":
					b = False
				else:
					b = True
			else:
				b = False
		# No existe, pues le indicamos al usuario que lo puede crea si lo desea o que si es el canal por defecto no puede eliminarlo.
		if b == False:
			connection.connection.send("El canal no existe. Para crear el canal --> CREA [nombre canal]")
		if b == False and nombre_canal == "default":
			connection.connection.send("El canal por defecto [default] no puede ser eliminado")
		# Existe, pues lo eliminamos.
		else:
			for canal in canales:
				if canal.nombre == nombre_canal:
					canales.remove(canal)
					connection.connection.send("Canal eliminado correctamente")
		print("EL usuario " + userName + "ha ejecutado el comando ELIMINA")
	# Si no envias ningun comando el mensaje se envia a todos los usuarios del canal actual.
	else:
		# Hace un recorrido por la lista de canales, para cada canal hace un recorrido para todos los usuarios.
		for canal in canales:
			for usuario in canal.usuarios:
				#Si el usuario existe en el canal. Hago un recorrido por la lista de conexiones y envio el mensaje a todas.
				if usuario == userName:
					for conexion in canal.conexiones:
						if conexion != connection.connection:
							mesg = "<" + usuario + "> " + message
							conexion.send(mesg)

# Funcion que gestiona las conexiones. Un hilo para cada conexion/usuario
def clientthread(clientSocket, addr):
	# Mensaje de bienvenida
	clientSocket.send("Bienvenido al chat")
	# Recibimos el nombre del usuario para identificarlo.
	userName = clientSocket.recv(2048)
	# Una vez tenemos la conexion del socket del usuario creamos un objeto de la clase Conexion para poder guardar de manera simple
	# su nombre y su conexion.
	conex = Connection(userName, clientSocket)
	# La metemos en la lista de conexiones para poder gestionarla de manera sencilla.
	connection_list.append(conex)
	# Añadimos al usuario en el canal por defecto
	default.usuarios.append(userName)
	# Metemos la conexion del usuario en la lista de conexiones del canal por defecto.
	default.conexiones.append(clientSocket)
	print(default.usuarios)
	# Bucle que recibe mensajes del usuario y llama a la funcion parse para procesarlos.
	while True:
		mesg = clientSocket.recv(2048)
		parse(mesg, conex, userName)


# Funcion principal que recibe todas las conexiones y abre un hilo para cada una de ellas.
if __name__ == "__main__":
	# Definimos el socket TCP
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	host = ''
	# Puerto que utiliza la app
	port = 12000
	addr = (host, port)

	serverSocket.bind((host, port))
	# El servidor acepta hasta 10 conexiones.
	serverSocket.listen(10)
	# Lista de conexiones que tiene el server.
	connection_list = []
	# Lista de canales.
	canales = []

	# Creamos el canal por defecto.
	default = Canal("default", [], [])
	default.defaultCanal("default")
	# Lo añadimos a la lista de canales.
	canales.append(default)

	print("Servidor esperando conexiones...")

	while True:
		
		clientSocket, addr = serverSocket.accept()
		

		# Imprime cada vez que entra una nueva conexion su direccion IP y el puerto.
		print("Cliente con direccion IP: " + str(addr[0]) + " y Puerto: " + str(addr[1]) + " conectado")

		#Creamos un thread para cada nueva conexion
		client_thread = threading.Thread(target=clientthread, args=[clientSocket, addr])
		client_thread.start()
	
	clientSocket.close()
	serverSocket.close()