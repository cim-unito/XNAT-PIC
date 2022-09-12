# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 11:18:01 2018

@author: Sara Zullino
"""
from pydicom import datadict
import pydicom.encoders.gdcm
import pydicom.encoders.pylibjpeg

def add_cest_dict():
    # CEST acquisition
    # Create new tag entries
    new_dict_items = {
        0x10610010: ("LO", "1", "CEST Parameters Creator", "", "Creator"),  # (data type, multiplicity, tag displayed name, tag keyword)
        0x10611001: ("LO", "1", "Chemical Exchange Saturation Type", "", "ChemicalExchangeSaturationType"),
        0x10611002: ("LO", "1", "Saturation Type", "", "SaturationType"),
        0x10611003: ("LO", "1", "Pulse Shape", "", "PulseShape"),
        0x10611004: ("DS", "1", "B1 Saturation (μT)", "", "B1Saturation"),
        0x10611005: ("DS", "1", "Pulse Length (ms)", "", "PulseLength"),
        0x10611006: ("DS", "1", "Pulse Number", "", "PulseNumber"),
        0x10611007: ("DS", "1", "Interpulse Delay", "", "InterpulseDelay"),
        0x10611008: ("DS", "1", "Saturation Length (ms)", "", "SaturationLength"),
        0x10611009: ("DS", "1", "Readout Time", "", "ReadoutTime"),
        0x10611010: ("DS", "1", "Pulse Length 2 (ms)", "", "PulseLength2"),
        0x10611011: ("DS", "1", "Duty Cycle", "", "DutyCycle"),
        0x10611012: ("DS", "1", "Recovery Time (ms)", "", "RecoveryTime"),
        0x10611013: ("DS", "1", "Measurement Number", "", "MeasurementNumber"),
        0x10611014: ("DS", "1", "Saturation Offset (Hz)", "", "SaturationOffsetHz"),
        0x10611015: ("DS", "1", "Saturation Offset (ppm)", "", "SaturationOffsetPpm"),

    }

    # Update the dictionary itself
    datadict.DicomDictionary.update(new_dict_items)

    # Update the reverse mapping from name to tag
    new_names_dict = dict([(val[4], tag) for tag, val in new_dict_items.items()])

    datadict.keyword_dict.update(new_names_dict)
    
def codify_cest_dict(private_creator):

    dict_items = {
        # tag: (VR, VM, description, is_retired)
        0x10610010: ("LO", "1", "CEST Parameters Creator", ""), 
        0x10611001: ("LO", "1", "Chemical Exchange Saturation Type", ""),
        0x10611002: ("LO", "1", "Saturation Type", ""),
        0x10611003: ("LO", "1", "Pulse Shape", ""),
        0x10611004: ("DS", "1", "B1 Saturation (μT)", ""),
        0x10611005: ("DS", "1", "Pulse Length (ms)", ""),
        0x10611006: ("DS", "1", "Pulse Number", ""),
        0x10611007: ("DS", "1", "Interpulse Delay", ""),
        0x10611008: ("DS", "1", "Saturation Length (ms)", ""),
        0x10611009: ("DS", "1", "Readout Time", ""),
        0x10611010: ("DS", "1", "Pulse Length 2 (ms)", ""),
        0x10611011: ("DS", "1", "Duty Cycle", ""),
        0x10611012: ("DS", "1", "Recovery Time (ms)", ""),
        0x10611013: ("DS", "1", "Measurement Number", ""),
        0x10611014: ("DS", "1", "Saturation Offset (Hz)", ""),
        0x10611015: ("DS", "1", "Saturation Offset (ppm)", ""),

    }

    datadict.add_private_dict_entries(private_creator, dict_items)