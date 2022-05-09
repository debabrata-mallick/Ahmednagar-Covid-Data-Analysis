#!/usr/bin/python3

import numpy as np
import csv, sys

def my_read_csv(fname):
    col2ind = {} # Dictionary of col name to index
    M = [] # The matrix of rows
    file_csv = csv.reader(open(fname, 'r'), delimiter=',', quotechar='"')
    row_num=0
    for row in file_csv:
        row_num += 1
        if(row_num == 1):
            for i in range(len(row)):
                col2ind[row[i]] = i
            continue # Ignore header row
        M.append(row)
    return (col2ind, M)


def levend(s, t):
    """ levenshtein_ratio_and_distance:
        Calculates levenshtein distance between two strings.
        If ratio_calc = True, the function computes the
        levenshtein distance ratio of similarity between two strings
        For all i and j, distance[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t
    """
    # Initialize matrix of zeros
    rows = len(s)+1
    cols = len(t)+1
    distance = np.zeros((rows,cols),dtype = int)

    # Populate matrix of zeros with the indeces of each character of both strings
    for i in range(1, rows):
        for k in range(1,cols):
            distance[i][0] = i
            distance[0][k] = k

    # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions    
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1].lower() == t[col-1].lower():
                cost = 0 # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
            else:
                # In order to align the results with those of the Python Levenshtein package, if we choose to calculate the ratio
                # the cost of a substitution is 2. If we calculate just distance, then the cost of a substitution is 1.
                cost = 1
            distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
                                 distance[row][col-1] + 1,          # Cost of insertions
                                 distance[row-1][col-1] + cost)     # Cost of substitutions
   
    return distance[rows-1][cols-1]

def match(slist,tlist):
  mm=len(slist)
  print(mm)
  nn=len(tlist)
  print(nn)
  dd = np.zeros((mm,nn),dtype = int)
  for i in range(0,mm):
      for j in range(0,nn):
        dd[i][j]=levend(slist[i],tlist[j])
  return dd

talukalist=["Ahmednagar","Parner","Pathardi","Shevgaon","Jamkhed","Karjat","Shrigonda","Nevasa","Rahata","Rahuri","Shrirampur","Akole","Kopargaon","Sangamner"]

slist=["Anagar","Pathri","Anaconda","Jam"]

#fname="Progressive_Death_Line_List_Ahmednagar.csv"
#fname="Ahmednagar_cases - March 21.csv"
#fname="Ahmednagar_cases - April 21.csv"
fname="Ahmednagar_cases - May 21.csv"
DISTANCE_THRESHOLD=2
outfname = "/tmp/taluka-match.csv"
out_csv = csv.writer(open(outfname, 'w'), delimiter=',', quotechar='"')
hdr_row = ['ICMR ID Check', 'Address', 'BestMatch', 'BestDistance', 'Match1', 'Distance1', 'Match2', 'Distance2', 'Match3', 'Distance3']
out_csv.writerow(hdr_row)
(col2ind, M) = my_read_csv(fname)
convert2space = ['-', ',', '.', '/', ':', ';', '(', ')', '&', '\'', '[', ']']
rownum = 0
for row in M:
    rownum += 1
    if(rownum % 1000 == 0):
        print("%d rows done" % (rownum))
    addr_str = row[col2ind['Address']]
    for c in convert2space:
        addr_str = addr_str.replace(c, ' ')
    addr_words = addr_str.split()
    distances = {}
    for tstr in talukalist:
        best_match_distance = 1e6
        for aw in addr_words:
            if((aw.lower() == "nagar") or (aw.lower() == "anagar")):
                aw = "Ahmednagar"
            distance = levend(aw, tstr)
            if(distance < best_match_distance):
                best_match_distance = distance
        distances[tstr] = best_match_distance
    sorted_distances = sorted(distances.items(), key=lambda x: x[1], reverse=False)

    row2write = [row[col2ind['ICMR ID']], addr_str]
    # If any taluka other than Ahmednagar matches, then take that instead of Ahmednagar
    # That is, take Ahmednagar only if nothing else matches
    best_match_taluka = sorted_distances[0][0]
    if(best_match_taluka.lower() == talukalist[0].lower()):
        if(sorted_distances[1][1] <= DISTANCE_THRESHOLD):
            best_match_taluka = sorted_distances[1][0]
    row2write.append(best_match_taluka)
    row2write.append(distances[best_match_taluka])
    # Write the best 3 matches also
    for i in range(3):
        row2write.append(sorted_distances[i][0])
        row2write.append(sorted_distances[i][1])
    out_csv.writerow(row2write)

print("Taluka match written to %s" % (outfname))
#d=match(slist,talukalist)
#print(d)
