from database.xnat_credential_dao import XnatCredentialDao


class ModelXnatAuth:
    def __init__(self):
        self.credentials = XnatCredentialDao.get_all_credentials()

    def insert_new_credential(self, address, username, password, remember):
        XnatCredentialDao.delete_credential()
        XnatCredentialDao.insert_new_credential(address, username, password,
                                                remember)

    def delete_credential(self):
        XnatCredentialDao.delete_credential()

    def load_remembered_credential(self):
        for cred in self.credentials:
            if cred.remember:
                return cred
        return None