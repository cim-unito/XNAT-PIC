from dataclasses import dataclass, field
from typing import List, Optional

from xnat_client.xnat_manager import XnatManager


@dataclass
class NewProjectData:
    title: str = ""
    project_id: str = ""
    editable_id: bool = False
    access_status: str = "private"  # private / protected / public
    description: str = ""
    keywords: List[str] = field(default_factory=list)
    selected_investigator: Optional[str] = None  # string tipo "Name,Surname"


class ModelXnatNewProject:
    """
    Model per la creazione di un nuovo progetto XNAT.
    Tiene i dati e chiama XnatManager per le operazioni remote.
    """

    def __init__(self):
        self._data = NewProjectData()

    # ----------------------
    # PROPERTIES
    # ----------------------
    @property
    def data(self) -> NewProjectData:
        return self._data

    # ----------------------
    # INVESTIGATORS
    # ----------------------
    def load_investigators(self):
        """
        Ritorna lista di stringhe "firstname,lastname" per popolazione dropdown.
        """
        investigators = XnatManager.list_investigators()
        result: List[str] = []
        for inv in investigators:
            fn = inv.get("firstname")
            ln = inv.get("lastname")
            if fn and ln:
                result.append(f"{fn},{ln}")
        return result

    def add_investigator(
        self,
        firstname: str,
        lastname: str,
        institution: str,
        email: str,
    ):
        """
        Crea un nuovo investigator e ritorna di nuovo la lista stringhe.
        """
        XnatManager.create_investigator(firstname, lastname, institution, email)
        return self.load_investigators()

    # ----------------------
    # PROJECT CREATION
    # ----------------------
    def create_project(self):
        """
        Usa XnatManager per creare il progetto su XNAT.
        """
        d = self._data

        title = (d.title or "").strip()
        project_id = (d.project_id or "").strip()

        if not title:
            raise ValueError("Project title is required.")
        if not project_id:
            raise ValueError("Project ID is required.")
        if " " in project_id:
            raise ValueError("Project ID cannot contain spaces.")

        access = (d.access_status or "private").lower()
        if access not in ("private", "protected", "public"):
            raise ValueError(f"Invalid access level: {access}")

        project = XnatManager.create_project(
            project_id=project_id,
            title=title,
            description=(d.description or "").strip(),
            keywords=d.keywords,
            access_status=access,
            investigator=d.selected_investigator,
        )
        return project
