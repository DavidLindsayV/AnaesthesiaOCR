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

        if columns[col_num] in fields:
            row_data[fields.index(columns[col_num])] = str(col[row].value)
    if end_of_data_reached:
        break
    expected_data.append(row_data)

print("Expected data loaded")

print("Number of images in OCR output: " + str(len(extracted_data)) + " \nNumber of images in testing data: " + str(len(expected_data)))
num_correct = 0
num_incorrect = 0
field_correct = [0 for x in range(len(fields))]
for i in range(len(extracted_data)):
    print(expected_data[i])
    print(extracted_data[i])
    for j in range(len(fields)):
        exp = expected_data[i][j]
        extr = extracted_data[i][j]
        if exp == extr:
            num_correct += 1
            field_correct[j] += 1
        else:
            num_incorrect += 1
    acc_so_far = num_correct/(num_correct + num_incorrect)
    # print("ACCURACY SO FAR: " + str(num_correct/(num_correct + num_incorrect)))
    print("Processed " + str(i+1) + " out of " + str(len(expected_data)))

print("ACCURACY: " + "{:.1f}".format((num_correct/(num_correct + num_incorrect))*100) + "%") 

for i in range(len(fields)):
    print("Accuracy for field " + str(fields[i]) + " = " + "{:.1f}".format((field_correct[i]/len(expected_data))*100) + "%") 