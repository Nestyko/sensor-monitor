from config import load_config, save_data
import getpass
import requests
import json


no_auth_info_message = {
    'spa': 'Informacion de usuario no administrada por favor ingrese correo y contraseña',
    'eng': 'User information not provided please enter email and password'
}

email_input_message = {
    'spa': 'Correo: ',
    'eng': 'E-mail: '
}

password_input_message = {
    'spa': 'Contraseña (No sera visible):',
    'eng': "Password (won't be visible): "
}

timeout_error_message = {
    'spa': 'Tiempo de espera de respuesta agotado',
    'eng': 'Timeout waiting for response'
}

connection_error_message = {
    'spa': "Error de Conexion",
    'eng': 'Connection error'
}

email_not_registered_message = {
    'spa': 'Correo no registrado',
    'eng': 'Email not registered'
}

password_error_message = {
    'spa': 'Contraseña invalida',
    'eng': 'Wrong password'
}

welcome_message = {
    'spa': 'Bienvenido',
    'eng': 'Welcome'
}

admin_groups_error_message = {
    'spa': 'Error obteniendo los grupos',
    'eng': 'Error getting the groups'
}

config = load_config() 
lang = config['lang']

class Authentication:

    def __init__(self):
        self.id = None
        if 'user_id' in config:
            self.id = config['user_id']
        self.email = None
        if 'email' in config:
            self.email = config['email']
        self.password = None
        if 'password' in config:
            self.password = config['password']
        self.s = requests.Session()
        self.jwt = None
        if 'jwt' in config and 'token' in config['jwt']:
            self.jwt = config['jwt']['token']
        self.is_auth = False
        if self.jwt and self.jwt != '':
            #Validate jwt
            res = self.s.get(config['base_url']+'/user/'+str(self.id))
            if res.status_code == 403:
                #Renew jwt
                self.promp_login()
            elif res.status_code >= 400:
                print('error on authentication')
                quit()
            elif res.status_code < 400:
                self.is_auth = True
                self.s.headers.update({'access_token': self.jwt})
        else:
            self.promp_login()

    def greetings(self, lang='spa'):
        return welcome_message[lang] + " " + self.email


    def promp_login(self):
        if self.email == '' or self.password == '':
            print(no_auth_info_message[lang])
            self.email = input(email_input_message[lang])
        while not self.is_auth:
            while not self.is_email_registered():
                print(email_not_registered_message[lang])
                self.email = input(email_input_message[lang])	
            
            self.auth = self.login()
            if self.auth:
                self.is_auth = True
            else:
                print(password_error_message[lang])
                self.password = getpass.getpass(password_input_message[lang])
        print(self.greetings(lang=lang))
    
    def is_email_registered(self):
        res = None
        try:
            res = requests.get(config['base_url']+'/auth', params={"email":self.email}, timeout=5)
        except TimeoutError: 
            print(timeout_error_message[lang])
        except Exception:
            print(connection_error_message[lang])
        if res and len(res.json()) > 0:
            return True
        return False

    def login(self):
        if not self.is_email_registered():
            return False
        try:
            user = {
                'email': self.email,
                'password': self.password
            }
            res = self.s.post(config['base_url']+'/auth/login', data=user, timeout=5)
        except TimeoutError:
            print(timeout_error_message[lang])
            return False
        except Exception:
            print(connection_error_message[lang])
            return False
        if(res.status_code == 200):
            self.id = res.json()['id']
            jwt_res = self.s.get(config['base_url']+'/user/jwt')
            jwt = jwt_res.json()
            self.s.headers.update({'access_token': jwt['token']})
            save_data(jwt, self.id)
            self.jwt = jwt
            return res.json()
        return False
    

    def getAdminGroups(self):
        if not self.id:
            print('Error no id found for the user, please login first')
            return []
        res = self.s.get(config['base_url']+'/grouppermission', params={'user': self.id})
        if res.status_code != 200:
            return []
        groups = res.json()
        admin_groups = [ g['group'] for g in groups if g['permissions'] and 'admin' in g['permissions']]
        return admin_groups
        print(groups)
        return groups


