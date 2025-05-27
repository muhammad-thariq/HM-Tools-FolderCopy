import os

def copy_folder_contents_to_txt(base_folder, output_filename_prefix="output_code", max_chars_per_file=4000000, specific_folders=None, exclude_folders=None):
    """
    Menyalin struktur folder, nama file, dan isi file dari folder sumber ke file TXT.
    Jika ukuran file TXT melebihi batas, file TXT baru akan dibuat.
    Dapat menyalin folder spesifik dan mengecualikan folder tertentu.

    Args:
        base_folder (str): Jalur ke folder dasar (parent dari script).
        output_filename_prefix (str): Awalan nama untuk file TXT output.
        max_chars_per_file (int): Batas karakter per file TXT. Default 4,000,000 karakter.
        specific_folders (list): Daftar jalur folder (relatif terhadap base_folder) yang akan disalin.
                                Jika None atau kosong, semua folder akan disalin.
        exclude_folders (list): Daftar jalur folder (relatif terhadap base_folder) yang akan dikecualikan.
    """
    output_file_index = 1
    current_char_count = 0
    output_file = None # Initialize to None

    def get_output_file():
        nonlocal output_file_index, current_char_count, output_file
        if output_file:
            output_file.close()
        output_file_path = os.path.join(base_folder, f"{output_filename_prefix}_{output_file_index}.txt")
        output_file = open(output_file_path, 'w', encoding='utf-8')
        current_char_count = 0
        print(f"Membuat file output baru: {output_file_path}")
        return output_file

    output_file = get_output_file() # Get the first output file

    # Convert exclude_folders to absolute paths for easier comparison
    abs_exclude_folders = [os.path.abspath(os.path.join(base_folder, ef)) for ef in exclude_folders] if exclude_folders else []

    # Determine the actual root(s) for walking
    walk_roots = []
    if specific_folders:
        for sf in specific_folders:
            abs_path = os.path.abspath(os.path.join(base_folder, sf))
            if os.path.isdir(abs_path): # Ensure it's a valid directory
                walk_roots.append(abs_path)
            else:
                print(f"Peringatan: Folder spesifik '{sf}' (full path: {abs_path}) tidak ditemukan atau bukan direktori. Akan diabaikan.")
    else:
        walk_roots.append(base_folder)

    if not walk_roots:
        print("Tidak ada folder yang valid untuk disalin. Proses dibatalkan.")
        output_file.close()
        return

    try:
        for walk_root in walk_roots:
            # Write structure header for each root
            output_file.write(f"\n--- Struktur Folder ({os.path.basename(walk_root)}/) ---\n")
            output_file.flush()
            current_char_count += len(f"\n--- Struktur Folder ({os.path.basename(walk_root)}/) ---\n")

            # Collect tree structure and file contents for the current walk_root
            tree_lines = []
            files_to_process = [] # List of (filepath, relative_path_for_display)

            for root, dirs, files in os.walk(walk_root):
                abs_root = os.path.abspath(root)

                # Check for exclusion
                if any(abs_root.startswith(ex_path) for ex_path in abs_exclude_folders):
                    dirs[:] = [] # Skip subdirectories
                    continue

                # Calculate level relative to the current walk_root
                relative_path = os.path.relpath(root, walk_root)
                level = relative_path.count(os.sep) if relative_path != '.' else 0 # '.' is root level
                indent = '    ' * level

                display_name = os.path.basename(root)
                if not display_name and level == 0: # Handle case where walk_root is a drive root or empty string
                    display_name = os.path.basename(walk_root) if os.path.basename(walk_root) else walk_root

                tree_lines.append(f"{indent}{display_name}/\n")
                subindent = '    ' * (level + 1)
                for f in files:
                    tree_lines.append(f"{subindent}{f}\n")
                    files_to_process.append((os.path.join(root, f), os.path.relpath(os.path.join(root, f), base_folder))) # Store full path and path relative to base_folder for display

            # Write collected tree structure
            for line in tree_lines:
                if current_char_count + len(line) > max_chars_per_file:
                    output_file_index += 1
                    output_file = get_output_file()
                output_file.write(line)
                current_char_count += len(line)
            output_file.write("\n")
            current_char_count += 1 # For the newline

            # Write file contents for the current walk_root
            output_file.write("--- Isi File ---\n")
            output_file.flush()
            current_char_count += len("--- Isi File ---\n")

            for filepath, display_rel_path in files_to_process:
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    file_info = f"\n--- Nama File: {display_rel_path} ---\n" # Use relative path for display
                    file_content = f"{content}\n"

                    if current_char_count + len(file_info) + len(file_content) > max_chars_per_file:
                        output_file_index += 1
                        output_file = get_output_file()

                    output_file.write(file_info)
                    output_file.write(file_content)
                    current_char_count += len(file_info) + len(file_content)

                except Exception as e:
                    error_message = f"\n--- Gagal membaca file: {display_rel_path} ({e}) ---\n"
                    if current_char_count + len(error_message) > max_chars_per_file:
                        output_file_index += 1
                        output_file = get_output_file()
                    output_file.write(error_message)
                    current_char_count += len(error_message)

    finally:
        if output_file:
            output_file.close()
        print(f"Proses selesai. File output disimpan di folder yang sama dengan script.")

if __name__ == "__main__":
    script_path = os.path.abspath(__file__)
    base_folder = os.path.dirname(script_path)

    print("Selamat datang di Code Copier!")
    print(f"Folder dasar (tempat script ini berada) adalah: {base_folder}")
    user_choice = input("Apakah Anda ingin (a)uto (copy semua folder dan subfolder) atau (s)pesifik (tentukan folder yang akan disalin/dikecualikan)? Masukkan 'a' atau 's': ").lower().strip()

    specific_folders_to_include = []
    folders_to_exclude = []

    if user_choice == 'a':
        print("Memulai mode otomatis...")
        copy_folder_contents_to_txt(base_folder)
    elif user_choice == 's':
        print("\nMode Spesifik dipilih.")
        print("Masukkan jalur folder yang ingin Anda **sertakan**, pisahkan dengan spasi. Contoh: 'src data' (kosongkan jika ingin menyertakan semua).")
        specific_input = input("Folder yang akan disertakan: ").strip()
        if specific_input:
            specific_folders_to_include = specific_input.split()

        print("\nMasukkan jalur folder yang ingin Anda **kecualikan**, pisahkan dengan spasi. Contoh: 'node_modules build' (kosongkan jika tidak ada yang dikecualikan).")
        exclude_input = input("Folder yang akan dikecualikan: ").strip()
        if exclude_input:
            folders_to_exclude = exclude_input.split()
        
        # If no specific folders are provided but exclude folders are, assume "all" are included
        if not specific_folders_to_include and folders_to_exclude:
            print("Anda memilih untuk tidak menyertakan folder spesifik, tetapi ada folder yang dikecualikan. Ini berarti semua folder akan dipertimbangkan, kecuali yang dikecualikan.")
        elif not specific_folders_to_include and not folders_to_exclude:
            print("Tidak ada folder spesifik atau pengecualian yang diberikan. Akan menyalin semua folder di folder dasar (mode otomatis).")
            
        print(f"\nRingkasan pilihan Anda:")
        print(f"Folder yang akan disalin: {specific_folders_to_include if specific_folders_to_include else 'Semua'}")
        print(f"Folder yang akan dikecualikan: {folders_to_exclude if folders_to_exclude else 'Tidak ada'}")
        
        copy_folder_contents_to_txt(
            base_folder,
            specific_folders=specific_folders_to_include,
            exclude_folders=folders_to_exclude
        )
    else:
        print("Pilihan tidak valid. Silakan masukkan 'a' atau 's'.")
