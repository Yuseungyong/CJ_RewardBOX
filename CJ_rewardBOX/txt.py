data1_before = 0
data2_before = 0
data3_before = 0

cnt = 0
while True:
    file1 = open("BPM_output.txt", 'r')
    data1 = file1.read()
    file2 = open("STEP_output.txt", 'r')
    data2 = file2.read()
    file3 = open("STEP_offset.txt", 'r')
    data3 = file3.read()
    if data1 =="":
        data1 = data1_before
    if data2 =="":
        data2 = data2_before
    if data1 =="":
        data3 = data3_before

    data1_before = data1
    data2_before = data2
    data3_before = data3 

    data1 = int(data1)
    data2 = int(data2)
    data3 = int(data3)
    
    print(data1, data2, data3)
    