import re
import sys
from nltk.metrics.distance import edit_distance
import csv
from jiwer import cer
import matplotlib.pyplot as plt
import os
import openpyxl

from monitor_values import Field_Ranges


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


def get_extracted_data():
    extracted_data = []
    with open(os.path.join("accuracy_result_csvs", "easyocr_96.3.csv"), "r") as file:
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
    return extracted_data


def get_expected_data():
    dataframe = openpyxl.load_workbook(os.path.join("images", "monitor_data.xlsx"))
    dataframe1 = dataframe["OldMonitor"]
    # expected_data = pd.read_excel(os.path.join("images","monitor_data.xlsx"), sheet_name="OldMonitor")
    firstrow = True
    end_of_data_reached = False
    columns = []
    expected_data = []
    for row in range(0, dataframe1.max_row):
        if firstrow:
            firstrow = False
            for col in dataframe1.iter_cols(1, dataframe1.max_column):
                print(col[row].value)
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
    return expected_data

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def calculate_accuracy_metrics(extracted_data, expected_data):
    num_correct = 0
    tot_edit_dist = 0
    tot_cer = 0
    tot_numerical_dist = 0
    eval_params = [
        [0 for y in range(5)] for x in range(len(fields))
    ]  # this is a 2d array. The first index is what the field is. The second array is of [count_of_correct_ocr, total_edit_distance, total_cer, tot_numeric_dist, tot_numeric_dist_normalised]

    # Estimates for the ranges of each physiological parameter. Note, these are ESTIMATES  TODO double check these estimates??
    field_ranges = Field_Ranges.field_ranges

    for i in range(len(extracted_data)):
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
            if is_float(extr) and is_float(exp):
                exp = re.sub(r"[^0-9.]", "", exp)
                extr = re.sub(r"[^0-9.]", "", extr)
                tot_numerical_dist += abs(float(exp) - float(extr))
                eval_params[j][3] += abs(float(exp) - float(extr))
                field_range = field_ranges[fields[j]][0] - field_ranges[fields[j]][1]
                eval_params[j][4] += abs(float(exp) - float(extr)) / field_range

        print("Processed " + str(i + 1) + " out of " + str(len(expected_data)))
    
    tot_param_count = len(extracted_data) * len(fields)
    avg_accuracy = "{:.1f}".format((num_correct / tot_param_count) * 100)
    avg_edit_distance = "{:.3f}".format((tot_edit_dist / tot_param_count))
    avg_cer = "{:.3f}".format((tot_cer / tot_param_count) * 100)
    avg_numerical_distance = "{:.3f}".format((tot_numerical_dist / tot_param_count))
    image_count = len(extracted_data)

    return avg_accuracy, avg_edit_distance, avg_cer, avg_numerical_distance, image_count, eval_params

def print_accuracy_metrics(avg_accuracy, avg_edit_distance, avg_cer, avg_numerical_distance, eval_params, image_count):
    print()
    print("ACCURACY: " + avg_accuracy + "%")
    print("AVG EDIT DISTANCE: " + avg_edit_distance + " edits")
    print("AVG CHARACTER ERROR RATE: " + avg_cer + "%")
    print("AVG NUMERICAL DISTANCE: " + avg_numerical_distance)
    print()
    for i in range(len(fields)):
        eval_params[i][0] = "{:.1f}".format((eval_params[i][0] / image_count) * 100)
        eval_params[i][1] = "{:.3f}".format((eval_params[i][1] / image_count))
        eval_params[i][2] = "{:.3f}".format((eval_params[i][2] / image_count) * 100)
        eval_params[i][3] = "{:.1f}".format((eval_params[i][3] / image_count))
        eval_params[i][4] = "{:.1f}".format(
            ((eval_params[i][4]) / image_count) * 100
        )
        print(
            "Field "
            + str(fields[i])
            + " Accuracy = "
            + eval_params[i][0]
            + "% | Avg Edit Distance: "
            + eval_params[i][1]
            + " edits | Avg CER: "
            + eval_params[i][2]
            + "% | Avg Numeric Distance = "
            + eval_params[i][3]
            + " | Normalised Avg Numeric Distance = "
            + eval_params[i][4]
            + "%"
        )

def create_accuracy_pyplot(avg_accuracy, avg_edit_distance, avg_cer, avg_numerical_distance, eval_params):
    fig, ax = plt.subplots()
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_frame_on(False)
    columns = [
        "Accuracy (%)",
        "Avg Edit Distance (edits)",
        "Avg Character Error Rate (%)",
        "Avg Numeric Distance (unitless)",
        "Norm Avg Numeric Distance (%)",
    ]
    fields.append("Average")
    rows = fields
    eval_params.append(
        [avg_accuracy, avg_edit_distance, avg_cer, avg_numerical_distance, "NA"]
    )
    table_data = eval_params
    table = ax.table(
        cellText=table_data,
        rowLabels=rows,
        colLabels=columns,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)  # Set the desired font size
    table.scale(1, 1)  # Scale the table cells (width, height)
    for key, cell in table.get_celld().items():
        if key[0] == 0 or key[1] == -1:
            cell.set_text_props(weight="bold")
            # cell.set_text_props(fontsize='10')
            cell.set_facecolor("#D3D3D3")  # Light gray background for header
        else:
            cell.set_edgecolor("black")  # Black border for cells
            cell.set_linewidth(0.5)  # Border line width
    final_row_idx = len(rows)
    for col_idx in range(len(columns)):
        cell = table[(final_row_idx, col_idx)]
        cell.set_text_props(weight="bold")
        cell.set_linewidth(1)

    table.auto_set_column_width(col=list(range(len(columns))))  # Adjust column widths
    plt.subplots_adjust(left=0.2, top=0.8)
    plt.show()


def calculate_accuracy():
    extracted_data = get_extracted_data()
    expected_data = get_expected_data()
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

    avg_accuracy, avg_edit_distance, avg_cer, avg_numerical_distance, image_count, eval_params = calculate_accuracy_metrics(extracted_data, expected_data)

    print_accuracy_metrics(avg_accuracy, avg_edit_distance, avg_cer, avg_numerical_distance, eval_params, image_count)
    create_accuracy_pyplot(avg_accuracy, avg_edit_distance, avg_cer, avg_numerical_distance, eval_params)

    
calculate_accuracy()


# TODO calculate the odds of getting an entire row correct, not just one field in a row
