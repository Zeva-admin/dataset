import os
import sys
import argparse
from dotenv import load_dotenv

def check():
    load_dotenv()
    required = ["YANDEX_CLIENT_ID", "YANDEX_CLIENT_SECRET", "YANDEX_TOKEN"]
    missing = [x for x in required if not os.getenv(x)]
    print("=== Environment check ===")
    if missing:
        print("Missing variables:", ", ".join(missing))
        return 1

    try:
        import datasets
        import yadisk
        print("Libraries: OK")
    except Exception as e:
        print("Library error:", e)
        return 1

    print("Dataset availability check...")
    try:
        from datasets import get_dataset_config_names
        get_dataset_config_names("Glint-Research/Fable-5-traces")
        print("Hugging Face dataset reachable: OK")
    except Exception as e:
        print("Dataset check failed:", e)
        return 1

    print("Everything looks ready.")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.check:
        sys.exit(check())

    load_dotenv()

    from datasets import load_dataset
    import yadisk

    folder = os.getenv("YANDEX_FOLDER", "Fable-5-traces")
    print("Downloading dataset...")
    ds = load_dataset("Glint-Research/Fable-5-traces")
    local_dir = "dataset_export"
    ds.save_to_disk(local_dir)
    print("Dataset saved locally.")

    y = yadisk.YaDisk(token=os.getenv("YANDEX_TOKEN"))

    if not y.exists(folder):
        y.mkdir(folder)

    for root, _, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            remote_path = f"{folder}/{os.path.relpath(local_path, local_dir)}"
            remote_parent = "/".join(remote_path.split("/")[:-1])
            try:
                if remote_parent and not y.exists(remote_parent):
                    y.mkdir(remote_parent)
            except Exception:
                pass
            print(f"Uploading {local_path} -> {remote_path}")
            y.upload(local_path, remote_path, overwrite=True)

    print("Finished.")

if __name__ == "__main__":
    main()
