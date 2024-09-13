# Folder Synchronization Tool

sync_folders_vs is a Python tool designed to synchronize files between a source folder and a replica folder. It ensures that the replica folder is an exact copy of the source folder, including removing files and directories that no longer exist in the source folder.



# Features

- Synchronizes Files and Directories: Copies new or updated files or directories from the source folder to the replica folder.

- Removes Files and Directories: Deletes files and directories in the replica that are no longer present in the source folder.

- Logging: Records synchronization activities and errors to a specified log file.

- Periodic Execution: Supports periodic synchronization at a user-defined interval.

- SHA-256 Checksum: Uses SHA-256 checksums to verify file integrity.



# Setup

Prerequisites:

- Python 3.6 or higher
- No external libraries required


Required Python packages:
  
- os
- shutil
- time
- hashlib
- argparse
- logging
- sys



# Installation

Clone the repository:

    git clone https://github.com/fgama94/sync_folders_vs.git
  
    cd sync_folders_vs



# Usage

After installing the required libraries, you can run the tool from the command line. Here is the general syntax:

    python sync_folders.py <source_folder> <replica_folder> <log_file> <interval>



# Arguments

- source_folder: Path to the source folder you want to synchronize.

- replica_folder: Path to the destination folder where the synchronization will occur.

- log_file: Path to the log file where synchronization details and errors will be recorded.

- interval: Time interval (in seconds) between synchronization checks.



# Example

    python sync_folders.py "C:\path\to\source" "C:\path\to\replica" "C:\path\to\log_file.log" 30

This command will synchronize the folders every 30 seconds and log the activities to log_file.log.



# Error Handling

- Source folder does not exist: The script exits with an error message if the source folder does not exist.

- Replica folder creation: If the replica folder does not exist, the script attempts to create it. Exits with an error if it cannot be created.

- Log File Path Issues: The script ensures the log file is not placed inside the source or replica folders. If there are issues with the log file path, the script will exit with an error message.



# Logging

The script logs information and errors. 

Log entries include timestamps and are saved to the file specified by <log_file>.



# License

This project is licensed under the MIT License. See the LICENSE file for details.
