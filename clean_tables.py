import pandas as pd

rr_collect_filename = ''
grid3_filename = ''
state = ''
df = pd.read_excel(rr_collect_filename,  index_col=None)
df2 = pd.read_csv(grid3_filename, index_col=None)


fields ={
        "State":"Please Select the State You are Currently In",
        "LGA":"Please Select the LGA You are Currently In",
        "Ward":"Please Select the ward",
        "Type":"Is your current location a Settlement or a Distribution Hub?",
        "Name of Settlement":"Please Type the Name of the Settlement",
        "DH":"What Distribution Hub is the settlement Clustered in?",
        "Type of DH":"What type of Distribution Hub is this?",
        "Others":"If others, please specify:",
        "Name of DH":"Please enter the name of the Distribution hub",
        "Settlement":"Please enter the settlement the Distribution hub is located in",
        "Location":"Capture the GPS Coordinate of the Location",
        "Date_time":"Form Filling End"
        }

def write_csv(data_frame):
    """
        a function that convert RR_Collect data to a format 
        suitable for matching process. It drops unwanted columns and splits 
        the coordinates field. It creates two csv files one for settlements
        and one for DH

        Args:
                Dataframe: pandas dataframe of the rr collect data set
        return:
                None

    """
    settlement_data = {"State":[],"LGA":[],"Ward":[], "Name of Settlement":[],"DH":[],
                        "Latitude":[],"Longitude":[], "Acurracy":[], "Altitude":[],"Date_time":[]
                    }
    DH_data = {"State":[],"LGA":[],"Ward":[], "Settlement":[], "Name of DH":[], "Type of DH":[],
                        "Latitude":[],"Longitude":[], "Acurracy":[], "Altitude":[],"Date_time":[]
                    }
    for idx in range(len(data_frame)):
        if data_frame[fields["Type"]][idx] == "Distribution Hub":
            print(data_frame[fields["Name of DH"]][idx])
            DH_data["State"].append(data_frame[fields["State"]][idx])
            DH_data["LGA"].append(data_frame[fields["LGA"]][idx])
            DH_data["Ward"].append(data_frame[fields["Ward"]][idx])
            DH_data["Settlement"].append(data_frame[fields["Settlement"]][idx])

            DH_data["Name of DH"].append(data_frame[fields["Name of DH"]][idx])
            type_of_dh = data_frame[fields["Type of DH"]][idx] if data_frame[fields["Type of DH"]][idx] != "Other" else data_frame[fields["Others"]][idx]
            DH_data["Type of DH"].append(type_of_dh)
            DH_data["Acurracy"].append(data_frame[fields["Location"]][idx].split("|")[0])
            DH_data["Altitude"].append(data_frame[fields["Location"]][idx].split("|")[1])
            DH_data["Latitude"].append(data_frame[fields["Location"]][idx].split("|")[2])
            DH_data["Longitude"].append(data_frame[fields["Location"]][idx].split("|")[3])
            DH_data["Date_time"].append(data_frame[fields["Date_time"]][idx])
        else:
            settlement_data["State"].append(data_frame[fields["State"]][idx])
            settlement_data["LGA"].append(data_frame[fields["LGA"]][idx])
            settlement_data["Ward"].append(data_frame[fields["Ward"]][idx])
            settlement_data["Name of Settlement"].append(data_frame[fields["Name of Settlement"]][idx])
            settlement_data["DH"].append(data_frame[fields["DH"]][idx])
            settlement_data["Acurracy"].append(data_frame[fields["Location"]][idx].split("|")[0])
            settlement_data["Altitude"].append(data_frame[fields["Location"]][idx].split("|")[1])
            settlement_data["Latitude"].append(data_frame[fields["Location"]][idx].split("|")[2])
            settlement_data["Longitude"].append(data_frame[fields["Location"]][idx].split("|")[3])
            settlement_data["Date_time"].append(data_frame[fields["Date_time"]][idx])

    settlement_dataframe = pd.DataFrame(settlement_data, index=None)
    dh_dataframe = pd.DataFrame(DH_data, index=None)
    print(settlement_dataframe)
    print(dh_dataframe)
    settlement_dataframe.to_csv("Cleaned_adamawa_settlement_capture.csv", index=False)
    dh_dataframe.to_csv("Cleaned_adamawa_DH_capture.csv", index=False)

def write_grid3_csv(data_frame,state):
    """
        extracts all settlments points of a state from the GRID3 data sets.
        it arrange the columns in a format suitable for matching process
        Args:
                data_frame: pandas dataframe of the GRID3 settlement point
                            data 
                state: The state you want it settlements to be extracted
    """
    settlement_data = {"State":[],"LGA":[],"Ward":[], "Name of Settlement":[],
                        "Latitude":[],"Longitude":[],}
    for idx in range(len(data_frame)):
        if data_frame['statename'][idx] == f"{state}":
            settlement_data["State"].append(data_frame["statename"][idx])
            settlement_data["LGA"].append(data_frame["lganame"][idx])
            settlement_data["Ward"].append(data_frame["wardname"][idx])
            settlement_data["Name of Settlement"].append(data_frame["set_name"][idx])
            settlement_data["Latitude"].append(data_frame["Y"][idx])
            settlement_data["Longitude"].append(data_frame["X"][idx])
          

    settlement_dataframe = pd.DataFrame(settlement_data, index=None)
    print(settlement_dataframe)
    settlement_dataframe.to_csv(f"{state}_grid3_settlements.csv", index=False)


write_csv(df)

write_grid3_csv(df2,state)