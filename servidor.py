# Importamos los módulos necesarios
import grpc
from concurrent import futures
# Importamos las librerías generadas por el compilador gRPC donde se encuentran las definiciones de las funciones y mensajes
import twitter_pb2
import twitter_pb2_grpc
import admindata
import os

registrados = admindata.Registrados()
# Añadimos 3 usuarios registrados para agilizar pruebas
registrados.registrar_usuario("ana", "ana")
registrados.registrar_usuario("paco", "paco")
registrados.registrar_usuario("juan", "juan")
# Añadimos algún usuario siguiendo a otro para pruebas
# Ana sigue a paco y juan, debe ver sus mensajes
registrados.seguir_usuario("ana", "paco")
registrados.seguir_usuario("ana", "juan")
# Paco sigue a juan, debe ver sus mensajes
registrados.seguir_usuario("juan", "paco")
logueados = admindata.Logueados()


# Implementar las funciones definidas en twitter.proto.
# Estas funciones son métodos de la clase TwitterServicer, que hereda de la clase generada por el compilador gRPC
# El argumento context no es necesario usarlo en nuestra práctica, pero es necesario incluirlo en la firma de la función
# El argumento request es el mensaje que envía el cliente cuando invoca la función remota, del formato definido en el archivo .proto
# Cada función remota debe retornar un mensaje de respuesta, que es el que recibe el cliente, del formato definido en el archivo .proto
# Una vez un usuario está logueado, el resto de acciones requieren que se compruebe en primer lugar el id session
class TwitterService(twitter_pb2_grpc.TwitterServicer):

    # Registrar un usuario nuevo si no existe el nombre de usuario ya registrado
    def Registrar(self, request, context):
        # Verificar si el usuario ya está registrado
        if registrados.existe_usuario(request.user):
            return twitter_pb2.RegistrarReply(error=1)  # Error 1: Usuario ya existe
        else:
            registrados.registrar_usuario(request.user, request.password)
            return twitter_pb2.RegistrarReply(error=0)  # Registro exitoso

    # Iniciar sesión de un usuario si el nombre de usuario y contraseña son correctos
    def Login(self, request, context):
        # Verificar si el usuario está registrado
        if not registrados.existe_usuario(request.user):
            return twitter_pb2.LoginReply(error=1, session=0)

        # Verificar la contraseña del usuario
        if not registrados.comprobar_credenciales(request.user, request.password):
            return twitter_pb2.LoginReply(error=2, session=0)
        # Verificar si el usuario ya está logueado. Regenerar session si ya está logueado. Sino loguear usuario
        if logueados.comprobar_logueado(request.user):
            login = logueados.regenerar_sesion(request.user)
            return twitter_pb2.LoginReply(error=0, session=login)
        else:
            login = logueados.loguear_usuario(request.user)
            return twitter_pb2.LoginReply(error=0, session=login)
        # Error 1: Usuario no existe
        # Verificar la contraseña del usuario
        # Error 2: Contraseña incorrecta
        # Verificar si el usuario ya está logueado. Regenerar session si ya está logueado. Sino loguear usuario

    # Cerrar sesión de un usuario
    def Logout(self, request, context):
        # Verificar que la session es correcta
        if logueados.comprobar_sesion(request.user, request.session):
            logueados.cerrar_sesion(request.user)
        return twitter_pb2.Void()

    # Devolver una lista de los usuarios registrados
    def VerUsuarios(self, request, context):
        # Verificar si el usuario está conectado y la session es correcta
        if logueados.comprobar_sesion(request.user, request.session):
            lista = registrados.ver_usuarios(request.user)
        return twitter_pb2.VerUsuariosReply(user=lista)

    # Añadir un nuevo usuario a la lista de suguiendo de un usuario
    def Seguir(self, request, context):
        # Verificar si el usuario está conectado y la session es correcta
        if logueados.comprobar_sesion(request.user, request.session):
            # Verificar si el usuario a seguir existe
            if not registrados.existe_usuario(request.user_to_follow):
                return twitter_pb2.SeguirReply(error=1)
            lista = registrados.ver_siguiendo(request.user).split(';')
            if request.user_to_follow in lista:
                return twitter_pb2.SeguirReply(error=2)
            else:
                registrados.seguir_usuario(request.user, request.user_to_follow)
                return twitter_pb2.SeguirReply(error=0)
        # Error 1: Usuario a seguir no existe

        # Verificar si el usuario ya está siguiendo al usuario a seguir
        # Error 2: Usuario ya está siguiendo al usuario a seguir

        # Añadir el usuario a la lista de siguiendo

    # Quitar un usuario de la lista siguiendo de un usuario
    def DejarSeguir(self, request, context):
        # Verificar si el usuario está conectado y la session es correcta

        if logueados.comprobar_sesion(request.user, request.session):
            lista = registrados.ver_siguiendo(request.user)
            lista = lista.split(';')
            if request.user_to_follow in lista:
                registrados.dejar_seguir_usuario(request.user, request.user_to_follow)
                return twitter_pb2.SeguirReply(error=0)
            return twitter_pb2.SeguirReply(error=2)

    # Devolver una lista de usuarios que está siguiendo el usuario request.user
    def VerSeguidos(self, request, context):
        # Verificar si el usuario está conectado y la session es correcta
        if logueados.comprobar_sesion(request.user, request.session):
            lista = registrados.ver_siguiendo(request.user).split(';')
        return twitter_pb2.VerSeguidosReply(user=lista)

    # Registrar un tuit en la lista de mensajes pendientes de enviar en función de los seguidores del usuario
    def EnviarTuit(self, request, context):
        # Verificar si el usuario está conectado y la session es correcta
        if logueados.comprobar_sesion(request.user, request.session):
            seguidores = registrados.ver_seguidores(request.user)
            logueados.registrar_mensaje(request.user, request.tuit.mensaje, seguidores)
        # Debes averiguar la lista de seguidores de request.user
        # Posteriormente registrar el mensaje pasando la lista de seguidores
        return twitter_pb2.Void()

    # Recibir tuits pendientes
    def RecibirTuits(self, request, context):
        # Verificar si el usuario está conectado y la session es correcta
        if logueados.comprobar_sesion(request.user, request.session):
            mensajes = logueados.recibir_mensajes(request.user)
            tuits = []
            if mensajes is not None:
                for mensaje in mensajes:
                    tuits.append(twitter_pb2.Tuit(user=mensaje[0], mensaje=mensaje[1]))
            return twitter_pb2.RecibirTuitsReply(tuit=tuits)
        else:
            return twitter_pb2.RecibirTuitsReply(tuit=[])
        # Leer la lista de listas con los mensajes pendientes construir el Reply como lista de twitter_pb2.Tuit


# Función para iniciar el servidor
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    twitter_pb2_grpc.add_TwitterServicer_to_server(TwitterService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Servidor iniciado")
    while True:
        print("""Menu:
              1. Mostrar usuarios registrados
              2. Mostrar usuarios conectados
              3. Mostrar mensajes pendientes de enviar
              4: Salir
              Este menú está siempre disponible aunque se muestren mensajes de log""")
        opcion = input("")
        match opcion:
            case "1":
                print("*** USUARIOS REGISTRADOS ***")
                registrados.mostrar_registrados()
            case "2":
                print("*** USUARIOS CONECTADOS ***")
                logueados.mostrar_logueados()
            case "3":
                print("*** MENSAJES PENDIENTES DE ENVIAR ***")
                logueados.mostrar_mensajes()
            case "4":
                server.stop(0)
                os.system("clear")
                break
            case _:
                print("Opción no válida")


if __name__ == '__main__':
    try:
        serve()
    except KeyboardInterrupt:
        print("Servidor detenido")
