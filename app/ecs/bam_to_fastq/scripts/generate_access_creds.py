#!/usr/bin/env python3

"""
Given a s3 uri, generate access credentials
"""

# Standard imports
import argparse
from pathlib import Path
from typing import cast

# Wrapica imports
from libica.openapi.v3 import AwsTempCredentials
from wrapica.project_data import (
    convert_uri_to_project_data_obj,
    get_credentials_access_for_project_folder
)


def write_credentials_to_file(
        aws_credentials: AwsTempCredentials,
        destination: Path
):
    """
    Create a shell script that can be sourced
    :param aws_credentials:
    :param destination:
    :return:
    """
    # Ensure output location is writeable
    destination.parent.mkdir(parents=True, exist_ok=True)

    # Create a little shell script to be sourced
    with open(destination, 'w') as f_handle:
        f_handle.write(f"export AWS_REGION={aws_credentials.region}\n")
        f_handle.write(f"export AWS_ACCESS_KEY_ID={aws_credentials.access_key}\n")
        f_handle.write(f"export AWS_SECRET_ACCESS_KEY={aws_credentials.secret_key}\n")
        f_handle.write(f"export AWS_SESSION_TOKEN={aws_credentials.session_token}\n")


def get_args():
    """
    Get arguments from system
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--uri', type=str)
    parser.add_argument('--destination', type=str)
    return parser.parse_args()


def main():
    """
    Run generate access creds script
    :return:
    """
    # Get args
    args = get_args()

    # Get uri as project data object
    project_data_folder = convert_uri_to_project_data_obj(
        data_uri=args.uri,
        create_data_if_not_found=True
    )

    # Set output
    destination = Path(args.destination)

    # Get aws credentials
    aws_credentials = cast(
        AwsTempCredentials,
        get_credentials_access_for_project_folder(
            project_id=project_data_folder.project_id,
            folder_id=project_data_folder.data.id
        )
    )

    # Write credentials to destination
    write_credentials_to_file(
        aws_credentials=aws_credentials,
        destination=destination
    )


if __name__ == '__main__':
    main()
