from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import ImmutableMultiDict
from models import User
from datetime import date, timedelta, datetime
import dao

app = Flask(__name__)
app.config['SECRET_KEY'] = '9OLExKD4o83d4K4qwe513eqgiQWLWQDrO'

login_manager = LoginManager() 
login_manager.init_app(app)

#operazioni di autenticazione e sessione
@login_manager.user_loader
def load_user(user_id):

    db_user = dao.get_user_by_id(user_id)

    if db_user is not None:
        user = User(id=db_user['id_utente'], email=db_user['email'], nome=db_user['nome'], cognome=db_user['cognome'], password=db_user['password'], isLocatore=db_user['isLocatore'], isProfessionista=db_user['isProfessionista'], dataNascita=db_user['dataNascita'], imgProfilo=db_user['imgProfilo'])
        return user
    else:
        return None

@app.route('/login', methods=['post'])
def login():
    utente_form = request.form.to_dict()

    if 'email' not in utente_form or dao.get_user_by_email(utente_form['email']) == None:
        app.logger.error('Email non valida')
        return redirect(url_for('index'))

    db_user = dao.get_user_by_email(utente_form['email'])

    if not db_user or not check_password_hash(db_user['password'], utente_form['password']):
        flash("Non esiste l'utente")
        return redirect(url_for('index'))
    else:
        new = User(id=db_user['id_utente'], email=db_user['email'], nome=db_user['nome'], cognome=db_user['cognome'], password=db_user['password'], isLocatore=db_user['isLocatore'], isProfessionista=db_user['isProfessionista'], dataNascita=db_user['dataNascita'], imgProfilo=db_user['imgProfilo'])
        login_user(new, True)
        return redirect(url_for('index'))

@app.route('/signup', methods=['POST'])
def signup():
    new_user_from_form = request.form.to_dict()

    if 'nome' not in new_user_from_form or new_user_from_form ['nome'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))
    if 'cognome' not in new_user_from_form or new_user_from_form ['cognome'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))
    if 'email' not in new_user_from_form or new_user_from_form ['email'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))
    if dao.get_user_by_email(new_user_from_form ['email']) != None:
        app.logger.error('Questa email è gia in uso')
        return redirect(url_for('index'))
    if 'password' not in new_user_from_form or new_user_from_form ['password'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))
    if 'isLocatore' not in new_user_from_form or new_user_from_form ['isLocatore'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))
    if new_user_from_form['isLocatore'].isdigit():
        isLocatore = int(new_user_from_form ['isLocatore'])
    if isLocatore != 0 and isLocatore != 1:
        app.logger.error('Vincolo di true/false non rispettato su cliente/locatore')
        return redirect(url_for('index'))
    if 'isProfessionista' not in new_user_from_form or new_user_from_form.get['isProfessionista'] == '':
        new_user_from_form ['isProfessionista']=0
    if new_user_from_form ['isProfessionista'] != 0 and new_user_from_form ['isProfessionista'] != "1":
        app.logger.error('Vincolo di true/false non rispettato su professionista')
        return redirect(url_for('index'))
    if 'dataNascita' in new_user_from_form and new_user_from_form['dataNascita'] != '':
        dataNascita = datetime.strptime(new_user_from_form['dataNascita'], '%Y-%m-%d')
        dataMaggiorenne = dataNascita + timedelta(days = 6570)              #18*365=6570
        if datetime.today() < dataMaggiorenne:
            app.logger.error('Bisogna avere almeno la capacità di agire per effettuare alcune operazioni consentite dal login')
            return redirect(url_for('index'))

    new_user_from_form['isLocatore'] = isLocatore
    new_user_from_form['isProfessionista'] = int(new_user_from_form ['isProfessionista'])
    new_user_from_form ['password'] = generate_password_hash(new_user_from_form ['password'])
    if request.files['imgProfilo'].filename == '':
        new_user_from_form['imgProfilo'] = ''
    else:
        foto = request.files['imgProfilo']
        foto.save('static/'+new_user_from_form['nome']+foto.filename)
        new_user_from_form['imgProfilo'] = new_user_from_form['nome']+foto.filename
    
    success = dao.crea_utente(new_user_from_form)

    if success:
        flash("Utente creato")
        return redirect(url_for('index'))
    else:
        flash("Error")
        return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#route di pagine 

@app.route('/')
def index():
    annunci_db = dao.get_annunci_prezzo_decrescente()
    return render_template('index.html', annunci = annunci_db, filtro = 0)

@app.route('/home')
def home():
    annunci_db = dao.get_annunci_locali_crescente()
    return render_template('index.html', annunci = annunci_db, filtro = 1)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/profilo/<int:id>')
@login_required
def profiloCliente(id):
    utente_db = dao.get_user_by_id(id)
    prenotazioni_db = dao.get_prenotazioni_cliente(id)
    return render_template('profiloCliente.html', cliente = utente_db, prenotazioni = prenotazioni_db)

@app.route('/myProfile/<int:id>/<int:filtro>')      #filtro=0annuncio/1prenotazioni-0disponibili/1nondispo/0ricevute/1fatte
@login_required
def profiloLocatore(id, filtro):
    utente_db = dao.get_user_by_id(id)
    annunci_db = dao.get_annunci_locatore(id)
    if filtro == 00:
        return render_template('profiloLocatore.html', locatore = utente_db, annunci = annunci_db, filtro = filtro)
    if filtro == 1:
        return render_template('profiloLocatore.html', locatore = utente_db, annunci = annunci_db, filtro = filtro)
    if filtro == 10:
        prenotazioni_db = dao.get_prenotazioni_locatore(id)
        return render_template('profiloLocatore.html', locatore = utente_db, prenotazioni = prenotazioni_db, filtro = filtro)
    if filtro == 11:
        prenotazioni_db = dao.get_prenotazioni_cliente(id)
        return render_template('profiloLocatore.html', locatore = utente_db, prenotazioni = prenotazioni_db, filtro = filtro)

@app.route('/annuncio/<int:id>/<giorno>')
def show_annuncio(id, giorno):
    annuncio_db = dao.get_annuncio_by_id(id)
    prenotazioni_db = dao.get_prenotazioni_confermate_annuncio(id)
    prenotazioni_annuncio_db = dao.get_prenotazioni_annuncio(id)
    utenti_con_prenotazione = []
    for prenotazione in prenotazioni_annuncio_db:
        if prenotazione[6] != 'rifiutata':                                  #prenotazione[6]=stato
            utenti_con_prenotazione.append(prenotazione['id_cliente'])
    slot_possibili = {}
    for i in range(0,7):
        slot_possibili[date.today()+timedelta(days=i)] = [1, 2, 3, 4]
    for prenotazione in prenotazioni_db:
        if datetime.strptime(prenotazione[4], "%Y-%m-%d").date() in slot_possibili:             #prenotazione[4]=data; prenotazione[5]=orario
            slot_possibili.get(datetime.strptime(prenotazione[4], "%Y-%m-%d").date()).pop(prenotazione[5]-1)
    locatore_db = dao.get_user_by_id(annuncio_db[8])        #annuncio_db[8] = id_locatore     
    
    if giorno == 'null':        
        return render_template('annuncio.html', annuncio = annuncio_db, slot_visita = slot_possibili, giorno_scelto = 'null', locatore = locatore_db, utenti_con_prenotazione = utenti_con_prenotazione)
    else:
        return render_template('annuncio.html', annuncio = annuncio_db, slot_visita = slot_possibili, giorno_scelto = datetime.strptime(giorno, "%Y-%m-%d").date(), locatore = locatore_db, utenti_con_prenotazione = utenti_con_prenotazione)

@app.route('/modificaProfilo/<int:id>')
@login_required
def modifica_profilo(id):
    utente_db = dao.get_user_by_id(id)
    return render_template('modificaProfilo.html', utente = utente_db)

@app.route('/modificaAnnuncio/<int:id>')
@login_required
def modifica_annuncio(id):
    annuncio_db = dao.get_annuncio_by_id(id)
    return render_template('modificaAnnuncio.html', annuncio = annuncio_db)

#route di aggiornamento e creazione

@app.route('/nuovo_annuncio/<int:id_locatore>', methods=['post'])
@login_required
def new_annuncio(id_locatore):
    annuncio = request.form.to_dict()

    if 'titolo' not in annuncio or annuncio['titolo'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))
    if 'indirizzo' not in annuncio or annuncio['indirizzo'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))
    if 'tipoCasa' not in annuncio or annuncio['tipoCasa'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))
    if annuncio['tipoCasa'].isdigit():
        annuncio ['tipoCasa'] = int(annuncio ['tipoCasa'])
    if annuncio['tipoCasa'] < 1 or annuncio['tipoCasa'] > 4:
        app.logger.error('Il campo non ha un valore valido')
        return redirect(url_for('index'))
    if annuncio['tipoCasa'] == 1:
        annuncio['tipoCasa'] = 'Casa indipendente'
    if annuncio['tipoCasa'] == 2:
        annuncio['tipoCasa'] = 'Appartamento'
    if annuncio['tipoCasa'] == 3:
        annuncio['tipoCasa'] = 'Loft'
    if annuncio['tipoCasa'] == 4:
        annuncio['tipoCasa'] = 'Villa'
    if 'numLocali' not in annuncio or annuncio['numLocali'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))
    if annuncio ['numLocali'].isdigit():
        annuncio ['numLocali'] = int(annuncio ['numLocali'])
    if annuncio ['numLocali'] < 1 or annuncio ['numLocali'] > 5:
        app.logger.error('Il campo non ha un valore valido')
        return redirect(url_for('index'))
    if 'descrizione' not in annuncio or annuncio['descrizione'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))
    if 'prezzo' not in annuncio or annuncio['prezzo'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))
    annuncio ['prezzo'] = annuncio ['prezzo'].replace(',','.')
    if not annuncio['prezzo'].replace('.','').isdecimal():
        app.logger.error('Il prezzo è fatto da numeri')
        return redirect(url_for('index'))
    if annuncio['prezzo'].replace('.','').isdecimal():
        annuncio['prezzo'] = round(float(annuncio ['prezzo']), 2)
    if not annuncio.get('isArredata'):
        annuncio['isArredata']=0
    if annuncio['isArredata'] != 0 and annuncio['isArredata'] != '1':
        app.logger.error('Vincolo di true/false non rispettato su arredamento')
        return redirect(url_for('index'))
    if not annuncio.get('isDisponibile'):
        annuncio['isDisponibile']=0
    if annuncio.get('isDisponibile') != 0 and annuncio['isDisponibile'] != '1':
        app.logger.error('Vincolo di true/false non rispettato su disponibilità')
        return redirect(url_for('index'))
    if request.files['url1'].filename == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))

    annuncio['id_locatore'] = id_locatore
    annuncio ['isArredata'] = int(annuncio ['isArredata'])
    annuncio ['isDisponibile'] = int(annuncio ['isDisponibile'])

    fotoPrincipale = request.files['url1']
    fotoPrincipale.save('static/'+annuncio['titolo']+fotoPrincipale.filename)
    annuncio['url1'] = annuncio['titolo']+fotoPrincipale.filename

    annuncio['url2'] = None
    annuncio['url3'] = None
    annuncio['url4'] = None
    annuncio['url5'] = None
    if 'fotoSecondarie' in request.files:
        foto_secondarie = request.files.getlist('fotoSecondarie')
        i=2
        if len(foto_secondarie)>4:
            app.logger.error('Non si possono avere più di 5 foto per annuncio')
            return redirect(url_for('index'))
        for foto in foto_secondarie:
                foto.save('static/'+annuncio['titolo']+foto.filename)
                nomeVar = 'url'+str(i)
                annuncio[nomeVar] = annuncio['titolo']+foto.filename
                i+=1
    
    success = dao.crea_annuncio(annuncio)

    if success:
        flash("Annuncio creato")
        return redirect(url_for('profiloLocatore', id=id_locatore, filtro=00))

    return redirect(url_for('profiloLocatore', id=id_locatore, filtro=00))

@app.route('/nuova_prenotazione/<int:id_annuncio>/<int:id_cliente>', methods=['post'])
@login_required
def new_prenotazione(id_annuncio, id_cliente):
    prenotazione = request.form.to_dict()
    if 'orario' not in prenotazione:
        return redirect(url_for('show_annuncio', id = id_annuncio, giorno = prenotazione.get('data')))
    else:
        if 'modalita' not in prenotazione:
            app.logger.error('il campo non può essere vuoto')
            return redirect(url_for('show_annuncio', id = id_annuncio, giorno='null'))
        prenotazione['modalita'] = int(prenotazione['modalita'])
        if prenotazione['modalita']!=0 and prenotazione['modalita']!=1:
            app.logger.error('vincolo True/False non valido su modalità')
            return redirect(url_for('show_annuncio', id = id_annuncio, giorno='null'))
        if 'data' not in prenotazione or prenotazione['data'] == '':
            app.logger.error('il campo non può essere vuoto')
            return redirect(url_for('show_annuncio', id = id_annuncio, giorno='null'))
        data = datetime.strptime(prenotazione['data'], '%Y-%m-%d')
        dataTermine = datetime.today()+timedelta(days=7)
        if data>dataTermine:
            app.logger.error('la data va scelta nei prossimi 7 giorni')
            return redirect(url_for('show_annuncio', id = id_annuncio, giorno='null'))
        if 'orario' not in prenotazione or prenotazione['orario'] == '':
            app.logger.error('il campo non può essere vuoto')
            return redirect(url_for('show_annuncio', id = id_annuncio, giorno='null'))
        if prenotazione['orario'].isdecimal():
            prenotazione['orario'] = int(prenotazione['orario'])
        if prenotazione['orario']<1 or prenotazione['orario']>4:
            app.logger.error('vincolo non valido su orario')
            return redirect(url_for('show_annuncio', id = id_annuncio, giorno='null'))
        prenotazioni_db = dao.get_prenotazioni_confermate_annuncio(id_annuncio)
        for preno_db in prenotazioni_db:
            if preno_db[4] == prenotazione['data'] and preno_db[5] == prenotazione['orario']:
                app.logger.error('slot già prenotato')
                return redirect(url_for('show_annuncio', id = id_annuncio, giorno='null'))
        
        prenotazione['id_annuncio'] = id_annuncio
        prenotazione['id_cliente'] = id_cliente
        prenotazione['stato'] = 'richiesta'
        success = dao.crea_prenotazione(prenotazione)

        if success:
            flash('Prenotazione creata')
            if dao.isLocatore_by_id(id_cliente)[0] == 0:
                return redirect(url_for('profiloCliente', id = id_cliente))
            if dao.isLocatore_by_id(id_cliente)[0] == 1:
                return redirect(url_for('profiloLocatore', id = id_cliente, filtro = 11))
        else:
            return redirect(url_for('index'))

@app.route('/accettazione_visita/<int:id_visita>', methods=['post'])
@login_required
def accettazioneVisita(id_visita):
    update = request.form.to_dict()
    update['id_prenotazione'] = id_visita
    if 'stato' not in update or (update['stato'] != "0" and update['stato'] != "1"):
        app.logger.error('Il campo non va manipolato in modo strano')
        id_locatore = dao.get_locatore_prenotazione(id_visita)[0]
        return redirect(url_for('profiloLocatore', id = id_locatore, filtro = 10))
    if update['stato'] == "0":
        update['stato'] = 'accettata'
        update['motivoRifiuto'] = ''
    if update['stato'] == "1":
        update['stato'] = 'rifiutata'
        if 'motivoRifiuto' not in update or update['motivoRifiuto'] == '':
            app.logger.error('Il campo non può essere vuoto')
            id_locatore = dao.get_locatore_prenotazione(id_visita)[0]
        return redirect(url_for('profiloLocatore', id = id_locatore, filtro = 10))
    success = dao.update_prenotazione(update)
    if success:
        id_locatore = dao.get_locatore_prenotazione(id_visita)[0]
        return redirect(url_for('profiloLocatore', id = id_locatore, filtro = 10))
    else:
        return redirect(url_for('show_annuncio', id = id_visita, giorno = 'null'))

@app.route('/modifica_utente/<int:id_utente>', methods=['post'])
@login_required
def update_utente(id_utente):
    new_utente = request.form.to_dict()
    utente_db = dao.get_user_by_id(id_utente)
    update = {}
    if 'nome' in new_utente and new_utente['nome'] != '':
        update['nome'] = new_utente['nome']
    else:
        update['nome'] = utente_db[3]
    if 'cognome' in new_utente and new_utente['cognome'] != '':
        update['cognome'] = new_utente['cognome']
    else:
        update['cognome'] = utente_db[4]
    if 'email' in new_utente and new_utente['email'] != '':
        update['email'] = new_utente['email']
    else:
        update['email'] = utente_db[1]
    if 'password' in new_utente and new_utente['password'] != '':
        update['password'] = generate_password_hash(new_utente['password'])
    else:
        update['password'] = utente_db[2]
    if 'dataNascita' in new_utente and new_utente['dataNascita'] != '':
        dataNascita = datetime.strptime(new_utente['dataNascita'], '%Y-%m-%d')
        dataMaggiorenne = dataNascita + timedelta(days = 6570)              #18*365=6570
        if datetime.today() < dataMaggiorenne:
            app.logger.error('Bisogna avere almeno la capacità di agire per effettuare alcune operazioni consentite dal login')
            return redirect(url_for('modifica_profilo', id = id_utente))
        else:
            update['dataNascita'] = new_utente['dataNascita']
    else:
        update['dataNascita'] = utente_db[7]
    if 'eliminaFoto' in new_utente and new_utente['eliminaFoto'] == '1':
        if request.files['imgProfilo'].filename != '':
            fotoProfilo = request.files['imgProfilo']
            fotoProfilo.save('static/'+update['nome']+fotoProfilo.filename)
            update['imgProfilo'] = update['nome']+fotoProfilo.filename
        else:
            update['imgProfilo'] = ''
    elif request.files['imgProfilo'].filename != '':
        fotoProfilo = request.files['imgProfilo']
        fotoProfilo.save('static/'+update['nome']+fotoProfilo.filename)
        update['imgProfilo'] = update['nome']+fotoProfilo.filename
    else:
        update['imgProfilo'] = utente_db[8]

    update['id_utente'] = id_utente
    success = dao.modifica_utente(update)
    if success:
        if dao.isLocatore_by_id(id_utente)[0] == 0:
            return redirect(url_for('profiloCliente', id = id_utente))
        if dao.isLocatore_by_id(id_utente)[0] == 1:
            return redirect(url_for('profiloLocatore', id = id_utente, filtro = 00))
    else:
        return redirect(url_for('index'))

@app.route('/modifica_annuncio/<int:id_annuncio>', methods=['post'])
@login_required
def update_annuncio(id_annuncio):
    annuncio = request.form.to_dict()
    vecchioAnnuncio = dao.get_annuncio_by_id(id_annuncio)

    if 'titolo' not in annuncio or annuncio ['titolo'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('modifica_annuncio', id = id_annuncio))
    if 'indirizzo' not in annuncio or annuncio ['indirizzo'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('modifica_annuncio', id = id_annuncio))
    if 'tipoCasa' not in annuncio or annuncio ['tipoCasa'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('modifica_annuncio', id = id_annuncio))
    if annuncio ['tipoCasa'].isdigit():
        annuncio ['tipoCasa'] = int(annuncio ['tipoCasa'])
    if annuncio ['tipoCasa'] < 1 or annuncio ['tipoCasa'] > 4:
        app.logger.error('Il campo non ha un valore valido')
        return redirect(url_for('modifica_annuncio', id = id_annuncio))
    if annuncio ['tipoCasa'] == 1:
        annuncio['tipoCasa'] = 'Casa indipendente'
    if annuncio ['tipoCasa'] == 2:
        annuncio['tipoCasa'] = 'Appartamento'
    if annuncio ['tipoCasa'] == 3:
        annuncio['tipoCasa'] = 'Loft'
    if annuncio ['tipoCasa'] == 4:
        annuncio['tipoCasa'] = 'Villa'
    if 'numLocali' not in annuncio or annuncio['numLocali'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('modifica_annuncio', id = id_annuncio))
    if annuncio ['numLocali'].isdigit():
        annuncio ['numLocali'] = int(annuncio ['numLocali'])
    if annuncio ['numLocali'] < 1 or annuncio ['numLocali'] > 5:
        app.logger.error('Il campo non ha un valore valido')
        return redirect(url_for('modifica_annuncio', id = id_annuncio))
    if  'descrizione' not in annuncio or annuncio ['descrizione'] == '':
        annuncio['descrizione'] = vecchioAnnuncio[5]
    if 'prezzo' not in annuncio or annuncio['prezzo'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('modifica_annuncio', id = id_annuncio))
    annuncio ['prezzo'] = annuncio ['prezzo'].replace(',','.')
    if annuncio['prezzo'].replace('.','').isdigit():
        annuncio['prezzo'] = round(float(annuncio ['prezzo']), 2)
    if 'isArredata' not in annuncio:
        annuncio['isArredata']=0
    if annuncio ['isArredata'] != 0 and annuncio ['isArredata'] != '1':
        app.logger.error('Vincolo di true/false non rispettato su arredamento')
        return redirect(url_for('modifica_annuncio', id = id_annuncio))
    if 'isDisponibile' not in annuncio:
        annuncio['isDisponibile']=0
    if annuncio.get('isDisponibile') != 0 and annuncio ['isDisponibile'] != '1':
        app.logger.error('Vincolo di true/false non rispettato su disponibilità')
        return redirect(url_for('modifica_annuncio', id = id_annuncio))
    #se elimina foto
    if request.files['url1'].filename == '' and 'elimina1' in annuncio and annuncio['elimina1'] == '1':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('modifica_annuncio', id = id_annuncio))
    if request.files['url2'].filename == '' and 'elimina2' in annuncio and annuncio['elimina2'] == '1':
        annuncio['url2'] = None
    if request.files['url3'].filename == '' and 'elimina3' in annuncio and annuncio['elimina3'] == '1':
        annuncio['url3'] = None
    if request.files['url4'].filename == '' and 'elimina4' in annuncio and annuncio['elimina4'] == '1':
        annuncio['url4'] = None
    if request.files['url5'].filename == '' and 'elimina5' in annuncio and annuncio['elimina5'] == '1':
        annuncio['url5'] = None
    #se cambia foto
    if 'elimina1' in annuncio and annuncio['elimina1'] == '1' and request.files['url1'].filename != '':
        request.files['url1'].save('static/'+annuncio['titolo']+request.files['url1'].filename)
        annuncio['url1'] = annuncio['titolo']+request.files['url1'].filename
    if 'elimina2' in annuncio and annuncio['elimina2'] == '1' and request.files['url2'].filename != '':
        request.files['url2'].save('static/'+annuncio['titolo']+request.files['url2'].filename)
        annuncio['url2'] = annuncio['titolo']+request.files['url2'].filename
    if 'elimina3' in annuncio and annuncio['elimina3'] == '1' and request.files['url3'].filename != '':
        request.files['url3'].save('static/'+annuncio['titolo']+request.files['url3'].filename)
        annuncio['url3'] = annuncio['titolo']+request.files['url3'].filename
    if 'elimina4' in annuncio and annuncio['elimina4'] == '1' and request.files['url4'].filename != '':
        request.files['url4'].save('static/'+annuncio['titolo']+request.files['url4'].filename)
        annuncio['url4'] = annuncio['titolo']+request.files['url4'].filename
    if 'elimina5' in annuncio and annuncio['elimina5'] == '1' and request.files['url5'].filename != '':
        request.files['url5'].save('static/'+annuncio['titolo']+request.files['url5'].filename)
        annuncio['url5'] = annuncio['titolo']+request.files['url5'].filename
    #se aggiunge foto
    if 'elimina1' not in annuncio and request.files['url1'].filename != '':
        flash('come è possibile che tu sia finito qui?')
        return redirect(url_for('modifica_annuncio', id = id_annuncio))
    if 'elimina2' not in annuncio and request.files['url2'].filename != '':
        request.files['url2'].save('static/'+annuncio['titolo']+request.files['url2'].filename)
        annuncio['url2'] = annuncio['titolo']+request.files['url2'].filename
    if 'elimina3' not in annuncio and request.files['url3'].filename != '':
        request.files['url3'].save('static/'+annuncio['titolo']+request.files['url3'].filename)
        annuncio['url3'] = annuncio['titolo']+request.files['url3'].filename
    if 'elimina4' not in annuncio and request.files['url4'].filename != '':
        request.files['url4'].save('static/'+annuncio['titolo']+request.files['url4'].filename)
        annuncio['url4'] = annuncio['titolo']+request.files['url4'].filename
    if 'elimina5' not in annuncio and request.files['url5'].filename != '':
        request.files['url5'].save('static/'+annuncio['titolo']+request.files['url5'].filename)
        annuncio['url5'] = annuncio['titolo']+request.files['url5'].filename
    #se non cambia foto
    if 'elimina1' not in annuncio and request.files['url1'].filename == '':
        annuncio['url1'] = vecchioAnnuncio[10]
    if 'elimina2' not in annuncio and request.files['url2'].filename == '':
        annuncio['url2'] = vecchioAnnuncio[11]
    if 'elimina3' not in annuncio and request.files['url3'].filename == '':
        annuncio['url3'] = vecchioAnnuncio[12]
    if 'elimina4' not in annuncio and request.files['url4'].filename == '':
        annuncio['url4'] = vecchioAnnuncio[13]
    if 'elimina5' not in annuncio and request.files['url5'].filename == '':
        annuncio['url5'] = vecchioAnnuncio[14]

    annuncio['id_annuncio'] = id_annuncio
    annuncio ['isArredata'] = int(annuncio ['isArredata'])
    annuncio ['isDisponibile'] = int(annuncio ['isDisponibile'])
    success = dao.modifica_annuncio(annuncio)
    if success:
        return redirect(url_for('show_annuncio', id = id_annuncio, giorno = 'null'))
    else:
        flash('qualcosa è andato storto')
        return redirect(url_for('modifica_annuncio', id = id_annuncio))