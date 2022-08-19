from Libraries_TKA import *
from utils.preprocessing import image_preprocessing

def get_parser():
    parser = argparse.ArgumentParser(description="Extract/Preprocess MRIs from the OAI dataset")
    parser.add_argument("--enrollees", dest="enrollees",
                        help="CSV containing list of eligable patients")
    parser.add_argument("--mri-info", dest="mri", 
                        help="OAI MRI CSV file for baseline visit. ")
    parser.add_argument("--view", dest="view", 
                        help="MRI view to extract")
    parser.add_argument("--outdir", dest="outdir", 
                        help="Output directory to store processed MRI files")
    parser.add_argument("--h5", type=bool, default=False, 
                       help="Save MRI slices in h5 format")

    return parser

def create_h5(save_dir, f_name, img):
    if not os.path.exists(save_dir):
        print("Creating savedir...")
        os.makedirs(save_dir)

    data_path = os.path.join(save_dir,f_name)
    f = h5py.File(data_path, 'w')
    f.create_dataset('data', data=img)
    f.close()
    
    
def filter_by_view(enrollee_pth, mri_pth, visit_id, view_query="SAG"):
    mri_info = pd.read_csv(mri_pth, sep="|")
    enrollees = pd.read_csv(enrollee_pth)
    
    # Column name formatters
    view_col = "V{id}MEXAMTP".format(id=visit_id)
    date_col = "V{id}MRDATE".format(id=visit_id)
    
    # Filter views and keep 
    unique_views = [view for view in mri_info[view_col].unique() if view_query in view]
    filtered = mri_info[mri_info[view_col].isin(unique_views)]
    joined_set = enrollees.merge(filtered, on='ID', how='right')
    joined_set[date_col] = pd.to_datetime(joined_set[date_col], infer_datetime_format=True)
    
    # Filter by eligability
    joined_set = joined_set[(joined_set.right_eligible & joined_set[view_col].str.contains("R")) |
                            (joined_set.left_eligible & joined_set[view_col].str.contains("L")) |
                            (joined_set.right_control & joined_set[view_col].str.contains("R")) |
                            (joined_set.left_control & joined_set[view_col].str.contains("L"))]
    
    joined_set["status"] = ["Progressed" if row.right_eligible or row.left_eligible else "NotProgressed"
                            for i, row in joined_set.iterrows()]
    return joined_set.reset_index(drop=True)


def retrieve_and_save_mri(pid, cohort, time, visit_id, mri_barcode, save_dir, filename=None, h5=False):
    slices = []
    mri_pth = "/mnt/data1/OAI/{vid}m/results/{visit}.{cohort}/{pid}/{date}/{barcode}/"
    mri_formatted_pth = mri_pth.format(vid=visit_id, visit=int(visit_id), cohort=cohort, pid=pid, 
                                 date=time, barcode=mri_barcode)
        
    # Preprocessing
    for slice_num in os.listdir(mri_formatted_pth):
        slice_pth = os.path.join(mri_formatted_pth, slice_num)

        if not h5:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
                
            shutil.copy(slice_pth, save_dir)
        
        # TODO: Add handling for preprocessing of dcm and h5  file formats
        # img, data, img_before = image_preprocessing(slice_pth)
        # slices.append(img)
    
    # Save in h5 format if h5=True
    if h5:
        filename = filename.format(pid=pid, barcode=mri_barcode)
        create_h5(save_dir, filename, slices)
        
    return True
    

def main():
    parser = get_parser()
    args = parser.parse_args()
        
    visit_id = "00"
    
    filtered_patients = filter_by_view(args.enrollees, args.mri, visit_id, args.view)

    filtered_patients["file_pth"] = "N/A" # 20 patients with no MRI barcode/date 
    
    file_dirs = []
    for i, row in filtered_patients.iterrows():
        cohort = "C.2" if row["V00CHRTHLF"]== "1: First half of cohort" else "E.1" if row["V00CHRTHLF"] == "2: Second half of cohort" else np.nan

        try: date = row["V" + visit_id + "MRDATE"].strftime("%Y%m%d")
        except:
            continue
        
        barcode = str(int(row["V00MRBARCD"]))[3:]
        
        # Generate folder/h5 file name
        save_name_template = "{pid}_{barcode}_L_{status}" if "L" in row.V00MEXAMTP else "{pid}_{barcode}_R_{status}" 
        save_name = save_name_template.format(pid=row.ID, barcode=barcode, status=row.status)


        if args.h5:
            retrieve_and_save_mri(row["ID"], cohort, date, visit_id, barcode, args.dirname, save_name) 
        else:
            retrieve_and_save_mri(row["ID"], cohort, date, visit_id, barcode, os.path.join(args.outdir, save_name)) # Remove the 166 at beginning to get id

 
        filtered_patients.loc[i, "file_pth"] = save_name
 
    
    filtered_patients.to_csv("eligable_MRI_8-07-2022.csv", index=False)

if __name__ == "__main__":
    main()