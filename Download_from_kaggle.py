from pathlib import Path
import kagglehub # read the library - download kaggle datasets

def download_and_list(slug: str) -> Path:
    folder = Path(kagglehub.dataset_download(slug))
    csvs = sorted(folder.rglob("*.csv")) # find every document that ends with csv
    print(f"\n[{slug}] downloaded to: {folder}")
    print("CSV files found:")
    for p in csvs:
        print(" -", p.name) # print csv file name
    if not csvs:
        raise FileNotFoundError(f"No CSV found under {folder}")
    return folder

prof_dir = download_and_list("ikynahidwin/depression-professional-dataset") # these are the directories of the kaggle slug
student_dir = download_and_list("adilshamim8/student-depression-dataset")
general_dir = download_and_list("anthonytherrien/depression-dataset")
