  <a href="https://www.eurobioimaging.eu/">
    <img src="assets/images/Eubi.jpg" alt="Logo" width="500"/>
  </a>

---

# XNAT-PIC

XNAT for Preclinical Imaging Centers (XNAT-PIC) is a free and open-source Windows desktop application, which offers several tools to expand the XNAT core functionalities to support
the preclinical imaging community and to promote open science practices.

---

## Table of Contents
- [Overview](#overview)
- [Main Features](#main-features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Run the App](#run-the-app)
- [Releases](#releases)
- [Roadmap](#roadmap)
- [License](#license)
- [Citation](#citation)
- [News](#news)
- [Contact](#contact)
- [Funding](#funding)
- [Acknowledgments](#acknowledgments)

---

## Overview

<img src="assets/images/Workflow.png" width="750" title="XNAT-PIC workflow" alt="XNAT-PIC workflow">

Schematic view. (A) XNAT-PIC converts to DICOM multimodal images from several vendors, uploads, and annotates
preclinical images to the XNAT server. (B) Datasets can be processed via containerized workflows in XNAT. (C) Custom
plugins introduce new data types for optical and optoacoustic imaging, enabling users to upload, organize, and view
these images directly in XNAT.

---

## Main Features

### 1) XNAT-PIC Converter
Converts raw imaging data from MRI (Bruker) and Optical Imaging (IVIS) systems into the DICOM format.

### 2) Uploader
Uploads DICOM datasets to an XNAT instance, supporting workflows at the project, subject, and experiment levels.
The uploader also enables the management of imaging modalities not natively supported by XNAT, such as optical imaging and photoacoustic imaging.
### 3) Grouping Annotation Interface
Provides an interface to efficiently cope with different experimental protocols by labelling subjects with dedicated Custom Forms to manage several types of cohorts (e.g. treated/untreated, timepoints, doses, etc..)

---

## Architecture

The app is a Python desktop application built with **Flet** and organized in modules:
- `converter/` for conversion workflows
- `uploader/` for XNAT upload workflows
- `custom_form/` for metadata annotation
- `xnat_client/` for XNAT API integration

Entry point: `main.py`.

---

## Requirements

Python dependencies are listed in [`requirements.txt`](requirements.txt):
- `flet`
- `numpy`
- `pydicom`
- `pillow`
- `xnat`
- `python-dateutil`
 
---

## Run the App

From the repository root:

```bash
python main.py
```

This launches the desktop UI via Flet.

---

## Releases
You can download stable and pre-release builds from the GitHub Releases page:

- **Latest release notes:** [v2.1-beta.0](https://github.com/FGamma/XNAT-PIC/releases/tag/v2.1-beta.0)
- **Direct MSI download (Windows):** [XNAT-PIC-2.1-beta.0.msi](https://github.com/FGamma/XNAT-PIC/releases/download/v2.1-beta.0/XNAT-PIC-2.1-beta.0.msi)
- **All releases:** [GitHub Releases](https://github.com/FGamma/XNAT-PIC/releases)


## Roadmap

See [open issues](https://github.com/FGamma/XNAT-PIC/issues) for planned features and known issues.

---

## License

XNAT-PIC is distributed under the terms of the GNU General Public License (GPL) v3 or later.
See [`LICENSE.md`](LICENSE.md) for details.

---

## Citation

If you use XNAT-PIC in your work, please cite:

- S. Zullino, A. Paglialonga, W. Dastrù, D. L. Longo, S. Aime. *XNAT-PIC: Extending XNAT to Preclinical Imaging Centers*, 2021. DOI/Preprint: https://arxiv.org/abs/2103.02044

---

## News

* "Demonstrator 5: XNAT-PIC: expanding XNAT for image archiving and processing to Preclinical Imaging Centers". EOSC-Life website, https://www.eosc-life.eu/d5/

* "Towards sharing and reusing of preclinical image data". Euro-Bioimaging website, https://www.eurobioimaging.eu/news/towards-sharing-and-reusing-of-preclinical-image-data/

* "Data Management: Biological and Preclinical Imaging Perspective". Euro-Bioimaging Virtual Pub, February 12th, 2021. <br>
[![](https://img.youtube.com/vi/QNiAGuFk53w/0.jpg)](https://youtu.be/QNiAGuFk53w "")

* "XNAT-PIC: expanding XNAT for image archiving and processing to Preclinical Imaging Centers". Demonstrator 5 from Populating EOSC-Life: Success stories for the Demonstrators – Session 1 from January 13, 2021.<br>
[![](https://img.youtube.com/vi/cpEcfIJJqCo/0.jpg)](https://youtu.be/cpEcfIJJqCo "")

---

## Contact

**Francesco Gammaraccio**  
Molecular Imaging Center  
Department of Molecular Biotechnology and Health Sciences  
Via Nizza 52 | 10126 Torino, Italy  
francesco.gammaraccio@unito.it | T +39 011 670 6473

<a href="https://en.unito.it/">
  <img src="assets/images/UnitoLogo.jpg" alt="Università di Torino logo" width="220"/>
</a>

**Kranthi Thej Kandula**  
Molecular Imaging Center  
Department of Molecular Biotechnology and Health Sciences  
Via Nizza 52 | 10126 Torino, Italy  
kranthithej.kandula@unito.it | T +39 011 670 6473

<a href="https://en.unito.it/">
  <img src="assets/images/UnitoLogo.jpg" alt="Università di Torino logo" width="220"/>
</a>

---
 
## Funding

European Union’s Horizon 2020 / Horizon Europe programmes under grant agreements:
- #824087 (EOSC-Life)
- #965345 (HealthyCloud)
- #101058427 (EOSC4Cancer)
- #1011100633 (EUCAIM)

<a href="https://www.eosc-life.eu/">
  <img src="assets/images/Eosc.png" alt="EOSC-Life logo" width="100"/>
</a>

<a href="https://healthycloud.eu/">
  <img src="assets/images/HealthyCloud.jpg" alt="HealthyCloud logo" width="200"/>
</a>

<a href="https://eosc4cancer.eu/"> 
  <img src="assets/images/eosc4cancer.png" alt="EOSC4Cancer logo" width="250"/>
</a>

<a href="https://eucanimage.eu/">
  <img src="assets/images/Eucaim.png" alt="EUCAIM logo" width="200"/>
</a>

---

## Acknowledgments

- Alessandro Paglialonga: https://github.com/pagli17
- Stefan Klein, Hakim Achterberg and Marcel Koek — Biomedical Imaging Group Rotterdam, Erasmus Medical Center, Rotterdam
- Matteo Caffini, "Project-Beat--Python": https://github.com/mcaffini/Project-Beat---Python
- Sara Zullino: https://github.com/szullino
