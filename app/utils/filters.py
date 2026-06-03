import os


def is_noise_file(path):

    filename = os.path.basename(path)

    return (
        filename.startswith("~$")
        or filename.endswith(("~", ".tmp", ".crdownload", ".part"))
        or ".idea" in path
        or "__pycache__" in path
    )