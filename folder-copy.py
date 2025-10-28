import os

def read_lines(filepath):
    """
    Read non-empty, non-comment lines from a text file.
    Lines starting with # are ignored. Whitespace and quotes are stripped.
    """
    lines = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for raw in f.readlines():
                line = raw.strip().strip('"').strip("'")
                if not line or line.startswith('#'):
                    continue
                lines.append(line)
    except FileNotFoundError:
        # Silently return empty if not present; the caller can decide defaults.
        return []
    return lines

def resolve_path(p, base_folder):
    """
    Resolve a possibly-relative path to an absolute, normalized path.
    """
    p = os.path.expandvars(os.path.expanduser(p))
    if not os.path.isabs(p):
        p = os.path.join(base_folder, p)
    return os.path.normpath(os.path.abspath(p))

def split_exclusions(exclude_paths):
    """
    Split exclusion paths into two lists: directories and files.
    Unknown (non-existent) paths are treated by suffix heuristic:
    - if no extension -> likely directory exclusion
    - else -> likely file exclusion
    """
    exclude_dirs = []
    exclude_files = []
    for p in exclude_paths:
        if os.path.isdir(p):
            exclude_dirs.append(p)
        elif os.path.isfile(p):
            exclude_files.append(p)
        else:
            # Heuristic based on suffix
            root, ext = os.path.splitext(p)
            if ext == "":
                exclude_dirs.append(p)
            else:
                exclude_files.append(p)
    return exclude_dirs, exclude_files

def is_excluded(target_path, exclude_dirs, exclude_files):
    """
    Return True if target_path is excluded by exact file match or by being within an excluded directory.
    """
    target_path = os.path.normcase(target_path)
    for ex_file in exclude_files:
        if os.path.normcase(target_path) == os.path.normcase(ex_file):
            return True
    # Directory containment check
    for ex_dir in exclude_dirs:
        ex_dir_nc = os.path.normcase(ex_dir.rstrip(os.sep))
        if target_path == ex_dir_nc or target_path.startswith(ex_dir_nc + os.sep):
            return True
    return False

def copy_folder_contents_to_txt(
    output_dir,
    include_dirs,
    include_files,
    exclude_dirs,
    exclude_files,
    output_filename_prefix="output_code",
    max_chars_per_file=4_000_000,
):
    """
    Write folder trees and file contents into TXT files under output_dir.
    include_dirs: list of absolute directory paths to walk
    include_files: list of absolute file paths to include
    exclude_dirs / exclude_files: lists of absolute paths to exclude
    """
    os.makedirs(output_dir, exist_ok=True)

    output_file_index = 1
    current_char_count = 0
    output_file = None
    written_files = set()  # avoid duplicates

    def get_output_file():
        nonlocal output_file_index, current_char_count, output_file
        if output_file:
            output_file.close()
        output_file_path = os.path.join(output_dir, f"{output_filename_prefix}_{output_file_index}.txt")
        output_file = open(output_file_path, 'w', encoding='utf-8')
        current_char_count = 0
        print(f"[info] Creating output file: {output_file_path}")
        return output_file

    def write_chunk(text):
        nonlocal output_file_index, current_char_count, output_file
        if output_file is None:
            get_output_file()
        # rotate file if needed
        if current_char_count + len(text) > max_chars_per_file:
            output_file_index += 1
            get_output_file()
        output_file.write(text)
        current_char_count += len(text)

    def list_and_collect_files(root_dir):
        """
        Produce tree listing lines and list of files to process for a single root_dir,
        respecting exclusions.
        """
        tree_lines = []
        files = []

        # tree header
        tree_lines.append(f"\n--- Struktur Folder ({os.path.abspath(root_dir)}{os.sep}) ---\n")

        for root, dirs, filenames in os.walk(root_dir):
            abs_root = os.path.abspath(root)

            # Remove excluded subdirs from traversal
            dirs[:] = [d for d in dirs if not is_excluded(os.path.join(abs_root, d), exclude_dirs, exclude_files)]
            if is_excluded(abs_root, exclude_dirs, exclude_files):
                # Skip this directory completely
                continue

            relative_path = os.path.relpath(abs_root, root_dir)
            level = 0 if relative_path == '.' else relative_path.count(os.sep)
            indent = '    ' * level

            display_name = os.path.basename(abs_root) if level > 0 else (os.path.basename(root_dir) or root_dir)
            tree_lines.append(f"{indent}{display_name}/\n")

            subindent = '    ' * (level + 1)
            for fname in filenames:
                file_abs = os.path.join(abs_root, fname)
                if is_excluded(file_abs, exclude_dirs, exclude_files):
                    continue
                tree_lines.append(f"{subindent}{fname}\n")
                display_rel = os.path.relpath(file_abs, root_dir)
                files.append((file_abs, display_rel))
        return tree_lines, files

    # Start writing
    get_output_file()

    # 1) Handle directory roots (with subtree)
    for dir_root in include_dirs:
        tree_lines, files_to_process = list_and_collect_files(dir_root)

        for line in tree_lines:
            write_chunk(line)
        write_chunk("\n--- Isi File ---\n")

        for fpath, rel_disp in files_to_process:
            normf = os.path.normcase(os.path.abspath(fpath))
            if normf in written_files:
                continue
            written_files.add(normf)

            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                file_info = f"\n--- Nama File: {rel_disp} ---\n"
                write_chunk(file_info)
                write_chunk(content + "\n")
            except Exception as e:
                write_chunk(f"\n--- Gagal membaca file: {rel_disp} ({e}) ---\n")

    # 2) Handle explicit single-file roots
    if include_files:
        write_chunk(f"\n--- File Tunggal ({len(include_files)} file) ---\n")
        write_chunk("--- Isi File ---\n")
    for fpath in include_files:
        if is_excluded(fpath, exclude_dirs, exclude_files):
            continue
        normf = os.path.normcase(os.path.abspath(fpath))
        if normf in written_files:
            continue
        written_files.add(normf)
        disp = os.path.basename(fpath)
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            file_info = f"\n--- Nama File: {disp} ---\n"
            write_chunk(file_info)
            write_chunk(content + "\n")
        except Exception as e:
            write_chunk(f"\n--- Gagal membaca file: {disp} ({e}) ---\n")

    if output_file:
        output_file.close()
    print("[done] Finished. Output files are in:", output_dir)

if __name__ == "__main__":
    # Base folder is the script directory
    script_path = os.path.abspath(__file__)
    base_folder = os.path.dirname(script_path)

    # Where output files go (default: next to the script)
    output_dir = base_folder

    # Load include/exclude lists
    include_raw = read_lines(os.path.join(base_folder, "user_paths.txt"))
    exclude_raw = read_lines(os.path.join(base_folder, "user_exceptions.txt"))

    # If user_paths.txt is empty/missing, fallback to scanning the script folder
    if not include_raw:
        print("[warn] user_paths.txt not found or empty. Defaulting to current folder.")
        include_raw = ["."]
    else:
        print(f"[info] Loaded {len(include_raw)} include path(s) from user_paths.txt")

    print(f"[info] Loaded {len(exclude_raw)} exclusion path(s) from user_exceptions.txt" if exclude_raw else "[info] No exclusions.")

    # Resolve to absolute paths
    include_abs = [resolve_path(p, base_folder) for p in include_raw]
    exclude_abs = [resolve_path(p, base_folder) for p in exclude_raw]

    # Partition includes into dirs/files; also allow heuristic for non-existing & no suffix -> treat as dir
    include_dirs, include_files = [], []
    for p in include_abs:
        if os.path.isdir(p):
            include_dirs.append(p)
        elif os.path.isfile(p):
            include_files.append(p)
        else:
            root, ext = os.path.splitext(p)
            if ext == "":
                print(f"[warn] Directory not found (treating as dir): {p}")
                if os.path.isdir(p):
                    include_dirs.append(p)
                else:
                    # keep but it won't produce output; warn
                    print(f"[warn] Skipped non-existent directory: {p}")
            else:
                print(f"[warn] File not found: {p}")

    # Prepare exclusions (split to dir/file lists, normalize)
    ex_dirs_raw, ex_files_raw = split_exclusions(exclude_abs)
    # Normalize casing & path for Windows-friendly comparisons
    ex_dirs = [os.path.normpath(os.path.abspath(d)) for d in ex_dirs_raw]
    ex_files = [os.path.normpath(os.path.abspath(f)) for f in ex_files_raw]

    if not include_dirs and not include_files:
        print("[error] Nothing to process. Check user_paths.txt entries.")
    else:
        copy_folder_contents_to_txt(
            output_dir=output_dir,
            include_dirs=include_dirs,
            include_files=include_files,
            exclude_dirs=ex_dirs,
            exclude_files=ex_files,
            output_filename_prefix="output_code",
            max_chars_per_file=4_000_000,
        )
