import os
import shutil
from pathlib import Path

from nnunetv2.dataset_conversion.generate_dataset_json import generate_dataset_json
from nnunetv2.paths import nnUNet_raw
import re

def make_out_dirs(dataset_id: int, task_name="ImageCAS"):
    dataset_name = f"Dataset{dataset_id:03d}_{task_name}"
#     out_dir = Path(nnUNet_raw.replace('"', "")) / dataset_name
    out_dir = Path("/workspace/U-Mamba/data/nnUNet_raw") / dataset_name
    out_train_dir = out_dir / "imagesTr"
    out_labels_dir = out_dir / "labelsTr"
    out_test_dir = out_dir / "imagesTs"
    out_testlabels_dir = out_dir / "labelsTs"
    
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(out_train_dir, exist_ok=True)
    os.makedirs(out_labels_dir, exist_ok=True)
    os.makedirs(out_test_dir, exist_ok=True)
    os.makedirs(out_testlabels_dir, exist_ok=True)
    
    return out_dir, out_train_dir, out_labels_dir, out_test_dir, out_testlabels_dir


def copy_files(src_data_folder: Path, train_dir: Path, labels_dir: Path, test_dir: Path, testlabels_dir: Path):
    patients_train = sorted([f for f in (src_data_folder / "training").iterdir()])
    patients_test = sorted([f for f in (src_data_folder / "testing").iterdir()])

    num_training_cases = 0
    for file in patients_train:
        match = re.match(r"(\d+)(.*)", file.name)
        if match:
            num_part = match.group(1)
            rest_part = match.group(2)

        if rest_part == ".img.nii.gz":
            shutil.copy(file, train_dir / f"{num_part}_0000.nii.gz")
#             print(f"{train_dir}/{num_part}_0000.nii.gz")
            num_training_cases += 1

        elif rest_part == ".label.nii.gz":
            shutil.copy(file, labels_dir / f"{num_part}.nii.gz")
#             print(f"{labels_dir}/{num_part}.nii.gz")

    for file in patients_test:
        match = re.match(r"(\d+)(.*)", file.name)
        if match:
            num_part = match.group(1)
            rest_part = match.group(2)

        if rest_part == ".img.nii.gz":
            shutil.copy(file, test_dir / f"{num_part}_0000.nii.gz")
#             print(f"{test_dir}/{num_part}_0000.nii.gz")

        elif rest_part == ".label.nii.gz":
            shutil.copy(file, testlabels_dir / f"{num_part}.nii.gz")
#             print(f"{testlabels_dir}/{num_part}.nii.gz")

    return num_training_cases


def convert_acdc(src_data_folder: str, dataset_id=66):
    out_dir, train_dir, labels_dir, test_dir, testlabels_dir = make_out_dirs(dataset_id=dataset_id)
    num_training_cases = copy_files(Path(src_data_folder), train_dir, labels_dir, test_dir, testlabels_dir)

    generate_dataset_json(
        str(out_dir),
        channel_names={
            0: "CT",
        },
        labels={
            "background": 0,
            "CA": 1,
        },
        file_ending=".nii.gz",
        num_training_cases=num_training_cases,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_folder",
        type=str,
        help="The downloaded ACDC dataset dir. Should contain extracted 'training' and 'testing' folders.",
    )
    parser.add_argument(
        "-d", "--dataset_id", required=False, type=int, default=66, help="nnU-Net Dataset ID, default: 66"
    )
    args = parser.parse_args()
    print("Converting...")
    convert_acdc(args.input_folder, args.dataset_id)
    print("Done!")
