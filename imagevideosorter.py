import os
import shutil
from datetime import datetime
from exif import Image
import exiftool
import numpy as np
from PIL import Image as PilImage, PngImagePlugin
from PIL.PngImagePlugin import PngImageFile
from plum.exceptions import UnpackError  # Import the specific exception


"""
Get EXIF-date-data from image.
"""
def get_capture_date_image(file_path):
    file_ext = file_path.lower().split('.')[-1]
    try:
        if file_ext in ['jpg', 'jpeg', 'JPG', 'JPEG']:
            with open(file_path, 'rb') as image_file:
                image = Image(image_file)
                if image.has_exif and hasattr(image, 'datetime_original'):
                    capture_date = image.datetime_original
                    return datetime.strptime(capture_date, '%Y:%m:%d %H:%M:%S')
        else:
            return None
    except UnpackError as e:
        print(f"UnpackError: {e}")
        return None
    except Exception as e:
        print(f"Exception: {e}")
        return None
    return None

"""
Get EXIF-date-data from video.
"""
def get_capture_date_video(file_path):
    video_date = None
    metadata = None
    with exiftool.ExifToolHelper() as et:
        try:
            metadata = et.get_metadata(file_path)
            if 'QuickTime:CreationDate' in metadata[0]:
                video_date = metadata[0]['QuickTime:CreationDate']
                if isinstance(video_date, str): # Transform to datetime-format
                    video_date = datetime.strptime(video_date, '%Y:%m:%d %H:%M:%S%z')
                video_date = video_date.replace(tzinfo=None)  # Remove the timezone info
            elif 'QuickTime:CreateDate' in metadata[0]:
                video_date = metadata[0]['QuickTime:CreateDate']
                if isinstance(video_date, str): # Transform to datetime-format
                    video_date = datetime.strptime(video_date, '%Y:%m:%d %H:%M:%S')
                video_date = video_date.replace(tzinfo=None)  # Remove the timezone info
        except Exception as e:
            print(f'Exception {e} occurred while attempting to read the metadata of video file: {file_path}.')
            video_date = None
        return video_date


"""
Function for creating photo/video/other folder structure to save all sorted data.
"""
def create_folders(root_path, folder_names):
    """
    Creates folders under the specified root path and adds subfolders to each.

    Parameters:
    root_path (str): The path where new folders should be created.
    folder_names (list): A list of folder names to create.
    """
    subfolders = ["kuvat", "videot", "muut"]

    for folder_name in folder_names:
        # Construct the full path for the new folder
        folder_path = os.path.join(root_path, folder_name)
        
        try:
            # Create the main directory
            os.makedirs(folder_path, exist_ok=True)
            print(f"Created folder: {folder_path}")

            # Create the subfolders
            for subfolder in subfolders:
                subfolder_path = os.path.join(folder_path, subfolder)
                os.makedirs(subfolder_path, exist_ok=True)
                print(f"  Created subfolder: {subfolder_path}")
        except Exception as e:
            print(f"Failed to create folder {folder_path} or its subfolders: {e}")

"""
Utility function for scanning all the files in the input directory to be sorted.
"""
def scan_directory(src_root):
    files = {}
    file_types = {}
    capture_dates = []
    file_index = 1
    # Walk through all folders and files.
    for dirpath, _, filenames in os.walk(src_root):
        for filename in filenames:
            file_ext = filename.lower().split('.')[-1]
            file_path = os.path.join(dirpath, filename)
            capture_date = None
            if file_ext in file_types:
                file_types[file_ext] += 1
            else:
                file_types[file_ext] = 1
            # Check file extension and get capture date if applicable
            if file_ext in ['jpg', 'jpeg', 'JPG', 'JPEG']:
                capture_date = get_capture_date_image(file_path)
            elif file_ext in ['mov', 'MOV']:
                capture_date = get_capture_date_video(file_path)
            if capture_date:
                month_year_str = capture_date.strftime('%Y-%m')  # Format as MM_YYYY
                capture_dates.append(month_year_str)
            print(f'Managed to retrive capture date: {capture_date} for file: {file_path}\n\n')
            # Store file information in the dictionary
            files[file_index] = {
                'filepath': file_path,
                'type': file_ext,
                'capture_date': capture_date # datetime-object
            }
            file_index += 1
    return files, file_types, capture_dates

"""
Function for processing given image/photo/other-file, renaming and copying it to corresponding new location.
"""
def process_file(file, dest_root):
    file_ext = file['type']
    capture_date = file['capture_date'] # datetime object
    filepath = file['filepath']
    filename = os.path.basename(filepath)
    dest_root_others_folder = os.path.join(dest_root, 'Muut')
    new_file_path = None
    if capture_date: # Means there is a capture date, non-None
        date_folder_name = capture_date.strftime('%Y-%m')
        # Format datetime for filename YYYYMMDD-HHMMSS
        new_file_name = str(capture_date.strftime('%Y%m%d-%H%M%S')) + str("." + file_ext)
        # Example base folder path
        # Construct full path for the folder
        dest_root_date_folder = os.path.join(dest_root, date_folder_name)
        # Construct full path for the file
        if file_ext in ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']:
            new_file_path = os.path.join(dest_root_date_folder, 'kuvat', new_file_name)
        elif file_ext in ['mov', 'mp4', 'MOV', 'MP4']:
            new_file_path = os.path.join(dest_root_date_folder, 'videot', new_file_name)
        else:
            new_file_path = os.path.join(dest_root_date_folder, 'muut', new_file_name)
    else:
        if file_ext in ['jpg', 'jpeg', 'png', 'JPG', 'JPEG', 'PNG']:
            new_file_path = os.path.join(dest_root_others_folder, 'kuvat', filename)
        elif file_ext in ['mov', 'mp4', 'MOV', 'MP4']:
            new_file_path = os.path.join(dest_root_others_folder, 'videot', filename)
        else:
            new_file_path = os.path.join(dest_root_others_folder, 'muut', filename)
    # Check if the file already exists
    if os.path.exists(new_file_path):
        base_name, extension = os.path.splitext(new_file_path)
        index = 1
        while True:
            indexed_file_path = f"{base_name}_{index}{extension}"
            if not os.path.exists(indexed_file_path):
                new_file_path = indexed_file_path
                break
            index += 1
    # Copy the file to the destination
    shutil.copy2(filepath, new_file_path)

if __name__ == "__main__":
    
    input_image_video_directory = '/media/jonne/Seagate Expansion Drive/Valokuvia'
    output_root_folder_path = '/media/jonne/Seagate Expansion Drive/Valokuvat_vuosittain'
     # Scan for all files and get file type counts
    all_files, file_types, capture_dates = scan_directory(input_image_video_directory)
    capture_dates.append('Muut') # For all other files, without date info.

    create_folders(output_root_folder_path, np.unique(capture_dates)) # Create the new folder structure based on the scanned files.

    # Process all files accordingly, rename and copy to correct location.
    for key, file in all_files.items():
        print(f'Copying file {key}/{len(all_files)}')
        process_file(file, output_root_folder_path)

    # Validate old and new files, verify all files were processed (visual inspection)
    print(f"Total number of old files found: {len(all_files)}")
    for file_type, count in file_types.items():
        print(f"Number of {file_type} files: {count}")
    all_files, file_types, capture_dates = scan_directory(output_root_folder_path)
    print(f"--- Total number of new files found: {len(all_files)}")
    for file_type, count in file_types.items():
        print(f"Number of {file_type} files: {count}")
    