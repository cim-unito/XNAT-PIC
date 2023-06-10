# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 10:40:47 2018

@author: Sara Zullino
"""

"""
Read Bruker visu_pars file.

Returns a dictionary of paramaters.

Adapted from Matteo Caffini
"""
import re
import numpy as np
import datetime

month_mapping = {
        'January': 1,
        'Jan': 1,
        'February': 2,
        'Feb': 2,
        'March': 3,
        'Mar': 3,
        'April': 4,
        'Apr': 4,
        'May': 5,
        'June': 6,
        'Jun': 6,
        'July': 7,
        'Jul': 7,
        'August': 8,
        'Aug': 8,
        'September': 9,
        'Sep': 9,
        'October': 10,
        'Oct': 10,
        'November': 11,
        'Nov': 11,
        'December': 12,
        'December': 12
        }


def read_visupars_parameters(filename):

    file_ID = open(filename, "r")
    C = file_ID.read()
    file_ID.close()

    C = re.sub("\$\$([^\n]*)\n", "", C)
    C = re.split("\s*##", C)
    C.remove("")

    parameters = {"_extra": []}
    orig = {"_extra": []}

    for ii in range(len(C)):
        parameter_line = C[ii]
        splitter = re.search("=", parameter_line)

        # process parameter name
        name = parameter_line[: splitter.start()]
        if "$" in name:
            name = name.replace("$", "")
        else:
            pass

        # process parameter value
        value = parameter_line[splitter.end() :]
        orig[name] = value

        if "\n" not in value:
            try:
                value = float(value)
                if round(value) == value:
                    value = int(value)
                else:
                    pass
            except:
                try:
                    value = int(value)
                except:
                    pass
        else:
            splitter = re.search("\n", value)
            first_part = value[: splitter.start()]
            second_part = value[splitter.end() :]

            first_part = first_part.replace(" ", "")
            first_part = first_part.replace("(", "")
            first_part = first_part.replace(")", "")

            try:
                value_size = [int(i) for i in first_part.split(",")]
                value_size = tuple(value_size)
            except:
                pass

            second_part = second_part.split()

            if len(second_part) == 0:
                second_part = ""
            elif len(second_part) == 1:
                second_part = second_part[0]
                try:
                    second_part = float(second_part)
                    if round(second_part) == second_part:
                        value = int(second_part)
                except:
                    try:
                        value = int(second_part)
                    except:
                        pass
            else:
                second_part = [
                    second_part[i].replace("<", "") for i in range(len(second_part))
                ]
                second_part = [
                    second_part[i].replace(">", "") for i in range(len(second_part))
                ]
                if ":" in second_part[0]:
                    second_part[2] = str(month_mapping.get(second_part[2]))
                    datestring = " ".join(second_part)
                    second_part = datetime.datetime.strptime(datestring, "%H:%M:%S %d %m %Y")
                else:
                    pass
                try:
                    second_part = np.array(second_part, dtype=float)
                    second_part = np.reshape(second_part, value_size)
                except:
                    pass
            try:
                second_part = second_part.replace("<", "")
                second_part = second_part.replace(">", "")
            except:
                pass

            value = second_part

        parameters[name] = value

    del parameters["_extra"]

    return parameters
