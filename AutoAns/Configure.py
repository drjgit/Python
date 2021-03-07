import configparser


class ConfigManger():
    cgf = None
    user_name = ''
    pass_word = ''

    def __init__(self):
        self.cfg = configparser.ConfigParser()
        self.cfg.read('config.cfg')
        section = self.cfg.sections()
        if (section):
            self.user_name = self.cfg.get('Admin','Username')
            self.pass_word = self.cfg.get('Admin','Password')
        else:
            self.cfg.add_section("Admin")
            self.cfg.set('Admin','Username','')
            self.cfg.set('Admin','Password','')

    def Save(self):
        with open('config.cfg','wb') as of:
            self.cfg.write(of)

    def get_username(self):
        return self.user_name

    def get_password(self):
        return self.pass_word

    def set_username(self,username):
        self.cfg.set('Admin','Username',username)
    
    def set_password(self,password):
        self.cfg.set('Admin','Password',password)