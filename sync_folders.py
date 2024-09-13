import os
import shutil
import time
import hashlib
import argparse
import logging
import sys

# Function to log and print a message
def response_message(message, type):
    """
    Log and print a response message.

    Args:
        message (str): The message to log and print.
        type (str): The type of message ('info', 'warning', 'error'). If invalid, defaults to 'info'.
    """
    if type == "info": logging.info(message)
    elif type == "warning": logging.warning(message)
    elif type == "error": logging.error(message)
    else: logging.info(message) # In case of a programming typo
    print(message)

# Function to calculate SHA-256 checksum of a file
def calculate_sha256(file_path):
    """
    Calculate the SHA-256 checksum of a file.

    Args:
        file_path (str): Path to the file for which to compute the checksum.

    Returns:
        str: SHA-256 checksum of the file in hexadecimal format.
    """
    try:
        with open(file_path, 'rb') as file:
            hash_sha256 = hashlib.sha256()
            for chunk in iter(lambda: file.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        message = f"Error calculating SHA-256 for file '{file_path}': {e}"
        response_message(message, "error")

# Function to replicate directory structure and synchronize files
def sync_folders(source, replica):
    """
    Synchronize files and directories from the source folder to the replica folder.

    Args:
        source (str): Path to the source folder.
        replica (str): Path to the replica folder.
    """
    add_files_and_directories(source, replica)
    remove_files_and_directories(source, replica)

# Function to add files and directories
def add_files_and_directories(source, replica):
    """
    Add files and directories from the source to the replica.

    Args:
        source (str): Path to the source directory.
        replica (str): Path to the replica directory.
    """
    global count
    try:
        # Walk through the source directory
        for source_dirpath, _, filenames in os.walk(source):
            # Determine the relative path and create corresponding path in the replica
            rel_path = os.path.relpath(source_dirpath, source)
            replica_dirpath = os.path.join(replica, rel_path)
            replica_dirpath = os.path.normpath(replica_dirpath)

            # Create the directory in the replica if it does not exist
            if not os.path.exists(replica_dirpath):
                try:
                    count += 1
                    os.makedirs(replica_dirpath)
                    message = f"Directory created: {replica_dirpath}"
                    response_message(message, "info")
                except Exception as e:
                    message = f"Error creating {replica_dirpath}: {e}"
                    response_message(message, "warning")

            # Copy files from source to replica
            for file in filenames:
                source_file = os.path.join(source_dirpath, file)
                replica_file = os.path.join(replica_dirpath, file)
                replica_file = os.path.normpath(replica_file)

                # Copy file if it does not exist in replica or has different checksum
                if not os.path.exists(replica_file) or calculate_sha256(source_file) != calculate_sha256(replica_file):
                    try:
                        count += 1
                        shutil.copy2(source_file, replica_file)
                        message = f"File copied: {source_file}"
                        response_message(message, "info")
                    except Exception as e:
                        message = f"Error copying {source_file} to {replica_dirpath}: {e}"
                        response_message(message, "warning")

    except Exception as e:
        message = f"Unknown error adding files or directories: {e}. The script will stop."
        response_message(message, "error")
        sys.exit(1)

# Function to remove files and directories
def remove_files_and_directories(source, replica):
    """
    Remove files and directories from the replica that are no longer in the source folder.

    Args:
        source (str): Path to the source folder.
        replica (str): Path to the replica folder.
    """
    global count
    try:
        # Walk through the replica directory in reverse order to handle files before directories
        for replica_dirpath, _, filenames in os.walk(replica, topdown=False):
            # Determine the relative path and corresponding path in the source
            rel_path = os.path.relpath(replica_dirpath, replica)
            source_dirpath = os.path.join(source, rel_path)
            source_dirpath = os.path.normpath(source_dirpath)

            # Remove files that are not present in the source
            for file in filenames:
                replica_file = os.path.join(replica_dirpath, file)
                source_file = os.path.join(source_dirpath, file)
                replica_file = os.path.normpath(replica_file)

                if not os.path.exists(source_file):
                    try:
                        count += 1
                        os.remove(replica_file)
                        message = f"File removed: {replica_file}"
                        response_message(message, "info")
                    except Exception as e:
                        message = f"Error removing {replica_file}: {e}"
                        response_message(message, "warning")

            # Remove directories that are no longer present in the source
            if not os.path.exists(source_dirpath):
                try:
                    count += 1
                    shutil.rmtree(replica_dirpath)
                    message = f"Directory removed: {replica_dirpath}"
                    response_message(message, "info")
                except Exception as e:
                    message = f"Error removing {replica_dirpath}: {e}"
                    response_message(message, "warning")

    except Exception as e:
        message = f"Unknown error removing files or directories: {e}. The script will stop."
        response_message(message, "error")
        sys.exit(1)

# Function to validate paths
def validate_paths(source, replica, log_file):
    """
    Validate the source, replica, and log file paths provided by the user.

    Args:
        source (str): Path to the source folder.
        replica (str): Path to the replica folder.
        log_file (str): Path to the log file.

    Raises:
        SystemExit: If any path is invalid or cannot be accessed.
    """

    source = os.path.abspath(source)
    replica = os.path.abspath(replica)
    log_file = os.path.abspath(log_file)

    # Check if source folder exists
    if not os.path.isdir(source):
        message = f"Source folder path '{source}' does not exist."
        print(message)
        sys.exit(1)

    # Check if replica folder exists; if not, attempt to create it
    if not os.path.isdir(replica):
        try:
            os.makedirs(replica)
        except Exception as e:
            message = f"Error: Could not create the replica folder on path '{replica}'."
            print(message)
            print(f"Exception: {e}")
            sys.exit(1)
    
    # Ensure log file is not inside source or replica directories
    if os.path.commonpath([log_file, source]) == source or os.path.commonpath([log_file, replica]) == replica:
        message = (f"Error: Log file '{log_file}' cannot be placed inside the source folder or replica folder. \n"
                   "Please provide a log file path that is outside both the source and replica directories.")
        print(message)
        sys.exit(1)
    
    # Set default log file path if not provided
    try:
        with open(log_file, 'a') as f:
            pass
    except:
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, 'w') as f:
                pass
        except Exception as e:
            message = f"Error: Could not open log file '{log_file}' for writing."
            print(message)
            print(f"Exception: {e}")
            sys.exit(1)

# Main function to handle periodic synchronization
def main():
    """
    Main function to handle argument parsing and periodic synchronization.
    """
    parser = argparse.ArgumentParser(description="Synchronize two folders")
    parser.add_argument("source", help="Path to the source folder.")
    parser.add_argument("replica", help="Path to the replica folder. The replica folder will be created if it does not exist in your directory.")
    parser.add_argument("log_file", help="Path to the log file. The log file will be created if it does not exist in your directory.")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds.")

    args = parser.parse_args()

    print(f"Source folder path: {args.source}")
    print(f"Replica folder path: {args.replica}")
    print(f"Log file path: {args.log_file}")
    print(f"Interval: {args.interval}")
    yes_no = input("These are the inputs you chose. Do you wish to proceed? (y/n) ")
    while yes_no not in ["y","n"]:
        yes_no = input("Invalid answer. These are the inputs you chose. Do you wish to proceed? (y/n) ")
    if yes_no == "y":
        pass
    elif yes_no == "n":
        sys.exit(0)

    validate_paths(args.source, args.replica, args.log_file)

    logging.basicConfig(filename=args.log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    global count
    try:
        while True:
            message = "Starting synchronization process..."
            response_message(message, "info")
            count = 0
            sync_folders(args.source, args.replica)
            if count == 0:
                message = "No files changed"
                response_message(message, "info")
            message = f"Synchronization process completed. Running it again in {args.interval} seconds..."
            response_message(message, "info")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        message = "Program interrupted by user. Synchronization completed."
        response_message(message, "info")
        sys.exit(1)
    except Exception as e:
        message = f"An unexpected error occurred: {e}"
        response_message(message, "error")
        sys.exit(1)

if __name__ == "__main__":
    main()