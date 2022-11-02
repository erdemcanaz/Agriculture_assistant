from pathlib import Path


def append_to_txt_file(file_name, data):
    this_file_parent_path = Path(__file__).parent
    log_folder_path = this_file_parent_path / "log_files"

    txt_file_path_str = str(log_folder_path)+"/"+str(file_name)+".txt"

    with open(txt_file_path_str, 'a') as f:
        f.write(data)


