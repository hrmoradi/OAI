import platform


# ToDo: File locations ##############################################################################################
# /data8/Package_1199934___44GB_screen
# /data8/Package_1200138___983GB_base
# /media/hmoradi/Seagate 8TB Drive/___NDA/Package_1200138/results/00m
# 0.C.2  0.E.1 #
# /data8/OAICompleteData_ASCII/
descript_base_dir = 'C:\\Users\\hrmor\\OneDrive - University of Mississippi Medical Center\\04_Projects\\Proj__Ahmad\\Proj__Nick\\NIH OAI Descr\\OAICompleteData_ASCII\\'
img_bese_dir = "C:\\Users\\hrmor\\OneDrive - University of Mississippi Medical Center\\04_Projects\\Proj__Ahmad\\Proj__Nick\\NIH OAI Descr\\Package_1199934_47GB\\results\\P001\\"
resultsLocation =""
folder_path =img_bese_dir # "\0.C.2\ # D:\\___NDA\\Package_1200138\\results\\00m\\
seperator_char = "\\"

if platform.system() != 'Windows':
    descript_base_dir = "/data8/OAICompleteData_ASCII/"
    img_bese_dir = "/data8/Package_1200138___983GB_base/"
    resultsLocation = ""
    folder_path = img_bese_dir # "/data8/Package_1200138___983GB_base/"  # "\0.C.2\
    seperator_char = "/"
logFile = open(resultsLocation+'Result_Logfile.txt', 'w')