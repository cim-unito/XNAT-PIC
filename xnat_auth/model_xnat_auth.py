from database.xnat_credential_dao import XnatCredentialDao


class ModelXnatAuth:
    def persist_credentials(self, address, username, password, remember):
        """Save or clear credentials depending on the remember flag."""
        if remember:
            XnatCredentialDao.delete_credential()
            XnatCredentialDao.insert_new_credential(
                address,
                username,
                password,
                remember,
            )
        else:
            XnatCredentialDao.delete_credential()

    def load_remembered_credential(self):
        """Return the first remembered credential, if any."""
        for cred in XnatCredentialDao.get_all_credentials():
            if cred.remember:
                return cred
        return None
