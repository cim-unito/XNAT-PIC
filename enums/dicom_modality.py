from enum import Enum

class DicomModality(Enum):
    CT = "CT"  # Computed Tomography
    MR = "MR"  # Magnetic Resonance
    OI = "OI"  # Optical Imaging (non standard Modality)
    OT = "OT"  # Other
    PAI = "PAI"  # Photoacoustic Imaging (non standard Modality)
    PT = "PT"  # Positron Emission Tomography (PET)
    US = "US"  # Ultrasound

    def __str__(self) -> str:
        return self.value
