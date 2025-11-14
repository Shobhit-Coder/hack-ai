import os
import json

OUTPUT_DIR = "/app/output"


def save_results(parsed_dict: dict):
    """
    parsed_dict: { "filename.pdf": { ...parsed data... }, ... }
    """

    print("--------------------------------------------------")
    print("[SAVE] save_results() called")
    print(f"[SAVE] OUTPUT_DIR is set to: {OUTPUT_DIR}")

    # Ensure output folder exists
    try:
        print("[SAVE] Ensuring output directory exists...")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print("[SAVE] Output directory is ready.")
    except Exception as e:
        print(f"[SAVE][ERROR] Could not create output directory: {e}")
        raise

    # If parsed data is empty
    if not parsed_dict:
        print("[SAVE] No parsed results to save — parsed_dict is empty.")
        print("--------------------------------------------------")
        return

    print("[SAVE] Files to save:", list(parsed_dict.keys()))

    # Save each parsed result
    for filename, parsed_data in parsed_dict.items():
        print("--------------------------------------------------")
        print(f"[SAVE] Processing file key: {filename}")

        # Normalize filename (remove any accidental paths)
        fname = os.path.basename(filename)
        out_name = fname + ".json"
        out_path = os.path.join(OUTPUT_DIR, out_name)

        print(f"[SAVE] Normalized filename: {fname}")
        print(f"[SAVE] Output JSON path: {out_path}")

        try:
            print(f"[SAVE] Writing JSON file for {fname}...")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(parsed_data, f, indent=4, ensure_ascii=False)
            print(f"[SAVE] Successfully wrote: {out_path}")
        except Exception as e:
            print(f"[SAVE][ERROR] Failed to write {out_path}: {e}")

    print("--------------------------------------------------")
    print("[SAVE] save_results() completed for all files.")
    print("--------------------------------------------------")
