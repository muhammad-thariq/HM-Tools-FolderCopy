# Folder Copy

---

This Python script provides a simple yet powerful way to **copy the structure and content of a specified folder (and its subfolders) into one or more text files**. It's particularly useful for creating a snapshot of a codebase, documenting project files, or preparing content for analysis or sharing, especially when dealing with large projects that might exceed typical file size limits.

## Features

* **Copies Folder Structure:** Recreates a hierarchical view of your directories and files, similar to the `tree /f` command.
* **Extracts File Content:** Reads the content of each file and appends it to the output.
* **Automatic File Splitting:** If the output file exceeds a defined character limit (defaulting to 4,000,000 characters), the script automatically creates a new text file to continue the output, preventing overly large single files.
* **Flexible Folder Selection:**
    * **Automatic Mode:** Copies all folders and subfolders within the script's directory.
    * **Specific Mode:** Allows you to specify which folders to include and/or exclude, giving you granular control over the copied content.
* **Error Handling:** Gracefully handles errors when reading files, logging them in the output without stopping the process.
* **Relative Path Support:** When specifying folders in "Specific Mode," you can use paths relative to the script's location.

## How to Use

1.  **Save the Script:** Save the provided Python code as `folder_copy.py` in the directory you want to process.
2.  **Run the Script:** Open a terminal or command prompt, navigate to the directory where you saved the script, and run it using:
    ```bash
    python folder_copy.py
    ```
3.  **Choose Your Mode:**
    * **Automatic Mode (`a`):** Type `a` and press Enter to copy all folders and files from the script's current directory downwards.
    * **Specific Mode (`s`):** Type `s` and press Enter. You'll then be prompted to enter your specific folders and/or exclusions.

### Specific Mode Input Format

Use `s` to indicate folders to include and `e` to indicate folders to exclude. Paths should be relative to the script's location.

* **Include specific folders:**
    ```
    s src data
    ```
    (This will copy content from `src` and `data` folders.)

* **Exclude specific folders:**
    ```
    e node_modules build
    ```
    (This will copy everything *except* content from `node_modules` and `build` folders.)

* **Combine includes and excludes:**
    ```
    s my_project/backend my_project/frontend e my_project/frontend/node_modules
    ```
    (This will copy content from `my_project/backend` and `my_project/frontend`, but will exclude the `node_modules` folder *within* `my_project/frontend`.)

## Output

The script will create one or more `.txt` files (e.g., `output_code_1.txt`, `output_code_2.txt`) in the same directory as the script. Each file will contain:

1.  **Folder Structure:** A tree-like representation of the copied directories and files.
2.  **File Content:** The actual content of each copied file, preceded by `--- Nama File: [filepath] ---`.
3.  **Error Messages:** If a file cannot be read, an error message will be included.

## Configuration (within the script)

You can modify the `copy_folder_contents_to_txt` function call in the `if __name__ == "__main__":` block to change default behavior:

* `output_filename_prefix`: Changes the prefix for the output text files (default: `output_code`).
* `max_chars_per_file`: Adjusts the maximum character limit per output file (default: 4,000,000).

```python
# Example of changing parameters in the main block
# copy_folder_contents_to_txt(
#     root_for_walk_param,
#     output_filename_prefix="project_snapshot",
#     max_chars_per_file=2000000, # 2 million characters
#     specific_folders_filter=specific_folders_for_filter,
#     exclude_folders_filter=exclude_folders_for_filter,
#     display_root_name=display_root_name_param
# )
