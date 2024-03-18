from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, nome, cognome, password, isLocatore, isProfessionista, dataNascita, imgProfilo):
        self.id = id
        self.email = email
        self.nome = nome
        self.cognome = cognome
        self.password = password
        self.isLocatore = isLocatore
        self.isProfessionista = isProfessionista
        self.dataNascita = dataNascita
        self.imgProfilo = imgProfilo