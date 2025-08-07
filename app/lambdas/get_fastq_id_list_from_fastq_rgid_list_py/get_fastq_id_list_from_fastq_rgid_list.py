#!/usr/bin/env python3

"""
Get the fastq ids from the rgid list

Given the rgid list, return the fastq ids that are associated with these rgids.
"""

# Layer imports
from orcabus_api_tools.fastq import get_fastq_by_rgid


def handler(event, context):
    """
    Given a library id, get the fastq rgids associated with the library.
    :param event:
    :param context:
    :return:
    """
    # Get the fastq rgid list from the event
    fastq_rgid_list = event.get("fastqRgidList", [])

    # Get the fastq ids
    all_fastq_ids = sorted(list(map(
        lambda fastq_rgid_iter_: get_fastq_by_rgid(fastq_rgid_iter_)['id'],
        fastq_rgid_list
    )))

    return {
        "fastqIdList": all_fastq_ids
    }


# if __name__ == "__main__":
#     from os import environ
#     import json
#     environ['AWS_PROFILE'] = 'umccr-production'
#     environ['HOSTNAME_SSM_PARAMETER_NAME'] = '/hosted_zone/umccr/name'
#     environ['ORCABUS_TOKEN_SECRET_ID'] = 'orcabus/token-service-jwt'
#     print(json.dumps(
#         handler(
#             {
#                 "fastqRgidList": [
#                     "GTTCGCCG+CAATGAGC.4.250724_A01052_0269_AHFHWJDSXF"
#                 ]
#             },
#             None
#         ),
#         indent=4
#     ))
#
#     # {
#     #     "fastqIdList": [
#     #         "fqr.01K12NF97VEM0V9K0ABFAEPHNT"
#     #     ]
#     # }
