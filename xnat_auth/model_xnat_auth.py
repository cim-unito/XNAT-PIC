from database.xnat_credential_dao import XnatCredentialDao


class ModelXnatAuth:
    def __init__(self):
        self.credentials = XnatCredentialDao.get_all_credentials()

    def persist_credentials(self, address, username, password, remember):
        """Save or clear credentials depending on the remember flag."""
        if remember:
            XnatCredentialDao.clear_credentials()
            XnatCredentialDao.replace_credentials(
                address,
                username,
                password,
                remember,
            )
        else:
            XnatCredentialDao.clear_credentials()

    def load_remembered_credential(self):
        """Return the first remembered credential, if any."""
        for cred in self.credentials:
            if cred.remember:
                return cred
        return None
