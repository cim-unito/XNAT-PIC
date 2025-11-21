from __future__ import annotations

from typing import Optional, List, Dict
import xnat
import requests


class XnatManager:
    _instance: Optional["XnatManager"] = None

    # ---------------------------------------------------------
    # COSTRUTTORE
    # ---------------------------------------------------------
    def __init__(self, address: str, username: str, password: str):
        self.address = address.rstrip("/")
        self.username = username
        self.password = password
        self.session: Optional[xnat.session.Session] = None

    # ---------------------------------------------------------
    # CONNESSIONE
    # ---------------------------------------------------------
    def connect(self) -> bool:
        try:
            self.session = xnat.connect(self.address, self.username, self.password)
            XnatManager._instance = self
            return True
        except Exception as e:
            print("XNAT connection error:", e)
            self.session = None
            return False

    def disconnect(self):
        if self.session:
            try:
                self.session.disconnect()
            except:
                pass

        self.session = None
        if XnatManager._instance is self:
            XnatManager._instance = None

    # ---------------------------------------------------------
    # STATIC SESSION CONTROL
    # ---------------------------------------------------------
    @staticmethod
    def start_session(address: str, username: str, password: str) -> bool:
        if XnatManager._instance:
            XnatManager._instance.disconnect()

        mgr = XnatManager(address, username, password)
        return mgr.connect()

    @staticmethod
    def disconnect_global():
        if XnatManager._instance:
            XnatManager._instance.disconnect()

    @staticmethod
    def has_active_session() -> bool:
        return (
            XnatManager._instance is not None
            and XnatManager._instance.session is not None
        )

    @staticmethod
    def get_session():
        return (
            XnatManager._instance.session
            if XnatManager._instance
            else None
        )

    # ---------------------------------------------------------
    # LIST PROJECTS
    # ---------------------------------------------------------
    @staticmethod
    def _safe_label(obj, fallback: str):
        for a in ("label", "name"):
            if hasattr(obj, a):
                v = getattr(obj, a)
                if v:
                    return v
        return fallback

    @staticmethod
    def list_projects():
        s = XnatManager.get_session()
        if not s:
            raise RuntimeError("No active session")

        projs = []
        for pid, proj in s.projects.items():
            projs.append({
                "id": pid,
                "label": XnatManager._safe_label(proj, pid)
            })
        return projs

    # ---------------------------------------------------------
    # LIST SUBJECTS
    # ---------------------------------------------------------
    @staticmethod
    def list_subjects(project_id: str) -> List[Dict[str, str]]:
        s = XnatManager.get_session()
        if not s:
            raise RuntimeError("No active session")

        if project_id not in s.projects:
            raise ValueError(f"Project '{project_id}' not found")

        proj = s.projects[project_id]
        subjects = []

        for sid, sub in proj.subjects.items():
            label = XnatManager._safe_label(sub, sid)
            real_id = getattr(sub, "id", sid)
            subjects.append({"id": real_id, "label": label})

        return subjects

    # ---------------------------------------------------------
    # LIST EXPERIMENTS
    # ---------------------------------------------------------
    @staticmethod
    def list_experiments(project_id: str, subject_id: str) -> List[Dict[str, str]]:
        s = XnatManager.get_session()
        if not s:
            raise RuntimeError("No active session")

        if project_id not in s.projects:
            raise ValueError(f"Project '{project_id}' not found")

        proj = s.projects[project_id]

        # subject_id may be label or real id
        subj = proj.subjects.get(subject_id)
        if subj is None:
            for s2 in proj.subjects.values():
                if getattr(s2, "id", None) == subject_id:
                    subj = s2
                    break

        if subj is None:
            raise ValueError(
                f"Subject '{subject_id}' not found in project '{project_id}'"
            )

        exps = []
        for eid, exp in subj.experiments.items():
            label = XnatManager._safe_label(exp, eid)
            real_id = getattr(exp, "id", eid)
            exps.append({"id": real_id, "label": label})

        return exps

    # ---------------------------------------------------------
    # REST WRAPPER (Basic Auth)
    # ---------------------------------------------------------
    @staticmethod
    def _rest(method: str, url: str, json: dict = None):
        inst = XnatManager._instance
        if not inst or not inst.session:
            raise RuntimeError("No active session")

        resp = requests.request(
            method=method,
            url=url,
            json=json,
            auth=(inst.username, inst.password),
            verify=False  # per SSL self-signed
        )

        if resp.status_code >= 400:
            raise RuntimeError(
                f"{method} {url} failed: {resp.status_code} {resp.text}"
            )

        return resp

    # ---------------------------------------------------------
    # CREATE PROJECT (FINAL + STABLE)
    # ---------------------------------------------------------
    @staticmethod
    def create_project(
        project_id: str,
        title: str,
        description: str = "",
        keywords: List[str] | None = None,
        access_status: str = "private",
        investigator: str | None = None,
    ):
        inst = XnatManager._instance
        s = inst.session if inst else None
        if not s:
            raise RuntimeError("No active XNAT session")

        project_id = project_id.strip()
        title = title.strip()

        if not project_id:
            raise ValueError("Project ID required")
        if " " in project_id:
            raise ValueError("Project ID cannot contain spaces")
        if not title:
            raise ValueError("Project title required")

        access_status = access_status.lower().strip()
        if access_status not in ("private", "protected", "public"):
            raise ValueError("Invalid access level")

        base = inst.address
        url_project = f"{base}/data/projects/{project_id}"

        # 1) CREATE PROJECT
        XnatManager._rest("PUT", url_project)

        # 2) METADATA
        payload = {
            "name": title,
            "secondary_ID": title,
            "description": description,
            "keywords": ",".join(keywords or []),
            "accessibility": access_status,
        }

        if investigator:
            parts = [p.strip() for p in investigator.split(",")]
            if len(parts) >= 2:
                payload["pi_firstname"] = parts[0]
                payload["pi_lastname"] = parts[1]

        XnatManager._rest("POST", url_project, json=payload)

        return {"id": project_id, "label": title}

    # ---------------------------------------------------------
    # INVESTIGATORS
    # ---------------------------------------------------------
    @staticmethod
    def list_investigators():
        inst = XnatManager._instance
        if not inst or not inst.session:
            raise RuntimeError("No active session")

        url = f"{inst.address}/data/investigators?format=json"

        try:
            resp = XnatManager._rest("GET", url)
            data = resp.json()
            rows = data.get("ResultSet", {}).get("Result", [])

            out = []
            for r in rows:
                fn = r.get("firstname") or r.get("xnat_investigatorData/firstname")
                ln = r.get("lastname") or r.get("xnat_investigatorData/lastname")
                if fn and ln:
                    out.append({"firstname": fn, "lastname": ln})

            return out
        except:
            return []

    @staticmethod
    def create_investigator(firstname: str, lastname: str,
                            institution: str = "", email: str = ""):

        inst = XnatManager._instance
        url = f"{inst.address}/data/investigators"

        payload = {
            "firstname": firstname.strip(),
            "lastname": lastname.strip(),
            "institution": institution.strip(),
            "email": email.strip(),
        }

        XnatManager._rest("POST", url, json=payload)
