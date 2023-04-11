import pandas as pd
import openpyxl
import re
from copy import deepcopy
import difflib

adamawa_LGA =  ["DEMSA","FUFORE","GANYE","GIREI","GOMBI","GUYUK","HONG","JADA",
       "LAMURDE","MADAGALI","MAIHA","MAYO-BELWA","MICHIKA","MUBI NORTH",
       "MUBI SOUTH","NUMAN","SHELLENG","SONG","TOUNGO","YOLA NORTH","YOLA SOUTH"
       ]
    
osun_LGA = ["ATAKUNMOSA EAST","ATAKUNMOSA WEST","AYEDAADE","AYEDIRE","BOLUWADURO","BORIPE",
        "EDE NORTH","EDE SOUTH","EGBEDORE","EJIGBO","IFE CENTRAL","IFE EAST",
        "IFE NORTH","IFE SOUTH","IFEDAYO","IFELODUN","ILA","ILESHA EAST","ILESHA WEST",
        "IREPODUN","IREWOLE","ISOKAN","IWO","OBOKUN","ODO-OTIN","OLAOLUWA","OLORUNDA",
        "ORIADE","OROLU","OSHOGBO",]

def get_p3b_list(df, LGA, p3b=True):

    """
        Extracts a list of settlements from a DataFrame containing P3B information.

        Parameters:
        df (pandas.DataFrame): The DataFrame containing the P3B information.
        LGA (str): The name of the Local Government Area (LGA) to extract settlements from.
        p3b (bool): Indicates whether the Dataframe is a P3B or not.

        Returns:
        tuple: A tuple containing the extracted settlements (as a dictionary) and the number of settlements found.
     """

    # Initialize an empty dictionary to store the extracted data
    p3b_list = {}

    # Initialize a counter variable to keep track of the number of settlements
    count = 0
   
    # Iterate over each row of the DataFrame
    for idx in range(len(df)):
        # Extract the settlement information from the appropriate column based on the p3b parameter
        if str(df[f"{'List of contiguous communities/ settlements' if p3b else 'P3B Name'}"][idx]) not in ["", " ", "NAN", "nan", "0"]:
            settlement = " ".join(str(df[f"{'List of contiguous communities/ settlements' if p3b else 'P3B Name'}"][idx]).lower().replace(".", "").replace(".", "").replace(")", "").replace("(", "").strip().split())
            
            # Extract the LGA information from the input parameter
            lga = f"{LGA}".lower().strip()

            # Extract the ward information from the appropriate column based on the p3b parameter
            ward = str(df[f"{'Wards' if p3b else 'Ward'}"][idx]).lower().strip()

            # Add the settlement information to the p3b_list dictionary
            if lga not in p3b_list:
                p3b_list[lga] = {}
            if ward not in p3b_list[lga]:
                p3b_list[lga][ward] = set()
            if settlement != "nan" and p3b and str(df["List of contiguous communities/ settlements"][idx]) not in ["", " ", "Nan", "NAN", "nan", "0", 0]:
                p3b_list[lga][ward].add(settlement)
                count += 1
            elif not p3b and str(df["Geo Capture Name"][idx]) not in ["", " ", "Nan", "NAN", "nan", "0", 0]:
                p3b_list[lga][ward].add(settlement)
                count += 1

    # Sort the settlements in each ward by name
    for key, values in p3b_list[LGA.lower()].items():
        count += len(values)
        p3b_list[LGA.lower()][key] = sorted(values)

    # Return the p3b_list dictionary and the settlement count
    return p3b_list, count

def get_captured_list(df, LGA, grid3=False):

    """
        Returns a dictionary of captured settlements in a given Local Government Area
        (LGA) with their corresponding coordinates.

        Args:
        df (pandas DataFrame): The data containing settlement, LGA, ward, latitude, 
                                longitude, and, if grid3 is False, altitude and accuracy.
        LGA (str): The name of the Local Government Area.
        grid3 (bool, optional): A boolean indicating whether to include altitude and accuracy 
                                values in the output. Defaults to False. It salso indicates 
                                whether the file is RR_colect or grid3 dataset

        Returns:
        dict: A dictionary where keys are LGAs and values are dictionaries where keys are wards and values are dictionaries
             where keys are settlements and values are strings of latitude and longitude separated by a '|' character, or, if grid3 is True, separated by '|' and followed by altitude and accuracy separated by '|'.

    """
    captured_list = {}

    # Iterate over each row in the dataframe
    for idx in range(len(df)):
        # Get the name of the settlement, LGA, ward, latitude, and longitude
        settlement = " ".join(str(df["Name of Settlement"][idx]).lower().replace(".","").replace(".","").replace(")","").replace("(","").strip().split())
        lga = str(df["LGA"][idx]).lower().strip()
        ward = str(df["Ward"][idx]).lower().strip()
        latitude= str(df["Latitude"][idx]).lower().strip()
        longitude = str(df["Longitude"][idx]).lower().strip()

        # If grid3 is False, also get the accuracy and altitude values
        if not grid3:
            accuracy = str(df["Acurracy"][idx]).lower().strip()
            altitude = str(df["Altitude"][idx]).lower().strip()

        # If the LGA matches the requested LGA
        if lga == LGA.lower():
            # Add the settlement to the captured_list dictionary
            if lga not in captured_list:
                captured_list[lga] = {}
            if ward not in captured_list[lga]:
                captured_list[lga][ward] = {}
            if settlement not in captured_list[lga][ward]:
                # If grid3 is False, only add latitude and longitude to the captured_list value
                captured_list[lga][ward][settlement] = f"{latitude}|{longitude}" if not grid3 else f"{latitude}|{longitude}|{accuracy}|{altitude}"

    return captured_list
