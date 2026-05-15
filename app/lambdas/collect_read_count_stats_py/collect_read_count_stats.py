#!/usr/bin/env python3

"""
Given a jsonlPath, read and print as a fastq list
"""

# Standard imports
from typing import Dict, List, Union
import json

# Wrapica imports
from wrapica.project_data import (
    convert_uri_to_project_data_obj,
    read_icav2_file_contents_to_string,
)

# Layer imports
from icav2_tools import set_icav2_env_vars


def handler(event, context) -> Dict[str, List[Dict[str, Union[str, int]]]]:
    """
    Given a jsonlPath as input, write as fastqList
    :param event:
    :param context:
    :return:
    """

    # Set env vars
    set_icav2_env_vars()

    # Get inputs
    jsonl_path = event["jsonlPath"]

    # Convert to project data object in ica
    project_data_obj = convert_uri_to_project_data_obj(jsonl_path)

    # Read file contents to string
    jsonl_file_contents = read_icav2_file_contents_to_string(
        project_id=project_data_obj.project_id,
        data_id=project_data_obj.data.id,
    )

    # Get jsonl lines as list of json objects
    fastq_list = [
        json.loads(jsonl_file_content_line)
        for jsonl_file_content_line in jsonl_file_contents.split("\n")[:-1]
    ]

    # Convert jsonl string to list of dicts
    return {
        "fastqList": fastq_list
    }
