import os
import re

def rename_files_in_directory(directory_path):
    """
    Renames all files in a given directory by adding a prefix.

    Args:
        directory_path (str): The path to the directory containing the files.
        prefix (str): The prefix to add to each filename.
    """
    try:
        # Get a list of all files in the directory
        for filename in os.listdir(directory_path):
            # Construct the full old file path
            old_file_path = os.path.join(directory_path, filename)

            # Check if it's a file (not a subdirectory)
            if os.path.isfile(old_file_path):
                # Construct the new filename with the prefix
                new_filename = re.sub(r"Five Iron Melee 30_\d{4}", "Five Iron Melee 30 ", filename)
                #new_filename = re.sub(r"_\d{4}", "", filename)
                # Construct the full new file path
                new_file_path = os.path.join(directory_path, new_filename)

                # Rename the file
                os.rename(old_file_path, new_file_path)
                print(f"Renamed '{filename}' to '{new_filename}'")

    except FileNotFoundError:
        print(f"Error: Directory not found at '{directory_path}'")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
# Replace 'C:\\Your\\Directory\\Path' with the actual path to your directory
target_directory = 'C:\\Users\\benji\\Documents\\slp2mp4'
rename_files_in_directory(target_directory)