import grpc
import twitter_pb2
import twitter_pb2_grpc
import os


# Menu de opciones inicial para registrarse y loguearse
def menu_inicial():
    while True:
        os.system("clear")
        print("""
                 ____        _            
                |  _ \ _   _| |_ ___ _ __ 
                | |_) | | | | __/ _ \ '__|
                |  __/| |_| | ||  __/ |   
                |_|    \__, |\__\___|_|   
                       |___/              
                """)
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("3. Salir\n")
        opcion = int(input("Ingrese opción: "))
        print('\n')
        if opcion < 1 or opcion > 3:
            print("Opción inválida")
        else:
            return opcion


# Menú una vez estás logueado
def menu_logueado():
    while True:
        os.system("clear")
        print("""
         ____        _            
        |  _ \ _   _| |_ ___ _ __ 
        | |_) | | | | __/ _ \ '__|
        |  __/| |_| | ||  __/ |   
        |_|    \__, |\__\___|_|   
               |___/              
        """)
        print("1. Ver usuarios registrados")
        print("2. Seguir a un usuario")
        print("3. Dejar de seguir a un usuario")
        print("4. Ver usuarios seguidos")
        print("5. Enviar tuit")
        print("6. Recibir tuits pendientes")
        print("7. Salir\n")
        opcion = int(input("Ingrese opción: "))
        print('\n')
        if opcion < 1 or opcion > 7:
            print("Opción inválida")
        else:
            return opcion


# Implementar las funciones del cliente por separado
# Cada función recibe el stub, solicita al usuario los datos necesarios, invoca la función remota y muestra el resultado
def registrar_usuario(stub):
    # Preguntar el usuario y la contraseña
    usuario = input("Usuario: ")
    passw = input("Pass: ")

    # Llamar a la función remota Registrar
    request = twitter_pb2.RegistrarRequest(user=usuario, password=passw)
    try:
        respuesta = stub.Registrar(request)
        if respuesta.error == 1:
            print("Error: El usuario ya existe\n")
        else:
            print("Registro exitoso\n")
    except grpc.RpcError as e:
        print(f"Error al registrar usuario: {e}\n")
    input("Presione una tecla para continuar")


def iniciar_sesion(stub):
    # Preguntar el usuario y la contraseña
    usuario = input("Usuario: ")
    passw = input("Contraseña: ")
    # Llamar a la función remota Login
    request = twitter_pb2.LoginRequest(user=usuario, password=passw)
    try:
        respuesta = stub.Login(request)
        if respuesta.error == 1:
            print("Error: Usuario incorrecto\n")
            return None, None
        elif respuesta.error == 2:
            print("Error: Contraseña incorrecta\n")
            return None, None
        else:
            print("Inicio de sesión exitoso\n")
            return usuario, respuesta.session
    except grpc.RpcError as e:
        print(f"Error al iniciar sesión: {e}\n")
        return None, None
    finally:
        input("Presione una tecla para continuar")
    # Debe mostrar un mensaje de error si el usuario no existe o la contraseña es incorrecta


# El resto de funciones deben recibir como parámetros el stub, user y session
def cerrar_sesion(stub, user, session):
    # Llamar a la función remota Logout
    logout = twitter_pb2.LogoutRequest(user=user, session=session)
    respuesta = stub.Logout(logout)
    os.system("clear")


def ver_usuarios_registrados(stub, user, session):
    # Imprimitr los usuarios registrados menos el propio usuario
    listusers = twitter_pb2.VerUsuariosRequest(user=user, session=session)
    try:
        respuesta = stub.VerUsuarios(listusers)
        for usuario in respuesta.user:
            print(usuario)
    except grpc.RpcError as e:
        print(f"Error al ver usuarios registrados: {e}\n")
    finally:
        input("Presione una tecla para continuar")


def seguir_usuario(stub, user, session):
    # Preguntar el usuario a seguir
    seguir = input("¿Qué usuario desea seguir?: ")
    print('\n')
    # Llamar a la función Seguir con el usuario introducido por parámetro
    request = twitter_pb2.SeguirRequest(user=user, session=session, user_to_follow=seguir)
    try:
        respuesta = stub.Seguir(request)
        if respuesta.error == 1:
            print("Error: El usuario no existe\n")
        elif respuesta.error == 2:
            print("Error: Ya sigues a ese usuario\n")
        else:
            print(f'Ahora sigues a {seguir}\n')
    except grpc.RpcError as e:
        print(f"Error al seguir usuario: {e}\n")
    finally:
        input("Presione una tecla para continuar")
    # Mostrar los mensajes de error según el reply


def dejar_seguir_usuario(stub, user, session):
    # Preguntar el usuario a dejar de seguir
    user_to_follow = input("¿Qué usuario desea dejar de seguir?: ")
    # Llamar a la función DejarSeguir con el usuario introducido por parámetro
    request = twitter_pb2.SeguirRequest(user=user, session=session, user_to_follow=user_to_follow)
    # Mostrar los mensajes de error según el reply
    try:
        respuesta = stub.DejarSeguir(request)
        if respuesta.error == 2:
            print("Error: No sigues a ese usuario\n")
        elif respuesta.error == 0:
            print(f"Has dejado de seguir a {user_to_follow}\n")
    except grpc.RpcError as e:
        print(f"Error al dejar de seguir usuario: {e}\n")
    finally:
        input("Presione una tecla para continuar")


def ver_usuarios_seguidos(stub, user, session):
    # Mostrar los usuarios seguidos por el usuario
    request = twitter_pb2.VerSeguidosRequest(user=user, session=session)
    try:
        respuesta = stub.VerSeguidos(request)
        for usuario in respuesta.user:
            print(usuario)
        print('\n')
    except grpc.RpcError as e:
        print(f"Error al ver usuarios seguidos: {e}\n")
    finally:
        input("Presione una tecla para continuar")


def enviar_tuit(stub, user, session):
    # Preguntar el mensaje del tuit
    # Enviar el tuit usando el procedimiento remoto
    tuit_text = input("Mensaje del tuit: ")
    tuit = twitter_pb2.Tuit(user=user, mensaje=tuit_text)
    request = twitter_pb2.EnviarTuitRequest(user=user, session=session, tuit=tuit)
    try:
        stub.EnviarTuit(request)
        print('\n')
        print("Tuit enviado")
    except grpc.RpcError as e:
        print(f"Error al enviar tuit: {e}\n")
    finally:
        input("Presione una tecla para continuar")


def recibir_tuits(stub, user, session):
    # Recibir los tuits pendientes invocando al procedimiento remoto
    request = twitter_pb2.RecibirTuitsRequest(user=user, session=session)
    try:
        respuesta = stub.RecibirTuits(request=request)
        for tuit in respuesta.tuit:
            print(f"{tuit.user}: {tuit.mensaje}")
        if not respuesta.tuit:
            print("No hay tuits pendientes\n")
    except grpc.RpcError as e:
        print(f"Error al recibir tuits: {e}\n")
    finally:
        input("Presione una tecla para continuar")


# Función principal. Abre el canal y ejecuta las opciones del menú hasta que se elija la opción de salir.
def main():
    os.system("clear")
    print("""
+-------------------------------+
|                               |
|        PyTer                  |
|                               |
|  Creado por Víctor Jimenez    |
|  para el CE_Python            |
|                               |
+-------------------------------+
    """)
    input("Presione una tecla para continuar")
    # Iniciar un canal grpc
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            # Crear un stub
            stub = twitter_pb2_grpc.TwitterStub(channel)
            user = None
            session = None

            # Mostrar el menú inicial
            while True:
                opcion = menu_inicial()
                if opcion == 1:
                    registrar_usuario(stub)
                elif opcion == 2:
                    user, session = iniciar_sesion(stub)
                    if session is not None:
                        break
                elif opcion == 3:
                    return None

            # Una vez logueado, mostrar el menú de opciones
            while True:
                opcion = menu_logueado()
                if opcion == 1:
                    ver_usuarios_registrados(stub, user, session)
                elif opcion == 2:
                    seguir_usuario(stub, user, session)
                elif opcion == 3:
                    dejar_seguir_usuario(stub, user, session)
                elif opcion == 4:
                    ver_usuarios_seguidos(stub, user, session)
                elif opcion == 5:
                    enviar_tuit(stub, user, session)
                elif opcion == 6:
                    recibir_tuits(stub, user, session)
                elif opcion == 7:
                    cerrar_sesion(stub, user, session)
                    return None
    except grpc.RpcError as e:
        print(f"Error al conectar con el servidor: {e}")


if __name__ == '__main__':
    main()
