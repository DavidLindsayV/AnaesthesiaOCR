import csv

def write_to_csv(ocr_data):
    field_names = ["rtime",	"ecg.hr",	"ecg.st1",	"ecg.st2",	"ecg.st3",	"ecg.imp_rr",	"p1.sys",	"p1.dia",	"p1.mean",	"p1.hr",	"p2.sys",	"p2.dia",	"p2.mean",	"p2.hr",	"p3.sys",	"p3.dia",	"p3.mean", 	"p3.hr",	"p4.sys",	"p4.dia",	"p4.mean",	"p4.hr",	"nibp.sys",	"nibp.dia",	"nibp.mean",	"nibp.hr",	"t1.temp",	"t2.temp",	"t3.temp",	"t4.temp",	"spo2.SpO2"	,"spo2.pr",	"spo2.ir_amp",	"co2.et",	"co2.fi",	"co2.rr",	"co2.amb_press",	"o2.et",	"o2.fi",	"n2o.et",	"n2o.fi",	"aa.et",	"aa.fi",	"aa.mac_sum",	"p5.sys",	"p5.dia",	"p5.mean",	"p5.hr",	"p6.sys",	"p6.dia",	"p6.mean",	"p6.hr"]

    data = []
    for data_row in ocr_data:
        dataDict = {}
        for field in field_names:
            if field in data_row:
                dataDict[field] = data_row[field]
            else:
                dataDict[field] = -32767
        data.append(dataDict)



    # File path to save the CSV file
    csv_file_path = 'output.csv'

    # Writing data to CSV file
    with open(csv_file_path, 'w', newline='') as csv_file:
        # Define CSV writer object
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        
        # Write header
        writer.writeheader()
        
        # Write data
        writer.writerows(data)
