import csv
from datetime import datetime, timedelta
import re


def is_number(string):
    # Regular expression to match a number, optionally surrounded by brackets
    pattern = r"\(?\d+(\.\d+)?\)?"
    return bool(re.match(pattern, string))


def parse_number(string):
    string = string.replace("(", "").replace(")", "")
    if "." in string:
        string = float(string)
    else:
        string = int(string)
    return string


def write_to_csv(ocr_data):
    field_names = ["rtime",	"ecg.hr",	"ecg.st1",	"ecg.st2",	"ecg.st3",	"ecg.imp_rr",	"p1.sys",	"p1.dia",	"p1.mean",	"p1.hr",	"p2.sys",	"p2.dia",	"p2.mean",	"p2.hr",	"p3.sys",	"p3.dia",	"p3.mean", 	"p3.hr",	"p4.sys",	"p4.dia",	"p4.mean",	"p4.hr",	"nibp.sys",	"nibp.dia",	"nibp.mean",	"nibp.hr",	"t1.temp",	"t2.temp",	"t3.temp",	"t4.temp",	"spo2.SpO2"	,"spo2.pr",	"spo2.ir_amp",	"co2.et",	"co2.fi",	"co2.rr",	"co2.amb_press",	"o2.et",	"o2.fi",	"n2o.et",	"n2o.fi",	"aa.et",	"aa.fi",	"aa.mac_sum",	"p5.sys",	"p5.dia",	"p5.mean",	"p5.hr",	"p6.sys",	"p6.dia",	"p6.mean",	"p6.hr"]
    fields_to_multiply_by_100 = [
        "p1.mean",
        "p1.sys",
        "p1.dia",
        "p2.mean",
        "p2.sys",
        "p2.dia",
        "p3.mean",
        "p3.sys",
        "p3.dia",
        "p4.mean",
        "p4.sys",
        "p4.dia",
        "nibp.mean",
        "nibp.sys",
        "nibp.dia",
        "co2.et",
        "co2.fi",
        "aa.mac_sum",
        "t1.temp",
        "t2.temp",
        "t3.temp",
        "t4.temp",
    ]

    data_writtenTextFormat = [] #the CSV which has text accurate to what was displayed on the screen. This matches with the excel file
    for data_row in ocr_data:
        dataDict = {}
        for field in field_names:
            if field in data_row:
                dataDict[field] = data_row[field]
            else:
                dataDict[field] = ''
        data_writtenTextFormat.append(dataDict)

    time = datetime.now()
    data_EddiFormat = [] #the CSV which has text in the format EDDI expects
    for data_row in ocr_data:
        dataDict = {}
        dataDict["rtime"] = time.strftime("%d/%m/%Y %H:%M:%S")
        time = time + timedelta(days=0, seconds=10)
        for field in data_row.keys():
            if is_number(data_row[field]):
                number = parse_number(data_row[field])
                if field in fields_to_multiply_by_100:
                    dataDict[field] = number * 100
                else:
                    dataDict[field] = number
            else:
                dataDict[field] = '' #the non numeric '' will be quoted and turn into ""
        data_EddiFormat.append(dataDict)

    # File path to save the CSV file
    csv_file_path_text = "output_text.csv"
    csv_file_path_EDDI = "output_eddi.csv"

    # Writing data to CSV file
    with open(csv_file_path_text, "w", newline="") as csv_file:
        # Define CSV writer object
        writer = csv.DictWriter(csv_file, fieldnames=data_writtenTextFormat[0].keys(), quoting=csv.QUOTE_NONNUMERIC)

        # Write header
        writer.writeheader()

        # Write data
        writer.writerows(data_writtenTextFormat)
    
    with open(csv_file_path_EDDI, "w", newline="") as csv_file:
        # Define CSV writer object
        writer = csv.DictWriter(csv_file, fieldnames=data_EddiFormat[0].keys(), quoting=csv.QUOTE_NONNUMERIC)

        # Write header
        writer.writeheader()

        # Write data
        writer.writerows(data_EddiFormat)