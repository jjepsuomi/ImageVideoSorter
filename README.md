# ImageVideoSorter
Simple Python-function for sorting all unsorted image/video/other-files based on EXIF-data date into nice temporal folder structure.

This code originates from the practical problem of having a large number of image/video data scattered into iPhone and iCloud and the difficulty of exporting them into Windows PC into temporally organized folders.

Specifically, this code will implement the following: 

1. Given an input folder location, the code scans recursively for all possible files in the given folder.
2. The function will check the capture date info from image/video EXIF-data and will produce a list of folders named as MM-YYYY based on unique month/year capture dates in the image/video data files. Also, additional "Others" folder is created for all other files which do not have the EXIF data available.
3. The code will create copies of image/video files which have the EXIF-capture date available, rename gthe files with naming convention YYYYMMDD-HHMMSS (capture date) and move the file to suitable temporal folder location (MM-YYYY).
4. Lastly, the code will produce some verification stats (to visually validate that all files were processed).
