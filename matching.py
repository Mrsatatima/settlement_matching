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