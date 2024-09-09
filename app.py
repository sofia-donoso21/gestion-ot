from module import Config, DataBase, Utils, ConfigAzure
from flask import Flask, json, jsonify, redirect, render_template, request, session
import pandas as pd
import os



app = Flask(__name__)






# Validar acceso antes de cada request
@app.before_request
def before_request():
    # Si la ruta es '/public/soporte', permitir acceso sin autenticación y no redirigir
    if request.path == '/public/soporte':
        return None  # Continuar normalmente sin redirigir

    # Verificar si el usuario tiene sesión activa
    username = session.get('username')

    # Si no está autenticado y la ruta no es '/auth', redirigir al login
    if not username and request.path != '/auth':
        return redirect('/auth')



# @app.route('/')
# def index():
#     username = session.get('username')
#     if username:
#         password = session.get('password')
#         if password:
#             return redirect('/inicio')
#         else:
#             return render_template("lockscreen.html", username= username.upper())
#     else:
#         return redirect('/auth')
@app.route('/')
def index():
    username = session.get('username')
    if username:
        password = session.get('password')
        if password:
            return redirect('/inicio')
        else:
            return render_template("lockscreen.html", username=username.upper())
    else:
        if request.path == '/public/soporte':
            return redirect('/public/soporte')
        else:
            return redirect('/auth')


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'GET':
        return render_template("auth.html")
    elif request.method == 'POST':
        try:
            user = request.form['user']
            password = Utils.encryptSHA256(request.form['password'])  
            connection = DataBase.get_db_connection()
            connection.begin() 
            with connection.cursor() as cursor:
                cursor.callproc('validate_auth', (user, password, 0, 0))
                cursor.execute("SELECT @_validate_auth_2 AS code, @_validate_auth_3 user_id")
                result = cursor.fetchone()
                code = result['code']
                user_id = result['user_id']
                if code == 200:
                    session['username'] = user
                    session['userid'] = user_id
                return jsonify({'code': code, 'user_id': user_id}) 
        except Exception as e:
            print(e)
            return jsonify({'error': e}) 
        finally:
            if 'connection' in locals():
                connection.close()
    else:
        return render_template("auth.html")


@app.route('/inicio', methods=['GET', 'POST'])
def inicio():  
    if request.method == 'GET':
        try:
            userid = session.get('userid')
            connection = DataBase.get_db_connection()
            connection.begin() 
            with connection.cursor() as cursor:
                query = "SELECT "
                query += "CONCAT(SUBSTRING_INDEX(nombre, ' ', 1), ' ', LEFT(app_pat, 1), '. ', ap_mat) nombre, "
                query += "(SELECT COUNT(cliente_id) FROM cliente WHERE estado = '0') count_clientes, "
                query += "(SELECT COUNT(sitio_id) FROM sitio WHERE estado = '0') count_sitios, "
                query += "(SELECT COUNT(ot_id) FROM orden_trabajo WHERE estado = '0') count_ot "
                query += f"FROM usuario WHERE usuario_id = {userid} "
                cursor.execute(query)
                data = cursor.fetchall()
                print("Data home: ", data)
                return render_template("dashboard.html", data=data)
        except Exception as e:
            print(e)
            return redirect('/auth')
        finally:
            if 'connection' in locals():
                connection.close()

    elif request.method == 'POST':
        return
    else:
        return


@app.route('/usuario', methods=['GET', 'POST'])
def usuario():
    if request.method == 'GET':
        try:
            userid = session.get('userid')
            connection = DataBase.get_db_connection()
            connection.begin() 
            with connection.cursor() as cursor:
                query = "SELECT "
                query += "usuario_id id, "
                query += "formatear_rut(numrut, dv) rut_formateado, "
                query += "username usuario, "
                query += "nombre, "
                query += "app_pat, "
                query+= "ap_mat, "
                query += "perfil ,"
                query += "CASE "
                query += "WHEN estado = 0 THEN 'Activo' "
                query += "WHEN estado = 1 THEN 'Inactivo' "
                query += "ELSE 'Desconocido' "
                query += "END AS estado "
                query += f"FROM usuario "
                cursor.execute(query)
                data = cursor.fetchall()
                cursor.execute(f"SELECT CONCAT(nombre, ' ', app_pat,' ', ap_mat ) nombre, CONCAT(SUBSTRING_INDEX(nombre, ' ', 1), ' ', LEFT(app_pat, 1), '. ', ap_mat) username FROM usuario WHERE usuario_id={userid}")
                name = cursor.fetchone()
                return render_template("user.html", data=data, name=name['nombre'], username=name['username'])
        except Exception as e:
            print(e)
            return redirect('/auth')
        finally:
            if 'connection' in locals():
                connection.close()

    elif request.method == 'POST':
        try:
            data = request.data
            json_data = json.loads(data)

            numrut = json_data['rut']
            dv = json_data['dv']
            username = json_data['user']
            pswrd = Utils.encryptSHA256(json_data['pswrd'])
            nombre =json_data['nombres']
            app_pat = json_data['ap_pat']
            ap_mat = json_data['ap_mat']
            perfil = json_data['perfil']
            code = 0
            msge = ""
            userid = 0
            params = [numrut, dv, username, pswrd, nombre, app_pat, ap_mat, perfil, code, msge, userid]
            
            # Llamo al sp de crear usuario
            connection = DataBase.get_db_connection()
            connection.begin() 
            with connection.cursor() as cursor:
                cursor.callproc('create_user', (params))
                cursor.execute("SELECT @_create_user_8 AS code, @_create_user_9 AS msge, @_create_user_10 AS userid")
                result = cursor.fetchone()
            return jsonify({'code': result['code'], 'msge': result['msge']})
        except Exception as e:
            print(e)
            return jsonify({'code': 500})
        finally:
            if 'connection' in locals():
                connection.close()


@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if request.method == 'GET':
        try:
            userid = session.get('userid')
            connection = DataBase.get_db_connection()
            connection.begin() 
            with connection.cursor() as cursor:
                query = "SELECT "
                query += "perfil_id id, "
                query += "nombre, "
                query += "descripcion, "
                query += "fecha_creacion ,"
                query += "CASE "
                query += "WHEN estado = 0 THEN 'Activo' "
                query += "WHEN estado = 1 THEN 'Inactivo' "
                query += "ELSE 'Desconocido' "
                query += "END AS estado "
                query += f"FROM perfil "
                cursor.execute(query)
                data = cursor.fetchall()

                query_user = "SELECT "
                query_user += "CONCAT(nombre, ' ', app_pat,' ', ap_mat ) nombre, "
                query_user += "CONCAT(SUBSTRING_INDEX(nombre, ' ', 1), ' ', LEFT(app_pat, 1), '. ', ap_mat) username "
                query_user += f"FROM usuario WHERE usuario_id={userid} "
                cursor.execute(query_user)
                data_user = cursor.fetchone()

                # Usua Permisos
                query_permisos = "SELECT "
                query_permisos += "A.usua_permisos_id id, "
                query_permisos += "B.nombre, "
                query_permisos += "A.permiso, "
                query_permisos += "A.fecha_creacion, "
                query_permisos += "CASE "
                query_permisos += "WHEN A.estado = 0 THEN 'Activo' "
                query_permisos += "WHEN A.estado = 1 THEN 'Inactivo' "
                query_permisos += "ELSE 'Desconocido' "
                query_permisos += "END AS estado, "



                query_permisos += "CASE "
                query_permisos += "WHEN A.permiso = 'SIUD' THEN 'El usuario tiene todos los permisos.' "
                query_permisos += "WHEN A.permiso = 'SIU0' THEN 'El usuario puede ver, agregar y editar.' "
                query_permisos += "WHEN A.permiso = 'SI00' THEN 'El usuario puede ver y agregar.' "
                query_permisos += "ELSE '' "
                query_permisos += "END AS tooltip "
                query_permisos += "FROM usua_permisos A "
                query_permisos += "LEFT JOIN perfil B ON A.perfil_id=B.perfil_id "
                cursor.execute(query_permisos)
                data_permisos = cursor.fetchall()

                # Perfiles
                query_perfiles = "SELECT perfil_id id, nombre FROM perfil"
                cursor.execute(query_perfiles)
                data_perfiles = cursor.fetchall()


                # Menu
                query_menu = "SELECT "
                query_menu += "A.usua_menu_id id, "
                query_menu += "B.nombre perfil, "
                query_menu += "A.item_name, "
                query_menu += "A.sub_item_name, "
                query_menu += "A.item_link, "
                query_menu += "A.fecha_creacion, "
                query_menu += "CASE "
                query_menu += "WHEN A.estado = 0 THEN 'Activo' "
                query_menu += "WHEN A.estado = 1 THEN 'Inactivo' "
                query_menu += "ELSE 'Desconocido' "
                query_menu += "END AS estado "
                query_menu += "FROM usua_menu A "
                query_menu += "LEFT JOIN perfil B ON A.perfil_id=B.perfil_id "
                cursor.execute(query_menu)
                data_menu = cursor.fetchall()

                return render_template("role.html", data=data, data_perfiles=data_perfiles, data_menu=data_menu, data_permisos=data_permisos, name=data_user['nombre'], username=data_user['username'])
        except Exception as e:
            print(e)
            return redirect('/inicio')
        finally:
            if 'connection' in locals():
                connection.close()

    elif request.method == 'POST':
        try:
            data = request.data
            json_data = json.loads(data)
            v_permissions = ''
            if 'permissions' in json_data:
                permissions = json_data['permissions']
                for permission in permissions:
                    if permission:
                        v_permissions += permission
                print("Permisos: ", v_permissions)

                params = [json_data['profile'], v_permissions, 0, '', 0]
                connection = DataBase.get_db_connection()
                connection.begin() 
                with connection.cursor() as cursor:
                    cursor.callproc('create_permissions', (params))
                    cursor.execute("SELECT @_create_permissions_2 AS code, @_create_permissions_3 AS msge, @_create_permissions_4 AS usua_permisos_id")
                    result = cursor.fetchone()
                return jsonify({'code': result['code'], 'msge': result['msge']})
            elif 'menu' in json_data:
                print("Menu")
            else:
                params = [json_data['name'], json_data['detail'], 0, '', 0]
                connection = DataBase.get_db_connection()
                connection.begin() 
                with connection.cursor() as cursor:
                    cursor.callproc('create_profile', (params))
                    cursor.execute("SELECT @_create_profile_2 AS code, @_create_profile_3 AS msge, @_create_profile_4 AS perfil_id")
                    result = cursor.fetchone()
                return jsonify({'code': result['code'], 'msge': result['msge']})
        except Exception as e:
            print(e)
            return redirect('/inicio')
        finally:
            if 'connection' in locals():
                connection.close()


@app.route('/cliente', methods=['GET', 'POST'])
def cliente():
    if request.method == 'GET':
        try:
            userid = session.get('userid')
            connection = DataBase.get_db_connection()
            connection.begin() 
            with connection.cursor() as cursor:
                query = "SELECT "
                query += "cliente_id id, "
                query += "nombre, "
                query += "razon_social, "
                query += "email, "
                query += "detalle, "
                query+= "fecha_creacion, "
                query += "estado, "
                query += "CASE "
                query += "WHEN estado = 0 THEN 'Activo' "
                query += "WHEN estado = 1 THEN 'Inactivo' "
                query += "ELSE 'Desconocido' "
                query += "END AS estado_format "
                query += f"FROM cliente "
                cursor.execute(query)
                data = cursor.fetchall()
                cursor.execute(f"SELECT CONCAT(nombre, ' ', app_pat,' ', ap_mat ) nombre, CONCAT(SUBSTRING_INDEX(nombre, ' ', 1), ' ', LEFT(app_pat, 1), '. ', ap_mat) username FROM usuario WHERE usuario_id={userid}")
                name = cursor.fetchone()

            return render_template("client.html", data=data, name=name['nombre'], username=name['username'])
        except Exception as e:
            print(e)
            return redirect('/inicio')
        finally:
            if 'connection' in locals():
                connection.close()
    elif request.method == 'POST':
        try:
            connection = DataBase.get_db_connection()
            connection.begin() 
            with connection.cursor() as cursor:
                data = request.data
                json_data = json.loads(data)
                msge = ''
                http_code = 0
                cliente_id = 0
                
                params = [
                    json_data['name'], 
                    json_data['company_name'], 
                    json_data['email'], 
                    json_data['detail'], 
                    http_code, 
                    msge, 
                    cliente_id]
                cursor.callproc('create_client', params)
                cursor.execute("SELECT @_create_client_4 AS code, @_create_client_5 AS msge, @_create_client_6 AS clientid")
                result = cursor.fetchone()
                return jsonify({'code': result['code'], 'msge': result['msge']})
        except Exception as e:
            print(e)
            return redirect('/inicio')
        finally:
            if 'connection' in locals():
                connection.close()


@app.route('/cliente/masivo', methods=['GET', 'POST'])
def cliente_masivo():
    if request.method == 'GET':
        try:
            userid = session.get('userid')
            connection = DataBase.get_db_connection()
            connection.begin() 
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT CONCAT(nombre, ' ', app_pat,' ', ap_mat ) nombre, CONCAT(SUBSTRING_INDEX(nombre, ' ', 1), ' ', LEFT(app_pat, 1), '. ', ap_mat) username FROM usuario WHERE usuario_id={userid}")
                name = cursor.fetchone()
            return render_template("bulk_client_upload.html", name=name['nombre'], username=name['username'])
        except Exception as e:
                print(e)
                return redirect('/inicio')
        finally:
            if 'connection' in locals():
                connection.close()
    elif request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'code': 400, 'msge': 'No se seleccionó ningún archivo'})

        file = request.files['file']
        formato = request.form.get('formato')
        separador = request.form.get('separador')

        if file.filename == '':
            return jsonify({'code': 400, 'msge': 'Nombre de archivo vacío'})

        # Guardar el archivo temporalmente en /static/tmp
        file_path = os.path.join('static', 'tmp', file.filename)
        file.save(file_path)

        # Procesar el archivo dependiendo del formato
        if formato == 'csv' or formato == 'txt':
            try:
                # Leer el archivo Excel usando pandas
                clientes_sitios = pd.read_csv(file, sep=separador)

                # Normalización de df
                columnas = clientes_sitios.columns
                clientes_sitios.columns = clientes_sitios.columns.str.lower()

                # Renombrar columnas de clientes (solo las que existen)
                clientes_sitios = clientes_sitios.rename(columns={
                    "nombre cliente": "cli_nombre",
                    "razon social cliente": "cli_razon_social",
                    "contacto cliente": "cli_contacto",
                    "correo cliente": "cli_correo",
                    "rubro o detalle": "cli_detalle",
                    "fecha de cuando ingreso el cliente a redinnova (si se tiene)": "cli_fecha_ingreso",
                    "nombre del sitio (si se tiene mas de 1 sitio, repetir la fila)": "site_nombre",
                    "nombre del sitio": "site_detalle",
                    "ubicacion del sitio": "site_ubicacion"
                })

                # Crear un DataFrame con las columnas que contienen 'cli'
                if any('cli' in col for col in clientes_sitios.columns):
                    df_clientes = clientes_sitios.filter(like='cli')
                    # Eliminar clientes Duplicados
                    df_clientes = df_clientes.drop_duplicates()
                    try:
                        connection = DataBase.get_db_connection()
                        connection.begin() 
                        with connection.cursor() as cursor:
                            # Convertir el DataFrame en un JSON
                            clientes_json = df_clientes.to_json(orient='records')
                            # Llamar al procedimiento almacenado y pasar el JSON como parámetro
                            cursor.callproc('InsertarClientesMasivo', (clientes_json, 0))
                            cursor.execute("SELECT @_InsertarClientesMasivo_1 AS code")
                            result = cursor.fetchone()
                            if result['code'] == 200:
                                # Borrar el archivo temporalmente después del procesamiento
                                try:
                                    os.remove(file_path)
                                except OSError as e:
                                    return jsonify({
                                        'code': result['code'],
                                        'msge': f'Error al eliminar el archivo: {e}'
                                    })
                            return jsonify({'code': result['code']})
                    except Exception as e:
                        return redirect('/inicio')
                    finally:
                        if 'connection' in locals():
                            connection.close()
                else:
                    print("No se encontraron columnas con 'cli' en el nombre.")
                    return jsonify({'code': result['code'], 'msge': 'El archivo contiene columnas no validas.'})
            except Exception as e:
                print(f"Error procesando Excel: {e}")
                return jsonify(
                    {
                        'code': result['code'], 
                        'msge': 'Error procesando el archivo: '.format(e)
                    })

        elif formato == 'xlsx':
            try:
                # Leer el archivo Excel usando pandas
                clientes_sitios = pd.read_excel(file)

                # Normalización de df
                columnas = clientes_sitios.columns
                clientes_sitios.columns = clientes_sitios.columns.str.lower()

                # Renombrar columnas de clientes (solo las que existen)
                clientes_sitios = clientes_sitios.rename(columns={
                    "nombre cliente": "cli_nombre",
                    "razon social cliente": "cli_razon_social",
                    "contacto cliente": "cli_contacto",
                    "correo cliente": "cli_correo",
                    "rubro o detalle": "cli_detalle",
                    "fecha de cuando ingreso el cliente a redinnova (si se tiene)": "cli_fecha_ingreso",
                    "nombre del sitio (si se tiene mas de 1 sitio, repetir la fila)": "site_nombre",
                    "nombre del sitio": "site_detalle",
                    "ubicacion del sitio": "site_ubicacion"
                })

                # Crear un DataFrame con las columnas que contienen 'cli'
                if any('cli' in col for col in clientes_sitios.columns):
                    df_clientes = clientes_sitios.filter(like='cli')
                    # Eliminar clientes Duplicados
                    df_clientes = df_clientes.drop_duplicates()
                    try:
                        connection = DataBase.get_db_connection()
                        connection.begin() 
                        with connection.cursor() as cursor:
                            # Convertir el DataFrame en un JSON
                            clientes_json = df_clientes.to_json(orient='records')
                            # Llamar al procedimiento almacenado y pasar el JSON como parámetro
                            cursor.callproc('InsertarClientesMasivo', (clientes_json, 0))
                            cursor.execute("SELECT @_InsertarClientesMasivo_1 AS code")
                            result = cursor.fetchone()
                            if result['code'] == 200:
                                # Borrar el archivo temporalmente después del procesamiento
                                try:
                                    os.remove(file_path)
                                except OSError as e:
                                    return jsonify({
                                        'code': result['code'],
                                        'msge': f'Error al eliminar el archivo: {e}'
                                    })
                            return jsonify({'code': result['code']})
                    except Exception as e:
                        return redirect('/inicio')
                    finally:
                        if 'connection' in locals():
                            connection.close()
                else:
                    print("No se encontraron columnas con 'cli' en el nombre.")
                    return jsonify({'code': result['code'], 'msge': 'El archivo contiene columnas no validas.'})
            except Exception as e:
                print(f"Error procesando: {e}")
                return jsonify(
                    {
                        'code': result['code'], 
                        'msge': 'Error procesando el archivo Excel: '.format(e)
                    })
        
        else:
            result = {'code': 400, 'msge': 'Formato no soportado'}


@app.route('/sitio', methods=['GET', 'POST'])
def sitio():
    if request.method == 'GET':
        try:
            userid = session.get('userid')
            connection = DataBase.get_db_connection()
            connection.begin() 
            with connection.cursor() as cursor:
                query =  "SELECT "
                query += "A.sitio_id id, "
                query += "B.nombre nombre_cliente, "
                query += "A.nombre,"
                query += "A.ubicacion, "
                query += "A.fecha_creacion, "
                query += "CASE "
                query += "WHEN A.estado = 0 THEN 'Activo' "
                query += "WHEN A.estado = 1 THEN 'Inactivo' "
                query += "ELSE 'Desconocido' "
                query += "END AS estado "
                query += "FROM sitio A "
                query += "LEFT JOIN cliente B ON A.cliente_id = B.cliente_id "

                
                cursor.execute(query)
                data = cursor.fetchall()
                cursor.execute(f"SELECT CONCAT(nombre, ' ', app_pat,' ', ap_mat ) nombre, CONCAT(SUBSTRING_INDEX(nombre, ' ', 1), ' ', LEFT(app_pat, 1), '. ', ap_mat) username FROM usuario WHERE usuario_id={userid}")
                name = cursor.fetchone()

                # Consultar los clientes
                query_clientes = "SELECT cliente_id id, nombre FROM cliente WHERE estado = '0' "
                cursor.execute(query_clientes)
                data_clientes = cursor.fetchall()
            return render_template("site.html", data=data, name=name['nombre'], username=name['username'], data_clientes=data_clientes)
        except Exception as e:
            print(e)
            return redirect('/inicio')
        finally:
            if 'connection' in locals():
                connection.close()
    elif request.method == 'POST':
        try:
            connection = DataBase.get_db_connection()
            connection.begin() 
            with connection.cursor() as cursor:
                data = request.data
                json_data = json.loads(data)
                msge = ''
                http_code = 0
                cliente_id = 0
                
                params = [
                    json_data['client'], 
                    json_data['name'], 
                    json_data['location'], 
                    http_code, 
                    msge, 
                    cliente_id]
                cursor.callproc('create_site', params)
                cursor.execute("SELECT @_create_site_3 AS code, @_create_client_4 AS msge, @_create_client_5 AS clientid")
                result = cursor.fetchone()
                return jsonify({'code': result['code'], 'msge': result['msge']})
        except Exception as e:
            print(e)
            return redirect('/inicio')
        finally:
            if 'connection' in locals():
                connection.close()


@app.route('/sitio/masivo', methods=['GET', 'POST'])
def sitio_masivo():
    if request.method == 'GET':
        try:
            userid = session.get('userid')
            connection = DataBase.get_db_connection()
            connection.begin() 
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT CONCAT(nombre, ' ', app_pat,' ', ap_mat ) nombre, CONCAT(SUBSTRING_INDEX(nombre, ' ', 1), ' ', LEFT(app_pat, 1), '. ', ap_mat) username FROM usuario WHERE usuario_id={userid}")
                name = cursor.fetchone()
            return render_template("bulk_site_upload.html", name=name['nombre'], username=name['username'])
        except Exception as e:
                print(e)
                return redirect('/inicio')
        finally:
            if 'connection' in locals():
                connection.close()
    elif request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'code': 400, 'msge': 'No se seleccionó ningún archivo'})

        file = request.files['file']
        formato = request.form.get('formato')
        separador = request.form.get('separador')

        if file.filename == '':
            return jsonify({'code': 400, 'msge': 'Nombre de archivo vacío'})

        # Guardar el archivo temporalmente en /static/tmp
        file_path = os.path.join('static', 'tmp', file.filename)
        file.save(file_path)

        # Procesar el archivo dependiendo del formato
        if formato == 'csv' or formato == 'txt':
            try:
                # Leer el archivo Excel usando pandas
                clientes_sitios = pd.read_csv(file, sep=separador)

                # Normalización de df
                columnas = clientes_sitios.columns
                clientes_sitios.columns = clientes_sitios.columns.str.lower()

                # Renombrar columnas de clientes (solo las que existen)
                clientes_sitios = clientes_sitios.rename(columns={
                    "nombre cliente": "cli_nombre",
                    "razon social cliente": "cli_razon_social",
                    "contacto cliente": "cli_contacto",
                    "correo cliente": "cli_correo",
                    "rubro o detalle": "cli_detalle",
                    "fecha de cuando ingreso el cliente a redinnova (si se tiene)": "cli_fecha_ingreso",
                    "nombre del sitio (si se tiene mas de 1 sitio, repetir la fila)": "site_nombre",
                    "nombre del sitio": "site_detalle",
                    "ubicacion del sitio": "site_ubicacion"
                })

                # Crear un DataFrame con las columnas que contienen 'cli'
                if any('cli' in col for col in clientes_sitios.columns):
                    df_clientes = clientes_sitios.filter(like='cli')
                    # Eliminar clientes Duplicados
                    df_clientes = df_clientes.drop_duplicates()
                    try:
                        connection = DataBase.get_db_connection()
                        connection.begin() 
                        with connection.cursor() as cursor:
                            # Convertir el DataFrame en un JSON
                            clientes_json = df_clientes.to_json(orient='records')
                            # Llamar al procedimiento almacenado y pasar el JSON como parámetro
                            cursor.callproc('InsertarClientesMasivo', (clientes_json, 0))
                            cursor.execute("SELECT @_InsertarClientesMasivo_1 AS code")
                            result = cursor.fetchone()
                            if result['code'] == 200:
                                # Borrar el archivo temporalmente después del procesamiento
                                try:
                                    os.remove(file_path)
                                except OSError as e:
                                    return jsonify({
                                        'code': result['code'],
                                        'msge': f'Error al eliminar el archivo: {e}'
                                    })
                            return jsonify({'code': result['code']})
                    except Exception as e:
                        return redirect('/inicio')
                    finally:
                        if 'connection' in locals():
                            connection.close()
                else:
                    print("No se encontraron columnas con 'cli' en el nombre.")
                    return jsonify({'code': result['code'], 'msge': 'El archivo contiene columnas no validas.'})
            except Exception as e:
                print(f"Error procesando Excel: {e}")
                return jsonify(
                    {
                        'code': result['code'], 
                        'msge': 'Error procesando el archivo: '.format(e)
                    })

        elif formato == 'xlsx':
            try:
                # Leer el archivo Excel usando pandas
                clientes_sitios = pd.read_excel(file)

                # Normalización de df
                columnas = clientes_sitios.columns
                clientes_sitios.columns = clientes_sitios.columns.str.lower()

                # Renombrar columnas de clientes (solo las que existen)
                clientes_sitios = clientes_sitios.rename(columns={
                    "nombre cliente": "cli_nombre",
                    "razon social cliente": "cli_razon_social",
                    "contacto cliente": "cli_contacto",
                    "correo cliente": "cli_correo",
                    "rubro o detalle": "cli_detalle",
                    "fecha de cuando ingreso el cliente a redinnova (si se tiene)": "cli_fecha_ingreso",
                    "nombre del sitio (si se tiene mas de 1 sitio, repetir la fila)": "site_nombre",
                    "nombre del sitio": "site_detalle",
                    "ubicacion del sitio": "site_ubicacion"
                })

                # Crear un df con los id's de los clientes, para reemplazar el nombre del cliente x el id
                try:
                    connection = DataBase.get_db_connection()
                    connection.begin() 
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT cliente_id, nombre cli_nombre FROM cliente WHERE estado=0")
                        result = cursor.fetchall()

                    # Crear un DataFrame a partir de result
                    df_clientes_bdd = pd.DataFrame(result, columns=['cliente_id', 'cli_nombre'])

                    # Combinar las bases de datos por la columna cli_nombre
                    base_combinada = pd.merge(clientes_sitios, df_clientes_bdd, on='cli_nombre', how='outer')

                    base_combinada.rename(
                        columns= {
                            'cliente_id': 'site_cliente_id'
                        },
                        inplace=True
                    )

                    # Crear un DataFrame con las columnas que contienen 'sitio'
                    if any('site' in col for col in base_combinada.columns):
                        df_sitios = base_combinada.filter(like='site')
                        # Eliminar sitios Duplicados
                        df_sitios = df_sitios.drop_duplicates()
                        # Eliminar las filas que tengan valores nulos en las columnas 'site_nombre', 'site_detalle' y 'site_ubicacion'
                        df_sitios_clean = df_sitios[
                            (df_sitios['site_nombre'].str.len() >= 1) &
                            (df_sitios['site_detalle'].str.len() >= 1) &
                            (df_sitios['site_ubicacion'].str.len() >= 1)
                        ]

                        # Convertir el DataFrame en un JSON
                        sitios_json = df_sitios_clean.to_json(orient='records')
                        print("df to json: ", sitios_json)

                        try:
                            connection = DataBase.get_db_connection()
                            connection.begin() 
                            with connection.cursor() as cursor:
                                # Llamar al procedimiento almacenado y pasar el JSON como parámetro
                                cursor.callproc('InsertarSitiosMasivo', (sitios_json, 0))
                                cursor.execute("SELECT @_InsertarSitiosMasivo_1 AS code")
                                result = cursor.fetchone()
                                if result['code'] == 200:
                                    # Borrar el archivo temporalmente después del procesamiento
                                    try:
                                        os.remove(file_path)
                                    except OSError as e:
                                        return jsonify({
                                            'code': result['code'],
                                            'msge': f'Error al eliminar el archivo: {e}'
                                        })
                                    
                                return jsonify({'code': result['code']})
                        except Exception as e:
                            return redirect('/inicio')
                        finally:
                            if 'connection' in locals():
                                connection.close()


                        # try:
                        #     connection = DataBase.get_db_connection()
                        #     connection.begin() 
                        #     with connection.cursor() as cursor:
                        #         # Guardar el archivo temporalmente en /static/tmp
                        #         file_path_df = os.path.join('static', 'tmp', 'df_sitios.xlsx')
                               
                        #         # Eliminar las filas que tengan valores nulos en las columnas 'site_nombre', 'site_detalle' y 'site_ubicacion'
                        #         df_sitios_clean = df_sitios[
                        #             (df_sitios['site_nombre'].str.len() >= 1) &
                        #             (df_sitios['site_detalle'].str.len() >= 1) &
                        #             (df_sitios['site_ubicacion'].str.len() >= 1)
                        #         ]

                        #         df_sitios_clean.to_excel(file_path_df, index=False)

                        #         # Convertir el DataFrame en un JSON
                        #         sitios_json = df_sitios_clean.to_json(orient='records')
                        #         # Llamar al procedimiento almacenado y pasar el JSON como parámetro
                        #         cursor.callproc('InsertarSitiosMasivo', (sitios_json, 0))
                        #         cursor.execute("SELECT @_InsertarSitiosMasivo_1 AS code")
                        #         result = cursor.fetchone()
                        #         if result['code'] == 200:
                        #             # Borrar el archivo temporalmente después del procesamiento
                        #             try:
                        #                 os.remove(file_path)
                        #             except OSError as e:
                        #                 return jsonify({
                        #                     'code': result['code'],
                        #                     'msge': f'Error al eliminar el archivo: {e}'
                        #                 })
                        #         return jsonify({'code': result['cod888
                        # 
                    else:
                        print("No se encontraron columnas con 'cli' en el nombre.")
                        return jsonify({'code': result['code'], 'msge': 'El archivo contiene columnas no validas.'})

    
                       
                except Exception as e:
                    return redirect('/inicio')
                finally:
                    if 'connection' in locals():
                        connection.close()

                
            except Exception as e:
                print(f"Error procesando: {e}")
                return jsonify(
                    {
                        'code': result['code'], 
                        'msge': 'Error procesando el archivo Excel: '.format(e)
                    })
        
        else:
            result = {'code': 400, 'msge': 'Formato no soportado'}


@app.route('/soporte', methods=['GET', 'POST'])
def soporte():
        userid = session.get('userid')
        if request.method == 'GET':
            try:
                connection = DataBase.get_db_connection()
                connection.begin() 
                with connection.cursor() as cursor:
                    # Usuario
                    cursor.execute(f"SELECT CONCAT(nombre, ' ', app_pat,' ', ap_mat ) nombre, CONCAT(SUBSTRING_INDEX(nombre, ' ', 1), ' ', LEFT(app_pat, 1), '. ', ap_mat) username FROM usuario WHERE usuario_id={userid}")
                    name = cursor.fetchone()

                    # Clientes
                    query_clientes = "SELECT "
                    query_clientes += "cliente_id id, "
                    query_clientes += "nombre "
                    query_clientes += "FROM cliente WHERE estado = '0' "
                    cursor.execute(query_clientes)
                    data_clientes = cursor.fetchall()

                    # Sitios
                    query_sitios = "SELECT "
                    query_sitios += "sitio_id id, "
                    query_sitios += "cliente_id, "
                    query_sitios += "nombre "
                    query_sitios += "FROM sitio WHERE estado = '0' "
                    cursor.execute(query_sitios)
                    data_sitios = cursor.fetchall()

                    # Tecnicos
                    query_tecnicos = "SELECT "
                    query_tecnicos += "A.tecnico_id id, "
                    query_tecnicos += "CONCAT(B.nombre, ' ', B.app_pat, ' ', B.ap_mat, ' (', B.username, ')') nombre "
                    query_tecnicos += "FROM TECNICO A "
                    query_tecnicos += "LEFT JOIN USUARIO B ON A.usuario_id = B.usuario_id "
                    query_tecnicos += "WHERE A.estado = 0 "
                    cursor.execute(query_tecnicos)
                    data_tecnicos = cursor.fetchall()

                    # Soporte
                    query_soporte = "SELECT "
                    query_soporte += "A.soporte_id id, "
                    query_soporte += "B.nombre, "
                    query_soporte += "B.razon_social, "
                    query_soporte += "B.email, "
                    query_soporte += "C.nombre sitio, "
                    query_soporte += "C.ubicacion, "
                    query_soporte += "A.detalle_equipo, "
                    query_soporte += "A.detalle_trabajo, "
                    query_soporte += "CASE "
                    query_soporte += "WHEN ISNULL(A.quien_valida) THEN 'Sin usuario validador' "
                    query_soporte += "WHEN A.quien_valida IN (' ', '') THEN 'Sin usuario validador' "
                    query_soporte += "ELSE A.quien_valida "
                    query_soporte += "END usuario_validador, "
                    query_soporte += "A.fecha_inicio, "
                    query_soporte += "A.fecha_termino, "
                    query_soporte += "A.fecha_creacion, "
                    query_soporte += "A.estado, "
                    query_soporte += "CASE "
                    query_soporte += "WHEN  A.estado = '0' THEN 'Soporte terminado' "
                    query_soporte += "WHEN  A.estado = '1' THEN 'Reporte enviado' "
                    query_soporte += "ELSE 'En progreso' "
                    query_soporte += "END estado_format, "
                    query_soporte += "CASE "
                    query_soporte += "WHEN  A.estado = '0' THEN 'No se ha enviado el reporte.' "
                    query_soporte += "WHEN  A.estado = '1' THEN 'Reporte enviado. Se da por finalizado el proceso.' "
                    query_soporte += "ELSE 'En progreso' "
                    query_soporte += "END sub_estado, "
                    query_soporte += "CASE "
                    query_soporte += "WHEN  A.estado = '0' THEN 'text-bg-warning' "
                    query_soporte += "WHEN  A.estado = '1' THEN 'text-bg-success' "
                    query_soporte += "ELSE 'text-bg-danger' "
                    query_soporte += "END color_badge_sub_estado, "
                    query_soporte += "CASE "
                    query_soporte += "WHEN  A.estado = '0' THEN 'text-bg-success' "
                    query_soporte += "WHEN  A.estado = '1' THEN 'text-bg-success' "
                    query_soporte += "ELSE 'text-bg-danger' "
                    query_soporte += "END color_badge_estado "
                    query_soporte += "FROM soporte A "
                    query_soporte += "LEFT JOIN cliente B ON A.cliente_id=B.cliente_id "
                    query_soporte += "LEFT JOIN sitio C ON A.sitio_id=C.sitio_id; "
                    

                    cursor.execute(query_soporte)
                    data_soporte = cursor.fetchall()

                return render_template("support.html", data_soporte=data_soporte,  data_clientes=data_clientes, data_sitios=data_sitios, data_tecnicos=data_tecnicos, name=name['nombre'], username=name['username'])

            except Exception as e:
                print(e)
                return redirect('/inicio')
            finally:
                if 'connection' in locals():
                    connection.close()
        elif request.method == 'POST':

            blob_service_client = ConfigAzure.get_blob_service_client()
            userid = session.get('userid')
            container_name = ConfigAzure.get_container_name()
            container_client = blob_service_client.get_container_client(container_name)

            try:
                if not container_client.exists():
                    container_client.create_container()
            except Exception as e:
                return jsonify({
                    'code': 400, 
                    'msge': f'Error al crear el contenedor: {e}'
                })
            
            uploaded_urls = []

            # Obtener archivos
            files = request.files.getlist('files[]')

            print("Files: ", files)
            
            # Procesar cada archivo
            for file in files:
                if file:
                    try:
                        blob_client = container_client.get_blob_client(f"{userid}/{file.filename}")
                        blob_client.upload_blob(file, overwrite=True)
                        blob_url = f"https://storageredinnovastudent.blob.core.windows.net/{container_name}/{userid}/{file.filename}"
                        uploaded_urls.append(blob_url)
                    except Exception as e:
                        return jsonify({
                            'code': 400, 
                            'msge': f'Error al subir el archivo {file.filename}: {e}'
                        })
            
            # Obtener otros campos del formulario
            client = request.form.get('client')
            site = request.form.get('site')
            technicians = request.form.get('technicians')
            equipment_details = request.form.get('equipment_details')
            jobs_details = request.form.get('jobs_details')
            date_start = request.form.get('date_start')
            date_end = request.form.get('date_end')
            validator = request.form.get('validator')

            # Verificar si se subieron archivos
            if len(uploaded_urls) >= 1:
                # Crear lista de diccionarios para el DataFrame
                data = []
                for url in uploaded_urls:
                    data.append({
                        'usuario_id': userid, 
                        'cliente_id': client,
                        'sitio_id': site,
                        'url': url,
                        'contenedor_nombre': container_name
                    })
                
                # Crear el DataFrame
                df = pd.DataFrame(data)

                # Convertir el DataFrame en un JSON
                archivos_json = df.to_json(orient='records')

                print("Archivos en json: ", archivos_json)
                print("Cliente: ", client)
                print("Site: ", site)
                print("Tecnico: ", technicians)
                print("Equipamento: ", equipment_details)
                print("Trabajos: ", jobs_details)
                print("Fecha inicio: ", date_start)
                print("Fecha termino: ", date_end)
                print("Usuario validador: ", validator)

                try:
                    connection = DataBase.get_db_connection()
                    connection.begin() 
                    with connection.cursor() as cursor:
                        # Llamar al procedimiento almacenado y pasar el JSON como parámetro
                        cursor.callproc('InsertarEvidenciaSoporte', (archivos_json, client, site, technicians, equipment_details, jobs_details,validator, date_start, date_end, 0, ''))
                        cursor.execute("SELECT @_InsertarEvidenciaSoporte_9 AS code, @_InsertarEvidenciaSoporte_10 AS msge")
                        result = cursor.fetchone()

                        return jsonify({'code': result['code'], 'msge': result['msge']})
                except Exception as e:
                    return redirect('/inicio')
                finally:
                    if 'connection' in locals():
                        connection.close()



@app.route('/public/soporte', methods=['GET', 'POST'])
def public_soporte():
    if request.method == 'GET':
        try:
            connection = DataBase.get_db_connection()
            connection.begin() 
            with connection.cursor() as cursor:
                # Clientes
                query_clientes = "SELECT "
                query_clientes += "cliente_id id, "
                query_clientes += "nombre "
                query_clientes += "FROM cliente WHERE estado = '0' "
                cursor.execute(query_clientes)
                data_clientes = cursor.fetchall()

                # Sitios
                query_sitios = "SELECT "
                query_sitios += "sitio_id id, "
                query_sitios += "cliente_id, "
                query_sitios += "nombre "
                query_sitios += "FROM sitio WHERE estado = '0' "
                cursor.execute(query_sitios)
                data_sitios = cursor.fetchall()

                # Tecnicos
                query_tecnicos = "SELECT "
                query_tecnicos += "A.tecnico_id id, "
                query_tecnicos += "CONCAT(B.nombre, ' ', B.app_pat, ' ', B.ap_mat, ' (', B.username, ')') nombre "
                query_tecnicos += "FROM TECNICO A "
                query_tecnicos += "LEFT JOIN USUARIO B ON A.usuario_id = B.usuario_id "
                query_tecnicos += "WHERE A.estado = 0 "
                cursor.execute(query_tecnicos)
                data_tecnicos = cursor.fetchall()

                
                return render_template('public_support.html', data_clientes=data_clientes, data_sitios=data_sitios, data_tecnicos=data_tecnicos)
        except Exception as e:
            return redirect('/')
        finally:
            if 'connection' in locals():
                connection.close()

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html')
    elif request.method == 'POST':
        return
    else:
        return  



if __name__ == '__main__':
    Config.config(app)