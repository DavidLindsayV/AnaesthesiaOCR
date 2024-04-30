import pandas as pd

import csv

fields = ['ecg.hr', 'co2.et', 'co2.fi', 'co2.rr', 'p1.sys', 'p1.dia', 'p1.mean', 'aa.et', 'aa.fi']
   

extracted_data = []
with open("output.csv", 'r') as file:
    csvreader = csv.reader(file)
    firstrow = True
    columns = []
    for row in csvreader:
        if firstrow:
            firstrow = False
            columns = row
            continue
        processed_row = [None for x in range(len(fields))]
        for i, field in enumerate(columns):
            if field in fields:
                processed_row[fields.index(field)] = str(row[i])
        extracted_data.append(processed_row)
    
print("Extracted data loaded")

import openpyxl
dataframe = openpyxl.load_workbook("monitor_data.xlsx")
dataframe1 = dataframe.active
firstrow = True
end_of_data_reached = False
columns = []
expected_data = []
for row in range(0, dataframe1.max_row):
    if firstrow:
        firstrow = False
        for col in dataframe1.iter_cols(1, dataframe1.max_column):
            columns.append(col[row].value)
        continue
    row_data = [None for x in range(len(fields))]

    col_num = -1
    for col in dataframe1.iter_cols(1, dataframe1.max_column):
        col_num += 1
        if col[row].value is None:
            end_of_data_reached = True
            break #you've reached the end of recorded data
        if columns[col_num] in fields:
            row_data[fields.index(columns[col_num])] = str(col[row].value)
    if end_of_data_reached:
        break
    expected_data.append(row_data)
    
print("Expected data loaded")

num_correct = 0
num_incorrect = 0
for i in range(len(extracted_data)):
    for j in range(len(fields)):
        exp = expected_data[i][j]
        extr = extracted_data[i][j]
        if exp == extr:
            num_correct += 1
        else:
            num_incorrect += 1

print("ACCURACY: " + str(num_correct/(num_correct + num_incorrect)))