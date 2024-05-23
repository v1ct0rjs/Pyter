import pandas as pd
from random import randint


# Definir una clase que contenga los usuarios registrados. La estructura para almacenarlos es un dataframe
class Registrados:
    # Constructor de la clase Registrados con atributo usuarios_registrados
    def __init__(self):
        self.registrados = pd.DataFrame(columns=["user", "password", "siguiendo"])

    # Método para comprobar si un usuario ya está registrado
    def existe_usuario(self, user):
        return self.registrados.query(f"user == '{user}'").shape[0] > 0

    # Método para registrar un usuario
    def registrar_usuario(self, user, password):
        # Crea una serie con los nuevos valores para la fila
        nueva_fila = pd.Series({'user': user, 'password': password, 'siguiendo': ""})
        # Añadir al dataframe usando loc y el último índice
        self.registrados.loc[len(self.registrados)] = nueva_fila

    # Método para comprobar la contraseña de un usuario existente. Si no existe el user retorna None
    def comprobar_credenciales(self, user, password):
        query = self.registrados.query(f"user == '{user}'")
        if query.shape[0] == 0:
            return None
        else:
            return query['password'].values[0] == password

    # Método para mostrar por pantalla los usuarios registrados
    def mostrar_registrados(self):
        print(self.registrados)

    # Método para añadir un usuario a la lista de siguiendo, separados por ';'
    def seguir_usuario(self, user, usuario_seguido):
        antiguos_siguiendo = self.registrados.loc[self.registrados["user"] == user, "siguiendo"].values[0]
        if antiguos_siguiendo == "":
            nuevos_siguiendo = usuario_seguido
        else:
            nuevos_siguiendo = antiguos_siguiendo + ";" + usuario_seguido
        self.registrados.loc[self.registrados["user"] == user, "siguiendo"] = nuevos_siguiendo

    # Método para dejar de seguir a un usuario.
    def dejar_seguir_usuario(self, user, usuario_seguido):
        # TODO
        listadf = self.registrados.loc[self.registrados["user"] == user, "siguiendo"].values[0]
        listadf = listadf.split(';')
        nlista = []
        cadena = None
        for usuario in listadf:
            if usuario != usuario_seguido:
                nlista.append(usuario)
        for nusuario in nlista:
            cadena = ';'.join(nlista)
        self.registrados.loc[self.registrados["user"] == user, "siguiendo"] = cadena
        # Quitar de usuarios seguidos al usuario_seguido

    # Método que retorna el contenido de la columna siguiendo para un user dado
    def ver_siguiendo(self, user):
        return self.registrados.query(f"user == '{user}'")["siguiendo"].values[0]

    # Método que devuelve una lista de los seguidores del usuario user
    def ver_seguidores(self, user):
        seguidores = []
        for index, row in self.registrados.iterrows():
            if user in row["siguiendo"].split(";"):
                seguidores.append(row["user"])
        return seguidores

    # Método que devuelve una lista de usuarios registrados menos el user pasado como argumento
    def ver_usuarios(self, user):
        return self.registrados[self.registrados["user"] != user]["user"].values.tolist()


# Definir una clase que contenga los usuarios logueados y los mensajes recibidos y pendientes de enviar
class Logueados:
    # Constructor de la clase Logueados con atributo usuarios_logueados
    def __init__(self):
        # Usuarios conectados
        self.logueados = pd.DataFrame(columns=["user", "session"])
        # Mensajes pendientes de enviar
        self.mensajes = pd.DataFrame(columns=["destinatario", "user", "mensaje"])

    # Método para comprobar si un usuario ya está logueado
    def comprobar_logueado(self, user):
        return self.logueados.query(f"user == '{user}'").shape[0] > 0

    # Método para loguear un usuario. Retorna la sesión generada
    def loguear_usuario(self, user):
        # Genera número aleatorio de 4 cifras
        session = randint(1000, 9999)
        # Generar una serie con la nueva fila
        nueva_fila = pd.Series({'user': user, 'session': session})
        # Añadir al dataframe usando loc y el último índice
        self.logueados.loc[len(self.logueados)] = nueva_fila
        return session

    # Método para cerrar sesión de un usuario
    def cerrar_sesion(self, user):
        self.logueados = self.logueados[self.logueados["user"] != user]

    # Método para obtener la sesión de un usuario
    def obtener_sesion(self, user):
        return self.logueados.query(f"user == '{user}'")["session"].values[0]

    # Método para comprobar que la sesión de un usuario es correcta. Si usuario no existe retorna None
    def comprobar_sesion(self, user, session):
        session_query = self.logueados.query(f"user == '{user}'")["session"].values
        if session_query.shape[0] == 0:
            return None
        else:
            return session_query == session

    # Generar un nuevo id de sesión y cambiarlo en el dataframe
    def regenerar_sesion(self, user):
        session = randint(1000, 9999)
        self.logueados.loc[self.logueados["user"] == user, "session"] = session
        return session

    # Método para mostrar por pantalla los usuarios logueados
    def mostrar_logueados(self):
        print(self.logueados)

    # Método que registra un mensaje según la lista de destinatarios recibida como argumento 
    def registrar_mensaje(self, user, mensaje, destinatarios):
        for destino in destinatarios:
            nueva_fila = pd.Series({'destinatario': destino, 'user': user, 'mensaje': mensaje})
            self.mensajes.loc[len(self.mensajes)] = nueva_fila

    # Método que retorna los mensajes pendientes de enviar a un usuario y los borra del dataframe
    # Los retorna en forma de lista de listas [[escritor, mensaje], [escritor, mensaje], ...]
    def recibir_mensajes(self, user):
        # TODO
        mensajes = self.mensajes.query(f"destinatario == '{user}'")
        self.mensajes = self.mensajes[self.mensajes["destinatario"] != user]
        if mensajes.shape[0] > 0:
            return mensajes[["user", "mensaje"]].values.tolist()
        return None

    # Imprimir mensajes pendientes de enviar
    def mostrar_mensajes(self):
        print(self.mensajes)


if __name__ == '__main__':
    # pruebas unitarias clase RegistradosF
    registrados = Registrados()
    # Añadimos 2 usuarios para pruebas
    registrados.registrar_usuario("usuario1", "password1")
    registrados.registrar_usuario("usuario2", "password2")
    registrados.registrar_usuario("usuario3", "password3")
    print("mostrando usuarios registrados. Debe haber 3")
    registrados.mostrar_registrados()

    assert registrados.existe_usuario("usuario1") == True
    assert registrados.existe_usuario("pepito") == False

    assert registrados.comprobar_credenciales("usuario1", "password1") == True
    assert registrados.comprobar_credenciales("usuario1", "password2") == False
    assert registrados.comprobar_credenciales("pepito", "password1") == None

    registrados.seguir_usuario(user="usuario1", usuario_seguido="usuario2")
    registrados.seguir_usuario(user="usuario1", usuario_seguido="usuario3")
    registrados.seguir_usuario(user="usuario2", usuario_seguido="usuario3")

    assert registrados.ver_siguiendo("usuario1") == "usuario2;usuario3"
    assert registrados.ver_siguiendo("usuario2") == "usuario3"
    assert registrados.ver_siguiendo("usuario3") == ""

    assert registrados.ver_seguidores("usuario1") == []
    assert registrados.ver_seguidores("usuario2") == ["usuario1"]
    assert registrados.ver_seguidores("usuario3") == ["usuario1", "usuario2"]

    resultado = registrados.ver_usuarios("usuario1")
    correcto = ["usuario2", "usuario3"]
    for res, corr in zip(resultado, correcto):
        assert res == corr

    resultado = registrados.ver_usuarios("usuario2")
    correcto = ["usuario1", "usuario3"]
    for res, corr in zip(resultado, correcto):
        assert res == corr

        # pruebas unitarias clase Logueados
    logueados = Logueados()
    assert logueados.comprobar_logueado("usuario1") == False
    session = logueados.loguear_usuario("usuario1")
    assert logueados.comprobar_logueado("usuario1") == True
    assert logueados.obtener_sesion("usuario1") == session
    assert logueados.comprobar_sesion("usuario1", session) == True
    assert logueados.comprobar_sesion("usuario1", session + 1) == False
    assert logueados.comprobar_sesion("usuario2", session) == None
    print("mostrando usuarios logueados. Deber haber usuario1")
    logueados.mostrar_logueados()
    logueados.cerrar_sesion("usuario1")
    print("mostrando usuarios logueados. Deber haber 0")
    logueados.mostrar_logueados()
    assert logueados.comprobar_logueado("usuario1") == False
    session = logueados.loguear_usuario("usuario1")
    session = logueados.regenerar_sesion("usuario1")
    assert logueados.comprobar_sesion("usuario1", session) == True
    session2 = logueados.loguear_usuario("usuario2")
    session3 = logueados.loguear_usuario("usuario3")
    seguidores1 = registrados.ver_seguidores("usuario1")
    print("seguidores de usuario1", seguidores1)
    seguidores2 = registrados.ver_seguidores("usuario2")
    print("seguidores de usuario2", seguidores2)
    seguidores3 = registrados.ver_seguidores("usuario3")
    print("seguidores de usuario3", seguidores3)
    logueados.registrar_mensaje("usuario1", "mensaje1", seguidores1)
    logueados.registrar_mensaje("usuario2", "mensaje2", seguidores2)
    logueados.registrar_mensaje("usuario3", "mensaje3", seguidores3)
    logueados.mostrar_mensajes()
    print("Mensajes para user1\n", logueados.recibir_mensajes("usuario1"))
    print("Mensajes para user2\n", logueados.recibir_mensajes("usuario2"))
    print("Mensajes para user3\n", logueados.recibir_mensajes("usuario3"))
