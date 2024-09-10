from flask_cors import CORS
import hashlib
import pymysql.cursors
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta


class Config:
    @staticmethod
    def config(app):
        app.secret_key = 'b1f21c5f7e90b9e6d3c3b12d916c6c82a8c0a72c97bdf8c918e3028b73cbb9a5'
        CORS(app)
        app.config['DEBUG'] = False
        app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
        app.run(debug=app.config['DEBUG'])

    
class Utils:
    @staticmethod
    def encryptSHA256(code):
        string_bytes = code.encode('utf-8')
        sha256_hash = hashlib.sha256()
        sha256_hash.update(string_bytes)
        hash_encriptado = sha256_hash.hexdigest()
        return hash_encriptado
            
class DataBase:
    @staticmethod
    def get_db_connection():
        return pymysql.connect(
            host='dev-red-innova.mysql.database.azure.com',
            user='sofiadonoso',
            password='Sda.280899$',
            database='gestion-ot-red-innova',
            cursorclass=pymysql.cursors.DictCursor,
            ssl_ca='static/base/DigiCertGlobalRootCA.crt.pem')
    
class ConfigAzure:
    @staticmethod
    def get_blob_service_client():
        # Configura la conexión con Azure Blob Storage
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING') 
        return BlobServiceClient.from_connection_string(connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING'))

    @staticmethod
    def get_container_name():
        return "gestion-ot"
    
    @staticmethod
    def generate_sas_url(container_name, blob_name):
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        # Crear el BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING'))
        # Generar SAS token
        sas_token = generate_blob_sas(
            account_name=blob_service_client.account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),  # Permiso de lectura
            expiry=datetime.utcnow() + timedelta(hours=1)  # Expira en 1 hora
        )
        # Crear URL con SAS
        blob_url_with_sas = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
        return blob_url_with_sas
    
    def extract_blob_name(url, container_name):
    # Eliminar el esquema y dominio
        path = url.split(f'https://storageredinnovastudent.blob.core.windows.net/{container_name}/')[1]
        
        return path
