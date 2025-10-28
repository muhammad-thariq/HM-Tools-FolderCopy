# Folder Copy (user_paths.txt + user_exceptions.txt)

A small Python utility that **exports folder trees and file contents** into rotating TXT files.  
It reads **`user_paths.txt`** (include list) and **`user_exceptions.txt`** (exclude list), so the user **doesn’t need to pass any CLI flags**.

> Bahasa: Script ini menyalin struktur folder dan isi file ke TXT. Path dibaca dari `user_paths.txt` (yang ingin disalin) dan pengecualian dari `user_exceptions.txt` (yang ingin dikecualikan). Tidak perlu input `a/s` di terminal.

---

## Features
- Read multiple **include paths** from `user_paths.txt`, one per line.
- Read multiple **exclusion paths** from `user_exceptions.txt`, one per line.
- **Directories** are walked recursively; **files** are read exactly.
- **No extension ⇒ treated as a directory path**.
- Exclusions can be **folders or files**; excluded folders skip all descendants.
- Large outputs **auto-rotate** to `output_code_1.txt`, `output_code_2.txt`, … at ~4,000,000 chars per file.
- Folder headers show the **full absolute path**.
- Works with **absolute or relative** paths (relative to the script directory).
- Uses only the Python **standard library**.

---

## Requirements
- Python 3.8+
- No external dependencies

---

## Files in this folder
```
your_script.py        # the main script (put any name you like)
user_paths.txt              # list of include paths (required; if empty/missing, defaults to '.')
user_exceptions.txt         # list of exclude paths (optional)
output_code_1.txt     # generated output (auto-rotated)
output_code_2.txt
...
```
> Put `your_script.py`, `user_paths.txt`, and (optionally) `user_exceptions.txt` in the **same folder**.

---

## Quick Start
1. **Create/Edit `user_paths.txt`** — one entry per line:
   ```
   C:\laragon\www\mini-project\ITS-PBKK-MID\app
   ./src
   C:\some\file.py
   ```
   - **Folder path** (with or without trailing slash) ⇒ the entire folder will be scanned.
   - **File path** (has an extension) ⇒ only that file will be read.

2. **Create/Edit `user_exceptions.txt`** (optional) — one entry per line:
   ```
   node_modules
   build
   C:\laragon\www\mini-project\ITS-PBKK-MID\app\Http\Controllers\Auth\LoginController.php
   ```
   - Exclusions can be **relative** (to the script) or **absolute**.
   - A folder exclusion skips **all** of its contents.
   - A file exclusion skips only that file.

3. **Run the script**:
   ```bash
   python your_script.py
   ```

4. **Check outputs**: `output_code_1.txt`, `output_code_2.txt`, … are created **next to the script**.

---

## Output Format
- Per included directory:
  - A header line:
    ```
    --- Struktur Folder (<absolute-folder-path>\)
    ```
  - The **tree listing** (indented), then
  - `--- Isi File ---` followed by each file’s content, wrapped with
    ```
    --- Nama File: <relative/path/from/include-root> ---
    <file content>
    ```
- For single-file includes, a section:
  ```
  --- File Tunggal (N file) ---
  --- Isi File ---
  ...
  ```

---

## Path Rules & Resolution
- Lines starting with `#` are **comments** and will be ignored.
- Blank lines are ignored.
- **Relative paths** are resolved **relative to the script directory**.
- **Non-existent paths**:
  - If they **look like a directory** (no extension), they are **ignored** with a warning.
  - If they **look like a file** (has an extension), they are **ignored** with a warning.

---

## Customization
- **Fixed output directory**: change `output_dir = base_folder` in `__main__` to a fixed path, e.g.:
  ```python
  output_dir = r"C:\Users\Thariq\Documents\ITS\PROJECT\swiss-design\folder_copy"
  ```
- **Rotate size**: tweak `max_chars_per_file=4_000_000` in the function call.
- **Header display**: currently shows the **absolute path**. If you prefer to display exactly what the user typed, store the raw lines and pass them to the header instead of using `os.path.abspath(...)`.

---

## Troubleshooting
- **“[error] Nothing to process.”**  
  `user_paths.txt` is empty or all entries are invalid/missing.
- **Permission errors** on some files/folders  
  Run with sufficient permissions or exclude the paths in `user_exceptions.txt`.
- **Binary files look garbled**  
  Script opens files as text (`encoding='utf-8', errors='ignore'`). Add patterns to `user_exceptions.txt` or adapt the reader for binary handling.

---
