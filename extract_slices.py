from Libraries_TKA import *
from PIL import Image

def get_parser():
    parser = argparse.ArgumentParser(description="Extract/Preprocess MRIs from the OAI dataset")
    parser.add_argument("--enrollees", dest="enrollees",
                        help="CSV containing list of eligable patients")
    parser.add_argument("--root", dest="rootdir", 
                        help="Root directory of MRI slices")
    parser.add_argument("--outdir", dest="outdir", 
                        help="Output directory to store MRI slices")
    parser.add_argument("--slices", type=int, default=10,
                        help="Number of slices per MRI to extract")
    parser.add_argument("--n", type=int, default=200, 
                       help="Number of MRIs to extract")

    return parser

def sample_and_extract(enrollees, num_mris, num_slices, root_dir, outdir):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    dcm_format = "{dcm}.dcm"
    samples = enrollees.sample(num_mris)
    slices_per_side = num_slices//2

    for i, row in samples.iterrows():
        directory = os.path.join(root_dir, row.file_pth)
        slices = os.listdir(directory)
        mid_slice = len(slices)//2

        copy_dir = os.path.join(outdir, row.file_pth)
        
        if not os.path.exists(copy_dir):
            os.makedirs(copy_dir)
        
        for slice_num in range(mid_slice-(slices_per_side), mid_slice + (slices_per_side + 1)):
            slice_name = str(slice_num).zfill(3)
            dcm = dicom.dcmread(os.path.join(directory, slice_name))
            img = Image.fromarray(dcm.pixel_array)
            img.convert('L').save(os.path.join(copy_dir, slice_name + ".jpg"))
            

def main():
    parser = get_parser()
    args = parser.parse_args()

    enrollees = pd.read_csv(args.enrollees)
    sample_and_extract(enrollees, args.n, args.slices, args.rootdir, args.outdir)
        


if __name__ == "__main__":
    main()