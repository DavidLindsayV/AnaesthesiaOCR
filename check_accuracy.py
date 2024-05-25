import re
import sys
import pandas as pd
from nltk.metrics.distance import edit_distance
import csv
from jiwer import cer

from monitor_values import OldMonitor


fields = [
    "ecg.hr",
    "co2.et",
    "co2.fi",
    "co2.rr",
    "p1.sys",
    "p1.dia",
    "p1.mean",
    "aa.et",
    "aa.fi",
]

# co2.rr 50
# p1.mean 80
# aa.et 91
# aa.fi 93

extracted_data = []
with open("output.csv", "r") as file:
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

if len(expected_data) != len(extracted_data):
    print(
        "ERROR: Length of expected data doesn't match length of extracted data. Ending program"
    )
    sys.exit()

print(
    "Number of images in OCR output: "
    + str(len(extracted_data))
    + " \nNumber of images in testing data: "
    + str(len(expected_data))
)
num_correct = 0
tot_edit_dist = 0
tot_cer = 0
tot_numerical_dist = 0
eval_params = [
    [0 for y in range(5)] for x in range(len(fields))
]  # this is a 2d array. The first index is what the field is. The second array is of [count_of_correct_ocr, total_edit_distance, total_cer, tot_numeric_dist, tot_numeric_dist_normalised]

# Estimates for the ranges of each physiological parameter. Note, these are ESTIMATES  TODO double check these estimates??
field_ranges = OldMonitor.field_ranges

for i in range(len(extracted_data)):
    # print(expected_data[i])
    # print(extracted_data[i])
    for j in range(len(fields)):
        exp = expected_data[i][j]
        extr = extracted_data[i][j]
        if exp == extr:
            num_correct += 1
            eval_params[j][0] += 1
        else:
            print("Field: " + fields[j] + " Exp: " + exp + " Extr: " + extr)
        tot_edit_dist += edit_distance(exp, extr)
        tot_cer += cer(exp, extr)
        eval_params[j][1] += edit_distance(exp, extr)
        eval_params[j][2] += cer(exp, extr)
        if re.search(r"[-+]?\d*\.?\d+", extr) and re.search(r"[-+]?\d*\.?\d+", exp):
            exp = re.sub(r"[^0-9.]", "", exp)
            extr = re.sub(r"[^0-9.]", "", extr)
            tot_numerical_dist += abs(float(exp) - float(extr))
            eval_params[j][3] += abs(float(exp) - float(extr))
            field_range = field_ranges[fields[j]][0] - field_ranges[fields[j]][1]
            eval_params[j][4] += abs(float(exp) - float(extr)) / field_range
            # if float(exp) < field_ranges[fields[j]][1] or float(exp) > field_ranges[fields[j]][0]:
            #     print(
            #         "field = "
            #         + str(fields[j])
            #         + " value = "
            #         + str(exp)
            #         + " max = "
            #         + str(field_ranges[fields[j]][0])
            #         + " min = "
            #         + str(field_ranges[fields[j]][1])
            #     )

    print("Processed " + str(i + 1) + " out of " + str(len(expected_data)))

print()
tot_param_count = len(extracted_data) * len(fields)
print("ACCURACY: " + "{:.1f}".format((num_correct / tot_param_count) * 100) + "%")
print(
    "AVG EDIT DISTANCE: "
    + "{:.3f}".format((tot_edit_dist / tot_param_count))
    + " edits"
)
print(
    "AVG CHARACTER ERROR RATE: "
    + "{:.3f}".format((tot_cer / tot_param_count) * 100)
    + "%"
)
print(
    "AVG NUMERICAL DISTANCE: " + "{:.3f}".format((tot_numerical_dist / tot_param_count))
)
print()
for i in range(len(fields)):
    print(
        "Field "
        + str(fields[i])
        + " Accuracy = "
        + "{:.1f}".format((eval_params[i][0] / len(expected_data)) * 100)
        + "% | Avg Edit Distance: "
        + "{:.3f}".format((eval_params[i][1] / len(expected_data)))
        + " edits | Avg CER: "
        + "{:.3f}".format((eval_params[i][2] / len(expected_data)) * 100)
        + "% | Avg Numeric Distance = "
        + "{:.1f}".format((eval_params[i][3] / len(expected_data)))
        + " | Normalised Avg Numeric Distance = "
        + "{:.1f}".format(((eval_params[i][4]) / len(expected_data)) * 100)
        + "%"
    )


# TODO calculate the odds of getting an entire row correct, not just one field in a row
