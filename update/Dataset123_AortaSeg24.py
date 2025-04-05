import os
import shutil
from pathlib import Path

from nnunetv2.dataset_conversion.generate_dataset_json import generate_dataset_json
from nnunetv2.paths import nnUNet_raw


def make_out_dirs(dataset_id: int, task_name="AortaSeg24"):
    dataset_name = f"Dataset{dataset_id:03d}_{task_name}"

#     out_dir = Path(nnUNet_raw.replace('"', "")) / dataset_name
    out_dir = Path("/workspace/U-Mamba/data/nnUNet_raw") / dataset_name
    out_train_dir = out_dir / "imagesTr"
    out_labels_dir = out_dir / "labelsTr"
    out_test_dir = out_dir / "imagesTs"
    out_testlabels_dir = out_dir / "labelsTs" #++
    
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(out_train_dir, exist_ok=True)
    os.makedirs(out_labels_dir, exist_ok=True)
    os.makedirs(out_test_dir, exist_ok=True)
    os.makedirs(out_testlabels_dir, exist_ok=True)
    
    return out_dir, out_train_dir, out_labels_dir, out_test_dir, out_testlabels_dir


def copy_files(src_data_folder: Path, train_dir: Path, labels_dir: Path, test_dir: Path, testlabels_dir: Path):
#     """Copy files from the ACDC dataset to the nnUNet dataset folder. Returns the number of training cases."""
#     patients_train = sorted([f for f in (src_data_folder / "images").iterdir() if f.is_dir()])
#     patients_test = sorted([f for f in (src_data_folder / "testing").iterdir() if f.is_dir()])

#     num_training_cases = 0
#     # Copy training files and corresponding labels.
#     for patient_dir in patients_train:
#         for file in patient_dir.iterdir():
#             if file.suffix == ".gz" and "_gt" not in file.name and "_4d" not in file.name:
#                 # The stem is 'patient.nii', and the suffix is '.gz'.
#                 # We split the stem and append _0000 to the patient part.
#                 shutil.copy(file, train_dir / f"{file.stem.split('.')[0]}_0000.nii.gz")
#                 num_training_cases += 1
#             elif file.suffix == ".gz" and "_gt" in file.name:
#                 shutil.copy(file, labels_dir / file.name.replace("_gt", ""))

#     # Copy test files.
#     for patient_dir in patients_test:
#         for file in patient_dir.iterdir():
#             if file.suffix == ".gz" and "_gt" not in file.name and "_4d" not in file.name:
#                 shutil.copy(file, test_dir / f"{file.stem.split('.')[0]}_0000.nii.gz")
#             elif file.suffix == ".gz" and "_gt" in file.name:
#                 shutil.copy(file, testlabels_dir / file.name.replace("_gt", ""))

    """Copy files from the dataset to designated training and testing folders based on file naming conventions."""
    
    # Get all .mha files in the images directory
    image_files = sorted(src_data_folder.glob("images/*.mha"))
    
    # Get all .mha label files in the labels directory
    label_files = sorted(src_data_folder.glob("masks/*.mha"))
    
    # Create a dictionary to easily map images to labels
    label_dict = {f.name.replace('_label', '_CTA'): f for f in label_files}

    # Filter files for training and testing based on the naming convention
    patients_train = [f for f in image_files if int(f.stem.split('subject')[1].split('_')[0]) <= 43]
    patients_test = [f for f in image_files if 41 <= int(f.stem.split('subject')[1].split('_')[0]) <= 53]

    num_training_cases = 0
    # Copy training files and corresponding labels.
    for file in patients_train:
        new_filename = f"{file.stem}_0000.mha"
        shutil.copy(file, train_dir / new_filename)
        num_training_cases += 1
        # Check and copy the corresponding label file
#         print(file.name)
        if file.name in label_dict:
            shutil.copy(label_dict[file.name], labels_dir / f"{file.stem}.mha")
            

    # Copy test files and labels.
    for file in patients_test:
        new_filename = f"{file.stem}_0000.mha"
        shutil.copy(file, test_dir / new_filename)
        # Check and copy the corresponding label file
        if file.name in label_dict:
            shutil.copy(label_dict[file.name], testlabels_dir / f"{file.stem}.mha")

    return num_training_cases


def convert_AortaSeg24(src_data_folder: str, dataset_id=123):
    out_dir, train_dir, labels_dir, test_dir, testlabels_dir = make_out_dirs(dataset_id=dataset_id)
    num_training_cases = copy_files(Path(src_data_folder), train_dir, labels_dir, test_dir, testlabels_dir)

    generate_dataset_json(
        str(out_dir),
        channel_names={
            0: "CTA",  # Assuming you only have one type of imaging modality
        },
        labels={
            "background": 0,
            "Zone0": 1,
            "Innominate": 2,
            "Zone1": 3,
            "Left_Common_Carotid": 4,
            "Zone2": 5,
            "Left_Subclavian_Artery": 6,
            "Zone3": 7,
            "Zone4": 8,
            "Zone5": 9,
            "Zone6": 10,
            "Celiac_Artery": 11,
            "Zone7": 12,
            "SMA": 13,
            "Zone8": 14,
            "Right_Renal_Artery": 15,
            "Left_Renal_Artery": 16,
            "Zone9": 17,
            "Zone10R": 18,
            "Zone10L": 19,
            "Right_Internal_Iliac_Artery": 20,
            "Left_Internal_Iliac_Artery": 21,
            "Zone11R": 22,
            "Zone11L": 23
        },
        file_ending=".mha",
        num_training_cases=num_training_cases,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input_folder", type=str, help="downloads AortaSeg24",
    )
    parser.add_argument(
        "-d", "--dataset_id", required=False, type=int, default=123, help="nnU-Net Dataset ID, default: 123"
    )
    args = parser.parse_args()
    print("Converting...")
    convert_AortaSeg24(args.input_folder, args.dataset_id)
    print("Done!")
