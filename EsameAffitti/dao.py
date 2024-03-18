import sqlite3

#operazioni su UTENTI
def get_user_by_email(user_email):
    conn = sqlite3.connect('db/dbAffitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM UTENTI WHERE email=?'
    cursor.execute(sql, (user_email, ))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result

def get_user_by_id(user_id):
    conn = sqlite3.connect('db/dbAffitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM UTENTI WHERE id_utente=?'
    cursor.execute(sql, (user_id, ))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result

def isLocatore_by_id(user_id):
    conn = sqlite3.connect('db/dbAffitti.db')
    cursor = conn.cursor()

    sql = 'SELECT isLocatore FROM UTENTI WHERE id_utente=?'
    cursor.execute(sql, (user_id, ))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result

def crea_utente(nuovo_utente):
    connection = sqlite3.connect('db/dbAffitti.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    query = 'INSERT INTO UTENTI(email,nome,cognome,password,isLocatore,isProfessionista,dataNascita,imgProfilo) VALUES (?,?,?,?,?,?,?,?)'
    success = False

    try:
        cursor.execute(query, (nuovo_utente['email'],nuovo_utente['nome'], nuovo_utente['cognome'],nuovo_utente['password'],nuovo_utente['isLocatore'],nuovo_utente['isProfessionista'],nuovo_utente['dataNascita'],nuovo_utente['imgProfilo']))
        connection.commit()
        success = True
    except Exception as e:
        print('Error', str(e))
        connection.rollback()

    cursor.close()
    connection.close()

    return success

def modifica_utente(update):
    connection = sqlite3.connect('db/dbAffitti.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    query = 'UPDATE UTENTI SET email=?, password=?, nome=?, cognome=?, dataNascita=?, imgProfilo=? WHERE id_utente=?'
    success = False

    try:
        cursor.execute(query, (update['email'], update['password'], update['nome'], update['cognome'], update['dataNascita'], update['imgProfilo'], update['id_utente']))
        connection.commit()
        success = True
    except Exception as e:
        print('Error', str(e))
        connection.rollback()

    cursor.close()
    connection.close()

    return success

#operazioni su ANNUNCI
def get_annunci_prezzo_decrescente():
    conn = sqlite3.connect('db/dbAffitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM ANNUNCI WHERE isDisponibile=? ORDER BY prezzo DESC'
    cursor.execute(sql, (1, ))
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result

def get_annunci_locali_crescente():
    conn = sqlite3.connect('db/dbAffitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM ANNUNCI WHERE isDisponibile=? ORDER BY numLocali'
    cursor.execute(sql, (1, ))
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result

def get_annunci_locatore(id_locatore):
    conn = sqlite3.connect('db/dbAffitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM ANNUNCI WHERE id_locatore=?'
    cursor.execute(sql, (id_locatore, ))
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result

def get_annuncio_by_id(id_annuncio):
    conn = sqlite3.connect('db/dbAffitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM ANNUNCI WHERE id_annuncio=?'
    cursor.execute(sql, (id_annuncio, ))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result

def crea_annuncio(nuovo_annuncio):
    connection = sqlite3.connect('db/dbAffitti.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    query = 'INSERT INTO ANNUNCI(titolo, indirizzo, tipoCasa, numLocali, descrizione, prezzo, isArredata, id_locatore, isDisponibile, url1, url2, url3, url4, url5) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    success = False

    try:
        cursor.execute(query, (nuovo_annuncio['titolo'], nuovo_annuncio['indirizzo'], nuovo_annuncio['tipoCasa'], nuovo_annuncio['numLocali'], nuovo_annuncio['descrizione'], nuovo_annuncio['prezzo'], nuovo_annuncio['isArredata'], nuovo_annuncio['id_locatore'], nuovo_annuncio['isDisponibile'], nuovo_annuncio['url1'], nuovo_annuncio['url2'], nuovo_annuncio['url3'], nuovo_annuncio['url4'], nuovo_annuncio['url5']))
        connection.commit()
        success = True
    except Exception as e:
        print('Error', str(e))
        connection.rollback()

    cursor.close()
    connection.close()

    return success

def modifica_annuncio(annuncio):
    connection = sqlite3.connect('db/dbAffitti.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    query = 'UPDATE ANNUNCI SET titolo=?, tipoCasa=?, numLocali=?, descrizione=?, prezzo=?, isArredata=?, isDisponibile=?, url1=?, url2=?, url3=?, url4=?, url5=? WHERE id_annuncio=?'
    success = False

    try:
        cursor.execute(query, (annuncio['titolo'], annuncio['tipoCasa'], annuncio['numLocali'], annuncio['descrizione'], annuncio['prezzo'], annuncio['isArredata'], annuncio['isDisponibile'], annuncio['url1'], annuncio['url2'], annuncio['url3'], annuncio['url4'], annuncio['url5'], annuncio['id_annuncio']))
        connection.commit()
        success = True
    except Exception as e:
        print('Error', str(e))
        connection.rollback()

    cursor.close()
    connection.close()

    return success

#operazioni su PRENOTAZIONI
def get_prenotazioni_cliente(id_cliente):
    conn = sqlite3.connect('db/dbAffitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM PRENOTAZIONI, ANNUNCI WHERE id_cliente=? AND PRENOTAZIONI.id_annuncio=ANNUNCI.id_annuncio'
    cursor.execute(sql, (id_cliente, ))
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result

def get_prenotazioni_locatore(id_locatore):
    conn = sqlite3.connect('db/dbAffitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM PRENOTAZIONI, ANNUNCI, UTENTI WHERE PRENOTAZIONI.id_annuncio=ANNUNCI.id_annuncio AND PRENOTAZIONI.id_cliente=UTENTI.id_utente AND id_locatore=?'
    cursor.execute(sql, (id_locatore, ))
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result

def get_prenotazioni_annuncio(id_annuncio):
    conn = sqlite3.connect('db/dbAffitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM PRENOTAZIONI WHERE id_annuncio=?'
    cursor.execute(sql, (id_annuncio, ))
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result

def get_prenotazioni_confermate_annuncio(id_annuncio):
    conn = sqlite3.connect('db/dbAffitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM PRENOTAZIONI WHERE id_annuncio=? AND stato=?'
    cursor.execute(sql, (id_annuncio, 'accettata', ))
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result

def crea_prenotazione(nuova_prenotazione):
    connection = sqlite3.connect('db/dbAffitti.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    query = 'INSERT INTO PRENOTAZIONI(id_annuncio, id_cliente, modalita, data, orario, stato) VALUES (?,?,?,?,?,?)'
    success = False

    try:
        cursor.execute(query, (nuova_prenotazione['id_annuncio'], nuova_prenotazione['id_cliente'], nuova_prenotazione['modalita'], nuova_prenotazione['data'], nuova_prenotazione['orario'], nuova_prenotazione['stato']))
        connection.commit()
        success = True
    except Exception as e:
        print('Error', str(e))
        connection.rollback()

    cursor.close()
    connection.close()

    return success

def update_prenotazione(update):
    connection = sqlite3.connect('db/dbAffitti.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    query = 'UPDATE PRENOTAZIONI SET stato=?, motivoRifiuto=? WHERE id_prenotazione=?'
    success = False

    try:
        stato = update['stato']
        motivo = update['motivoRifiuto']
        prenotazione = update['id_prenotazione']
        cursor.execute(query, (stato, motivo, prenotazione))
        connection.commit()
        success = True
    except Exception as e:
        print('Error', str(e))
        connection.rollback()

    cursor.close()
    connection.close()

    return success

def get_locatore_prenotazione(id_prenotazione):
    conn = sqlite3.connect('db/dbAffitti.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT id_locatore FROM PRENOTAZIONI, ANNUNCI WHERE PRENOTAZIONI.id_annuncio=ANNUNCI.id_annuncio AND id_prenotazione=?'
    cursor.execute(sql, (id_prenotazione, ))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result
