import os
from flask import Flask, render_template, request, redirect, session, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'QAZWSXEDCRFVTGBYHNUJMIKOLP'

# Configura la conexión con MongoDB
client = MongoClient('mongodb+srv://desarrollo2023:assssdwwwwq@millenium.pardqk8.mongodb.net/')
db = client['millenium']
user_collection = db['users']
trabajadores_collection = db['trabajadores']




# Ruta para el login
@app.route('/')
def login():
    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = user_collection.find_one({'username': username, 'password': password})
        if user:
            session['username'] = user['username']
            if user['rol'] == 'admin':
                trabajadores = trabajadores_collection.find()
                return render_template('admin_profile.html', username=username, trabajadores=trabajadores)
            elif user['rol'] == 'trabajador':
                trabajador = trabajadores_collection.find_one({'user_id': user['user_id']})
                return render_template('user_profile.html', username=username, trabajador=trabajador)
            else:
                return render_template('error.html', message='Rol de usuario no válido.')
        else:
            return render_template('error.html', message='Usuario o contraseña incorrectos.')

    # Si la solicitud es GET, simplemente renderiza el formulario de inicio de sesión
    return render_template('login.html')

#ruta para que cuando cierre sesion y ponga en regresar no pueda volver a la pagina anterior
@app.route('/back')
def back():
    return render_template('login.html')


# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/admin_profile')
def admin_profile():
    if 'username' in session:
        # Obtén todos los trabajadores
        trabajadores = trabajadores_collection.find()
        return render_template('admin_profile.html', username=session['username'], trabajadores=trabajadores)
    else:
        return redirect('/')



# Ruta para agregar un trabajador (solo para administradores)
from bson.objectid import ObjectId

@app.route('/admin_add', methods=['POST'])
def admin_add():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    rut = request.form['rut']
    sexo = request.form['sexo']
    cargo = request.form['cargo']
    direccion = request.form['direccion']
    telefono = request.form['telefono']
    fecha_ingreso = request.form['fecha_ingreso']
    area = request.form['area']
    departamento = request.form['departamento']
    password = request.form['password']
    rol = request.form['rol']
    carga_nombre = request.form['carga_nombre']
    relacion = request.form['relacion']
    edad_carga = request.form['edad_carga']
    contacto_emergencia = request.form['contacto_emergencia']
    telefono_emergencia = request.form['telefono_emergencia']
    direccion_emergencia = request.form['direccion_emergencia']
    
    # Genera un nuevo ObjectId para el usuario y el trabajador
    user_id = ObjectId()
    
    # Inserta el usuario y obtén su ID
    user_collection.insert_one({
        'username': nombre.lower() + '_' + apellido.lower(),
        'password': password,  
        'rol': rol,
        'user_id': user_id
    })

    # Inserta el trabajador relacionado con el usuario
    trabajadores_collection.insert_one({
        '_id': user_id,
        'nombre': nombre,
        'apellido': apellido,
        'rut': rut,
        'sexo': sexo,
        'cargo': cargo,
        'direccion': direccion,
        'telefono': telefono,
        'fecha_ingreso': fecha_ingreso,
        'area': area,
        'departamento': departamento,
        'user_id': user_id,
        'carga_nombre': carga_nombre ,
        'relacion': relacion,
        'edad_carga': edad_carga,
        'contacto_emergencia': contacto_emergencia,
        'telefono_emergencia': telefono_emergencia,
        'direccion_emergencia': direccion_emergencia
    })

    # Actualiza la lista de trabajadores después de agregar uno nuevo
    trabajadores = trabajadores_collection.find()

    return render_template('admin_profile.html', username=session['username'], trabajadores=trabajadores)





@app.route('/admin_delete/<id>', methods=['POST'])
def admin_delete(id):
    # Obtén el ID del usuario asociado al trabajador
    trabajador = trabajadores_collection.find_one({'user_id': ObjectId(id)})
    user_id = trabajador['user_id']

    # Elimina el trabajador
    trabajadores_collection.delete_one({'user_id': ObjectId(id)})

    # Elimina el usuario
    user_collection.delete_one({'user_id': ObjectId(user_id)})

    # Actualiza la lista de trabajadores después de eliminar uno
    trabajadores = trabajadores_collection.find()

    return render_template('admin_profile.html', username=session['username'], trabajadores=trabajadores)

@app.route('/user_update', methods=['POST'])
def user_update():
    if 'username' in session:
        user = user_collection.find_one({'username': session['username']})
        trabajador = trabajadores_collection.find_one({'user_id': user['user_id']})

        # Obtener los datos enviados desde el formulario
        carga_nombre= request.form['carga_nombre']
        edad_carga = request.form['edad_carga']
        relacion = request.form['relacion']
        contacto_emergencia = request.form['contacto_emergencia']
        telefono_emergencia = request.form['telefono_emergencia']
        direccion_emergencia = request.form['direccion_emergencia']
        direccion = request.form['direccion']
        telefono = request.form['telefono']

        # Actualizar la información del trabajador en la base de datos
        trabajadores_collection.update_one({'_id': trabajador['_id']}, {'$set': {
            'carga_nombre': carga_nombre ,
            'edad_carga': edad_carga,
            'relacion': relacion,
            'contacto_emergencia': contacto_emergencia,
            'telefono_emergencia': telefono_emergencia,
            'direccion_emergencia': direccion_emergencia,
            'direccion': direccion,
            'telefono': telefono
        }})

        # Redirigir al perfil del usuario con los cambios actualizados
        return redirect('/user_profile')

    else:
        return redirect('/')

@app.route('/search', methods=['POST'])
def search():
    if 'username' in session:
        search_term = request.form['search_term']
        trabajadores = trabajadores_collection.find({
            '$or': [
                {'nombre': {'$regex': search_term, '$options': 'i'}},
                {'rut': {'$regex': search_term, '$options': 'i'}},
                {'cargo': {'$regex': search_term, '$options': 'i'}},
                {'sexo': {'$regex': search_term, '$options': 'i'}}
            ]
        })
        return render_template('search_results.html', trabajadores=trabajadores)

    else:
        return redirect('/')
    



@app.route('/user_profile')
def user_profile():
    if 'username' in session:
        user = user_collection.find_one({'username': session['username']})
        trabajador = trabajadores_collection.find_one({'user_id': user['user_id']})

        return render_template('user_profile.html', username=session['username'], trabajador=trabajador)
    else:
        return redirect('/')

from datetime import datetime
@app.route('/enviar_solicitud', methods=['POST'])
def enviar_solicitud():
    if 'username' in session:
        user = user_collection.find_one({'username': session['username']})
        if user['rol'] == 'trabajador':
            trabajador = trabajadores_collection.find_one({'user_id': user['user_id']})

            # Obtén los datos enviados desde el formulario
            fecha = request.form['fecha']
            motivo = request.form['motivo']

            # Convierte la fecha a un formato adecuado (puedes usar una biblioteca para validarla)
            try:
                fecha = datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                return render_template('user_profile.html', username=session['username'], trabajador=trabajador, message='Fecha inválida.')

            # Crea la solicitud
            solicitud = {
                'fecha': fecha,
                'motivo': motivo,
                'estado': 'pendiente'
            }

            # Agrega la solicitud a la lista de solicitudes de permiso del trabajador
            trabajadores_collection.update_one(
                {'user_id': user['user_id']},
                {'$push': {'solicitudes_permiso': solicitud}}
            )

            return render_template('user_profile.html', username=session['username'], trabajador=trabajador, message='Solicitud enviada con éxito.')
        else:
            return render_template('error.html', message='No tienes permiso para enviar solicitudes.')
    else:
        return redirect('/')

@app.route('/solicitudes_pendientes')
def solicitudes_pendientes():
    if 'username' in session:
        user = user_collection.find_one({'username': session['username']})
        if user['rol'] == 'admin':
            trabajadores = trabajadores_collection.find()
            return render_template('admin_profile.html', username=session['username'], trabajadores=trabajadores)
        else:
            return render_template('error.html', message='No tienes permiso para ver las solicitudes pendientes.')
    else:
        return redirect('/')

@app.route('/aprobar_solicitud/<trabajador_id>/<solicitud_index>', methods=['POST'])
def aprobar_solicitud(trabajador_id, solicitud_index):
    # Obtener el trabajador y la solicitud de permiso
    trabajador = trabajadores_collection.find_one({'_id': ObjectId(trabajador_id)})
    solicitud = trabajador['solicitudes_permiso'][int(solicitud_index)]

    # Actualizar el estado de la solicitud
    trabajadores_collection.update_one(
        {'_id': ObjectId(trabajador_id)},
        {'$set': {f'solicitudes_permiso.{solicitud_index}.estado': 'aprobada'}}
    )

    return redirect('/solicitudes_pendientes')

@app.route('/denegar_solicitud/<trabajador_id>/<solicitud_index>', methods=['POST'])
def denegar_solicitud(trabajador_id, solicitud_index):
    # Obtener el trabajador y la solicitud de permiso
    trabajador = trabajadores_collection.find_one({'_id': ObjectId(trabajador_id)})
    solicitud = trabajador['solicitudes_permiso'][int(solicitud_index)]

    # Actualizar el estado de la solicitud
    trabajadores_collection.update_one(
        {'_id': ObjectId(trabajador_id)},
        {'$set': {f'solicitudes_permiso.{solicitud_index}.estado': 'denegada'}}
    )

    return redirect('/solicitudes_pendientes')




    
if __name__ == '__main__':
    app.run()
