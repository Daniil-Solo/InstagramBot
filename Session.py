from Master import Master


class Session:
    def __init__(self, parameters, browser):
        self._parameters = parameters
        self._browser = browser
        self.potential_clients = None

    def generate_potential_clients(self):
        master_name, master_status, message = self.get_master()
        if not master_status:
            return False, message

        master = Master(name=master_name, browser=self._browser)
        potential_clients, potential_clients_status, message = master.get_potential_clients(self._parameters)
        if not potential_clients_status:
            return False, message
        
        self.potential_clients = potential_clients
        return True, ""

    def like_generated_users(self):
        pass

    def get_master(self):
        pass
