from database.xnat_credential_dao import XnatCredentialDao


class ModelXnatAuth:
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
        credentials = XnatCredentialDao.get_remembered_credential()
        return credentials
