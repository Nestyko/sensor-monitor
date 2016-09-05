from config import load_config, save_data
import getpass
import requests


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

config = load_config() 
lang = config['lang']

class Authentication:

    def __init__(self):
        
        self.email = config['email']
        self.password = config['password']
        self.jwt = None
        if 'jwt' in config and 'token' in config['jwt']:
            self.jwt = config['jwt']['token']
        self.is_auth = False
        if self.jwt and self.jwt != '':
            #Validate jwt
            self.is_auth = True
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
            s = requests.Session()
            res = s.post(config['base_url']+'/auth/login', data=user, timeout=5)
        except TimeoutError:
            print(timeout_error_message[lang])
        except Exception:
            print(connection_error_message[lang])
        if(res.status_code == 200):
            jwt_res = s.get(config['base_url']+'/user/jwt')
            self.jwt = jwt_res.json()
            save_data(self.jwt, res.json()['id'])
            return res.json()
        return False
    

    def user_id(self):
        if not self.auth:
            return None
        return self.auth['id']
