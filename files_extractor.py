import mimetypes
import os
import shutil
import subprocess

import magic
from rich import print


def extract_objects_from_pcap(pcap_path):
    # Print the name of the pcap file
    pcap_name = os.path.basename(pcap_path)
    print(f"[yellow]Processing file: {pcap_name}")

    # Ensure the output directory exists
    output_dir = f'output/{pcap_name}/objects'
    os.makedirs(output_dir, exist_ok=True)

    # Construct the tshark command
    tshark_command = [
        'tshark',
        '-r', pcap_path,
        '--export-objects', f'http,{output_dir}'
    ]

    # Run the tshark command
    result = subprocess.run(tshark_command, capture_output=True, text=True)

    # Check for errors
    if result.returncode != 0:
        print(f"[red bold]Error running tshark: {result.stderr}")
    else:
        # Example usage
        categorize_files(output_dir)
        print(f"[green bold]Objects extracted to {output_dir}")


def categorize_files(folder_path):
    # Ensure the output directories exist
    categories = ['images', 'html', 'css', 'js', 'ico', 'php', 'asp', 'json']
    for category in categories:
        os.makedirs(os.path.join(folder_path, category), exist_ok=True)

    # Initialize the magic library
    mime = magic.Magic(mime=True)

    m_types = set()

    # Iterate over files in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            # Check for file extension first
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                # If no extension or unknown type, use python-magic
                mime_type = mime.from_file(file_path)

            # Determine the category based on MIME type
            if mime_type:
                m_types.add(mime_type)
                if mime_type.startswith('image/'):
                    category = 'images'
                elif mime_type == 'text/html':
                    category = 'html'
                elif mime_type == 'text/css':
                    category = 'css'
                elif mime_type == 'application/javascript':
                    category = 'js'
                elif mime_type == 'image/vnd.microsoft.icon':
                    category = 'ico'
                elif mime_type == 'application/json':
                    category = 'json'
                else:
                    continue  # Skip files that don't match any category

                # Move the file to the appropriate category folder
                shutil.move(file_path, os.path.join(folder_path, category, file_name))
    print(f"[cyan]Mime types: {m_types}")





def extract_keys_from_pcap(pcap_path):
    # Print the name of the pcap file
    pcap_name = os.path.basename(pcap_path)
    print(f"[yellow]Processing file: {pcap_name}")

    # Ensure the output directory exists
    output_dir = f'output/{pcap_name}/keys'
    os.makedirs(output_dir, exist_ok=True)

    # Construct the tshark command
    tshark_command = [
        'tshark',
        '-r', pcap_path,
        '--export-tls-session-keys', f'{output_dir}/key'
    ]

    # Run the tshark command
    result = subprocess.run(tshark_command, capture_output=True, text=True)

    # Check for errors
    if result.returncode != 0:
        print(f"[red bold]Error running tshark: {result.stderr}")
    else:
        print(f"[green bold]Objects extracted to {output_dir}")


def extract_pcap(pcap_path):
    extract_objects_from_pcap(pcap_path)
    # extract_keys_from_pcap(pcap_path)


# Example usage
extract_pcap('data/GeekLounge.pcap')
