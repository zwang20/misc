import subprocess


def get_previous_files():
    return (
        subprocess.run(["ls", "batch"], capture_output=True, check=True)
        .stdout.decode("utf-8")
        .strip()
        .split()
    )


def get_prefix_list(batch):
    prefix_list = []
    with open(f"batch/{batch}.txt", encoding="utf-8") as f:
        for line in f:
            prefix_list.append(line.strip())
    return prefix_list
