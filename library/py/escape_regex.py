import sys
import re
import shutil

def escape_regex_chars(pattern):
    special_chars = r'\^$.|?*+()[{\\'
    escaped_pattern = re.sub(fr'([{re.escape(special_chars)}])', r'\\\1', pattern)
    return escaped_pattern

def escape_file(input_file):
    temp_file = input_file + ".tmp"
    backup_file = input_file + ".bak"

    # Create a backup of the input file
    shutil.copyfile(input_file, backup_file)

    with open(input_file, 'r') as file_in, open(temp_file, 'w') as file_out:
        for line in file_in:
            escaped_line = escape_regex_chars(line)
            file_out.write(escaped_line)

    # Create a backup of the input file
    #shutil.copyfile(temp_file, input_file)
    shutil.move(temp_file, input_file)


if __name__=="__main__":
    if len(sys.argv) != 2:
        print("Usage: python escape_regex_chars.py input_file")
        sys.exit(1)
    escape_file(sys.argv[1])