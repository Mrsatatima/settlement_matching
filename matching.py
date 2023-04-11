import pandas as pd
import openpyxl
import re
from copy import deepcopy
import difflib
import os

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

def matching_same_name(p3b_list, capture_list, perfect_match, LGA, captured=True):
    """
        Matches settlements in the P3B list with those in the capture list that have the same name, 
        and returns a dictionary of perfect matches. 
        
        Args:
            p3b_list (dict): Dictionary of settlements in P3B list.
            capture_list (dict): Dictionary of captured settlements.
            perfect_match (dict): Dictionary of perfect matches.
            LGA (str): Name of Local Government Area.
            captured (bool): Whether the capture list is a RR collect or a GRID3 list. 
                Defaults to True.
        
        Returns:
            tuple: A tuple containing the updated P3B list, capture list, perfect match dictionary, and count of matches.
    """
    settlement_list = {}
    count = 0
    
    # Iterate through the P3B list and compare settlements to the captured settlements.
    for lga, wards in p3b_list.items():
        if lga in capture_list:
            for ward in wards:
                if ward in capture_list[lga]:
                    for settlement in wards[ward]:
                        if settlement in capture_list[lga][ward]:
                            # Add the settlement to the perfect match dictionary.
                            if lga not in perfect_match:
                                perfect_match[lga] = {}
                            if ward not in perfect_match[lga]:
                                perfect_match[lga][ward] = {}
                            perfect_match[lga][ward][settlement] = {settlement: capture_list[lga][ward][settlement]} \
                                if captured else {settlement: settlement}
                            count += 1
                            
                            # Remove the settlement from the capture list.
                            if captured:
                                capture_list[lga][ward].pop(settlement)
                            else:
                                capture_list[lga][ward].remove(settlement)
                            
                            # Add the settlement to the settlement list.
                            if ward not in settlement_list:
                                settlement_list[ward] = []
                            settlement_list[ward].append(settlement)
    
    # Remove settlements from the P3B list that have been matched using the settlement list.
    for ward, settlements in settlement_list.items():
        for settlement in settlements:
            if settlement in p3b_list[LGA.lower()][ward]:
                p3b_list[LGA.lower()][ward].remove(settlement)
    
    # Return the updated P3B list, capture list, perfect match dictionary, and count of matches.
    return p3b_list, capture_list, perfect_match, count

def match_phrases(phrase1, phrase2, ratio=0.8):
    """
        Compares two phrases and returns whether they are a match based on a similarity ratio.

        Args:
            phrase1 (str): The first phrase to compare.
            phrase2 (str): The second phrase to compare.
            ratio (float, optional): The minimum similarity ratio required to consider the phrases a match. Defaults to 0.8.

        Returns:
            tuple: A tuple containing a boolean indicating whether the phrases are a match, and the similarity ratio between them.
    """
    # If either phrase is empty or only contains whitespace, they cannot be a match
    if phrase1 in [" ",""] or phrase2 in [" ",""]:
        return False, 0
    
    # Calculate the similarity ratio between the two phrases using the SequenceMatcher class from difflib
    similarity_ratio = difflib.SequenceMatcher(None, phrase1, phrase2).ratio()
    
    # If the similarity ratio is above the specified threshold, consider the phrases a match
    if similarity_ratio >= ratio:  
        return True, similarity_ratio
    else:
        return False, similarity_ratio

def similar_name(p3b_list, capture_list, perfect_match, LGA, ratio, dictionary=False):
    """
        Find similar names between two dictionaries of settlements.

        Parameters:
        -----------
        p3b_list : dict
            A dictionary of settlements with Local Government Areas and wards as keys from P3B.
        capture_list : dict
            A dictionary of settlements with Local Government Areas and wards as keys from RR Collect of GRID3.
        perfect_match : dict
            A dictionary to store the matching settlements.
        LGA : str
            A string that specifies the Local Government Area to match.
        ratio : float
            A float between 0 and 1 that specifies the ratio of similarity between the settlement names.
        captured : bool, optional
            A boolean value that specifies if the settlement name should be captured or not.
        dictionary : bool, optional
            A boolean value that specifies if the common words in the settlement names should be removed.

        Returns:
        --------
        tuple
            A tuple containing four elements:
            - A dictionary of matching settlements.
            - A dictionary of settlements with unmatched settlements removed.
            - The number of settlements removed.
            - A dictionary of settlements that did not match.
    """
    p3b_list=deepcopy(p3b_list)  # Make a copy of p3b_list to avoid modifying the original
    capture_list=deepcopy(capture_list)  # Make a copy of capture_list to avoid modifying the original
    count =0  # Initialize a count variable to zero
    settlement_list = {}  # Create an empty dictionary to store the settlement data

    # Loop through the LGA and wards in p3b_list
    for lga, wards in p3b_list.items():
        if lga in capture_list:  # Check if the LGA is in the capture_list or matching
            # Loop through the wards in the p3b_list
            for ward in wards:
                if ward in capture_list[lga]:  # Check if the ward is in the capture_list for the current LGA
                    # Loop through the settlements in the current ward
                    for settlement in wards[ward]:
                        matcthin_list = {}  # Initialize an empty dictionary to store matching settlements

                        # Loop through the settlements in the capture_list for the current LGA and ward
                        for settlement2 in capture_list[lga][ward]:
                            common_words = ["anguwan","anguwar","anguwa","angwa","ang","unguwan","unguwar",
                                            "alhaji","alh", "gidan","gildan","jauro","ung"
                                            "lccn","mayo", "village","head","phcc","phc","clinic","hc",
                                            "health","clinic", "post", "hp","hc", "jauro",'gida',"h/c","h/p"
                                            "house", "primary","pri", "school","sch","islamiyya","mallam","malam",
                                            "primary", "secondary","hospital","dh","sec","line","street","str",
                                            "sabon gari","sabongari"]  # Define a list of common words to remove from settlement names
                            
                            settlement_remove = settlement  # Set the settlement_remove variable to the current settlement
                            settlement2_remove = settlement2  # Set the settlement2_remove variable to the current settlement in the capture_list
                            if dictionary: # if dictionary is true remove common words
                                for word in common_words: # loop through common_words list
                                    settlement_remove = settlement_remove.replace(word,"") # remove common words from settlement
                                    settlement2_remove = settlement2_remove.replace(word,"") # remove common words from settlement2
                            settlement2_remove.strip() # remove leading/trailing spaces from settlement2_remove
                            settlement_remove.strip() # remove leading/trailing spaces from settlement_remove
                            get_match = match_phrases(settlement_remove,settlement2_remove,ratio) # get match between settlement and settlement2
                            if get_match[0]: # if get_match is is true
                                matcthin_list[settlement2] = get_match[1] # add settlement2 and its match ratio to matcthin_list
                        if matcthin_list: # if matcthin_list is not empty
                            settlement2 = max(matcthin_list, key=matcthin_list.get) # get settlement2 with highest match ratio
                            if lga not in perfect_match: # if lga not in perfect_match
                                perfect_match[lga]={} # add lga to perfect_match
                            if ward not in perfect_match[lga]: # if ward not in perfect_match[lga]
                                perfect_match[lga][ward]={} # add ward to perfect_match[lga]
                            if settlement not in perfect_match[lga][ward]: # if settlement not in perfect_match[lga][ward]
                                perfect_match[lga][ward][settlement]={} # add settlement to perfect_match[lga][ward]
                            perfect_match[lga][ward][settlement][settlement2]=capture_list[lga][ward][settlement2] 
                            # add settlement and its best match (settlement2) to perfect_match[lga][ward]
                            capture_list[lga][ward].pop(settlement2) # remove settlement2 from capture_list
                            if ward not in settlement_list: # if ward not in settlement_list
                                settlement_list[ward] =set() # add ward to settlement_list
                            settlement_list[ward].add(settlement) # add settlement to settlement_list[ward]

    # loop through settlement_list to remove settlements that are matched in p3b_list
    for ward, settlements in settlement_list.items(): # loop through settlement_list
        for settlement in settlements: # loop through settlements in ward
            if settlement in p3b_list[LGA.lower()][ward]: # if settlement is in p3b_list[LGA.lower()][ward]
                p3b_list[LGA.lower()][ward].remove(settlement) # remove settlement from p3b_list
            count+=1

    # return the following variables
    return perfect_match, p3b_list, count, capture_list

def create_excel(matched_settlements, unmatched_settlements,LGA, file_name, grid3=False,field_name="GRID3 Name"):
    """
        Creates an excel sheet with settlement data for a given Local Government Area (LGA).

        Args:
            matched_settlements (dict): A dictionary containing matched settlements information.
            unmatched_settlements (dict): A dictionary containing unmatched settlements information.
            LGA (str): Name of the Local Government Area (LGA).
            file_name (str): Name of the Excel file to be created.
            grid3 (bool, optional): A boolean value indicating whether its GRID3 or RR Collect.
                                    Defaults to False.
            field_name (str, optional): Name of the field to be used for Grid3 name if grid3 is True.
                                        Defaults to "GRID3 Name".

        Returns:
            str: A string indicating that the function has finished execution ("DONE").
    """

    lga_name = []
    ward_name =[]
    p3b_name = []
    grid3_name = []
    capture_name= []
    coordinate = []
    lat  =[]
    lon = []
    acc = []
    alt = []

    # Loop through the matched_settlements dictionary to extract information
    # and append it to respective lists
    for lga, wards in matched_settlements.items():
        for ward, dhs in wards.items():
            for dh, dh2 in dhs.items():
                text =""
                cod_text =""
                for name, coord in dh2.items():
                    text += f"{name}"
                    cod_text += f"{coord}"
                cod =cod_text.split("|")
                lat.append(cod[0])
                lon.append(cod[1])
                if len(cod) ==4:
                    acc.append(cod[2])
                    alt.append(cod[3])
                else:
                    acc.append("")
                    alt.append("")

                capture_name.append(text.capitalize())
                lga_name.append(lga.capitalize())
                ward_name.append(ward.capitalize())
                p3b_name.append(dh.capitalize())

    # Loop through the unmatched_settlements dictionary to extract information
    # and append it to respective lists
    for lga, wards in unmatched_settlements.items():
        for ward, dhs in wards.items():
            for dh in dhs:
                coordinate.append("")
                grid3_name.append(" ")
                capture_name.append(" ")
                lga_name.append(lga.capitalize())
                ward_name.append(ward.capitalize())
                p3b_name.append(dh)
                lat.append("")
                lon.append("")
                acc.append("")
                alt.append("")

    # Create pre_reconciled DataFrame with the extracted information
    if not grid3:
        pre_reconciled = pd.DataFrame({"LGA":lga_name,"Ward":ward_name,"DH P3B Name":p3b_name,
                            f"{field_name}":capture_name, "Latitude":lat,"Longitude":lon,
                            "Accuracy":acc,"Altitude":alt})
    else:
        pre_reconciled = pd.DataFrame({"LGA":lga_name,"Ward":ward_name,"DH P3B Name":p3b_name,
                            f"{field_name}":capture_name, "Latitude":lat,"Longitude":lon,})

    # Print pre_reconciled DataFrame
    print(pre_reconciled)
    #create excel file using file name if its not in the directory
    if not os.path.isfile(file_name):
        wb = openpyxl.Workbook()  
        wb.save(file_name, as_template=False)

    # Open the workbook and create a writer object to write the DataFrame to the sheet
    book = openpyxl.load_workbook(file_name)
    writer = pd.ExcelWriter(file_name, "openpyxl")
    writer.book =book
    pre_reconciled.to_excel(writer, sheet_name=f'{LGA}',index=False )
    writer.close()
    return "DONE"

def run():
    """
        Runs the matching process for each Local Government Area (LGA) in Adamawa state.

        Reads in data files for settlements captured in grid3 and RR Collection exercises,
        as well as the P3B data for each LGA. Matches settlements in the P3B data to settlements in the
        grid3 and RR Collection data, then writes the results to separate Excel files for each LGA.

        Returns nothing.
    """
    # Read in the data files for settlements captured in grid3 and RR Collection exercises
    grid3_file= pd.read_csv("Adamawa_grid3_settlements.csv")
    rr_collect_file = pd.read_csv("Cleaned_adamawa_settlement_capture.csv")

    # Create a dictionary to hold the matching results for each LGA
    summary_dic= {"LGA":[],"Total P3B Settlement":[],
                  "100% matched":[],">= 70% matched":[],
                  ">= 50% matched":[],"Not matched":[]}

    # Iterate over each LGA
    for local_gov in LGA:
        # Read in the P3B data for the current LGA
        p3b =  pd.read_excel("ADAMAWA HARMONIZED P3B.xlsx", f'{local_gov}'.upper())

        # Get a list of settlements in the P3B data for the current LGA
        # and the total number of settlements in the P3B data for the current LGA
        p3b_list, total_settlement = get_p3b_list(p3b,local_gov,)

        # Get a list of settlements captured in grid3 for the current LGA,
        # and match settlements in the P3B data to settlements in the grid3 data
        grid3_list = get_captured_list(grid3_file,local_gov,True)
        perfect = {}
        updated_p3B_list, updated_grid3_list, perfect, same_matched = matching_same_name(p3b_list,grid3_list,perfect,local_gov)

        # Match settlements in the P3B data that were not matched in the first pass to
        # settlements in the grid3 data using a similarity threshold of 0.9
        perfect, not_matched, similar_matched_7, updated_grid3_list = similar_name(updated_p3B_list, updated_grid3_list,perfect,local_gov,.9)

        # Match settlements in the P3B data that were not matched in the second pass to
        # settlements in the grid3 data using a similarity threshold of 0.75
        perfect, not_matched, similar_matched_5, updated_grid3_list= similar_name(not_matched,updated_grid3_list,perfect,local_gov,.75,dictionary=True)

        # Write the matching results to an Excel file for the current LGA
        create_excel(perfect,{},local_gov,"Adamawa_matching_set_with_GRID3.xlsx",True)

        # Print a message indicating that the matching process for the current LGA is complete
        print("Done...........................................")
        print("Finish GRID3...........................................||||||||||||||||||||||||||||||||||")

        # Match settlements in the P3B data that were not matched in the first pass to rr_collect data
        perfect ={}
        # Perform exact name matching between not_matched settlements from p3b data and rr_collect data
        updated_not_matched, updated_rr_collect_list, perfect, same_matched = matching_same_name(not_matched,rr_collect_list,perfect,local_gov)
       
        # Match settlements in the P3B data that were not matched in the second pass to
        # settlements in  rr_collect data using a similarity threshold of 0.9
        perfect, updated_not_matched, similar_matched_7, updated_rr_collect_list = similar_name(updated_not_matched, updated_rr_collect_list,perfect,local_gov,.9)

        # Match settlements in the P3B data that were not matched in the second pass to
        # settlements in  rr_collect data using a similarity threshold of 0.75
        perfect, updated_not_matched, similar_matched_5, updated_rr_collect_list= similar_name(updated_not_matched,updated_rr_collect_list,perfect,local_gov,.75,dictionary=True)
       
        # Create an excel file with matched settlements between not_matched settlements from p3b data and rr_collect data
        create_excel(perfect,{},local_gov,"Adamawa_matching_set_with_RR_Collect.xlsx",field_name="RR Collect Name")
        print("Done...........................................")
        print("Finish rr collect...........................................||||||||||||||||||||||||||||||||||")


        # Match settlements that did not macthed at all using lower threshold and append to another file
        # Perform similar name matching between updated_not_matched settlements from p3b data and grid3 data with threshold of 0.6
        perfect ={}
        perfect, updated_not_matched, similar_matched_5, updated_grid3_list= similar_name(updated_not_matched,updated_grid3_list,perfect,local_gov,.6,dictionary=True)
        create_excel(perfect,{},local_gov,"Adamawa_matching_set_with_GRID3_6.xlsx")
        print("Done...........................................")
        
        # Perform similar name matching between updated_not_matched settlements from p3b data and rr collect data data with threshold of 0.6

        perfect ={}
        perfect, updated_not_matched, similar_matched_5, updated_rr_collect_list= similar_name(updated_not_matched,updated_rr_collect_list,perfect,local_gov,.6,dictionary=True)
      
        create_excel(perfect,{},local_gov,"Adamawa_matching_set_with_RR_Collect_6.xlsx",field_name="RR Collect Name")

        # Create Excel file with the not matched items
        create_excel({},updated_not_matched,local_gov,"Adamawa_matching_set_no_match.xlsx")

        print("Done...........................................")
    print("Finish...........................................")
