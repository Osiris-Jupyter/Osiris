import csv 

csv_name_normal = 'analyzed_results_normal.csv'
csv_name_OEC = 'analyzed_results_OEC.csv'

csv_file = open(csv_name_OEC, 'r', encoding='utf-8')
reader = csv.reader(csv_file)

reproductivity_ratios = []
for row_idx, row in enumerate(reader):
    reproductivity_ratio = float(row[3])
    # print(reproductivity_ratio)
    reproductivity_ratios.append(reproductivity_ratio)
    
avg_reproductivity_ratio = sum(reproductivity_ratios) / len(reproductivity_ratios)
print(avg_reproductivity_ratio)
