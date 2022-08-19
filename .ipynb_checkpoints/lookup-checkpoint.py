from Param_TKA import *
from Libraries_TKA import *

def main():

    # todo: enrollees:: Join
    enrollees = pd.read_csv(descript_base_dir + "Enrollees.txt", sep="|")

    for visit in [0]:# 0,1,3,5,6,8,10 # 0-> base, 1->12m, 3->24m, 5->36, 6->48
        visit_str = "{0:0=2d}".format(visit)
        print("\n",visit_str)

        # todo: xray00:: lateral
        xray00 = pd.read_csv(descript_base_dir + "XRay"+visit_str+".txt",sep="|")
        print(xray00.head(2),"\n")

        # "V00EXAMTP" in "Lateral Left Knee", "Lateral Right Knee"   OR "PA Fixed Flexion Right Knee", "PA Fixed Flexion Left Knee"
        print("xray"+visit_str+" shape:", xray00.shape )
        print("xray"+visit_str+" unique patients:", xray00['ID'].unique().shape)
        filter = ["Lateral Left Knee", "Lateral Right Knee","PA Fixed Flexion Right Knee", "PA Fixed Flexion Left Knee"]
        xray00 = xray00[xray00["V"+visit_str+"EXAMTP"].isin(filter)]
        print("Drop all but: ",filter)
        print("xray"+visit_str+" shape:", xray00.shape)
        print("xray"+visit_str+" unique patients:", xray00['ID'].unique().shape)
        for col in []: # ["V00XRCOMP","V00ACCEPT","V00ALIGN","V00CENTER","V00DEPICT","V00EXPOSE","V00MOTION","V00POSITN"]:
            xray00 = xray00[xray00[col].isin(["\'Y\': QCd and found to be acceptable","\' \'  : Not QCd or meets QC standard","1: Yes",])]
            print("xray"+visit_str+" shape:", xray00.shape)
            print("xray"+visit_str+" unique patients:",col, xray00['ID'].unique().shape)

        joinedSet = enrollees.merge(xray00, suffixes=('', '_duplicate'), on='ID', how='right')
        print("JoinedSet: ", joinedSet["V00COHORT"].value_counts())
        joinedSet["V" + visit_str + "XRDATE"] = pd.to_datetime(joinedSet["V" + visit_str + "XRDATE"],infer_datetime_format=True)
        duplicate = [x for x in joinedSet.columns if "_duplicate" in x ]

        # continue
        counter = 0
        for index, row in joinedSet.iterrows():
            counter+=1
            # https://medium.com/@vivek8981/dicom-to-jpg-and-extract-all-patients-information-using-python-5e6dd1f1a07d
            # D:\___NDA\Package_1200138\results\00m\0.E.1\9152569\20060302\01351805\001
            # D:\___NDA\Package_1200138\results\00m\0.E.1\   ID  \  Date  \166+ ...\001
            # D:\___NDA\Package_1200138\results\00m\  ?  \   ID  \V00XRDATE\V00XRBARCD -166\001


            cohort = "C.2" if row["V00CHRTHLF"]== "1: First half of cohort" else "E.1" if row["V00CHRTHLF"]== "2: Second half of cohort" else np.nan
            try: date_str = row["V" + visit_str + "XRDATE"].strftime("%Y%m%d")
            except:
                print("na",end=".")
                continue

            image_dir = str(visit)+"."+cohort+    "\\"   +str(row["ID"])+  "\\"  +str(date_str)+  "\\" +str(str(int(row["V00XRBARCD"])).split(str(166))[1])+   "\\001"
            # folder_path ="D:\\___NDA\\Package_1200138\\results\\00m\\" # "\0.C.2\
            ds = dicom.dcmread(os.path.join(folder_path, img_bese_dir +image_dir.replace("\\",seperator_char)))
            pixel_array_numpy = ds.pixel_array
            jpg_folder_path = ".\\jpg\\"
            cv2.imwrite(os.path.join(jpg_folder_path.replace("\\",seperator_char), image_dir.replace("\\","_")+".jpg"), pixel_array_numpy)

            plt.imshow(ds.pixel_array)
            plt.title(row["V00XRSIDE"]+" * "+ str(row["ID"])+" * "+image_dir)
            if counter == 1: plt.show()
            print(counter, end=".")
            if counter == 3: exit()
            exit()
        print()

if __name__ == '__main__':
    main()