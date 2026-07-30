#!/usr/bin/env python3

"""
Get the BAM output from a dragen-wgts-dna workflow run given a portal run id and phenotype.
For the RNA pipeline, we extract the tumor RNA BAM URI from the upstream workflow outputs.
"""

# Standard imports
from typing import Optional, Literal, List
from pathlib import Path

# Layer imports
from orcabus_api_tools.filemanager import get_file_manager_request_response_results
from orcabus_api_tools.filemanager.models import FileObject

# Globals
Phenotype = Literal["TUMOR", "NORMAL"]
PHENOTYPE_LIST: List[Phenotype] = ["TUMOR", "NORMAL"]


def get_bam_from_dragen_workflow(portal_run_id: str, phenotype: Phenotype) -> Optional[FileObject]:
    """Get the BAM file from a dragen workflow run for the given phenotype"""
    if phenotype == 'TUMOR':
        bam_file = next(filter(
            lambda file_iter: file_iter['key'].endswith("_tumor.bam"),
            get_file_manager_request_response_results(
                endpoint="api/v1/s3/attributes",
                params={
                    "portalRunId": portal_run_id,
                }
            )
        ))
        return bam_file
    elif phenotype == 'NORMAL':
        bam_file = next(filter(
            lambda file_iter: file_iter['key'].endswith("_normal.bam"),
            get_file_manager_request_response_results(
                endpoint="api/v1/s3/attributes",
                params={
                    "portalRunId": portal_run_id,
                }
            )
        ))
        return bam_file
    raise ValueError("Phenotype must be either 'TUMOR' or 'NORMAL'")


def handler(event, context):
    """
    Given a portal run id and phenotype, get the BAM file URI from the upstream dragen workflow
    :param event:
    :param context:
    :return:
    """

    # Get inputs from the event
    portal_run_id = event.get('portalRunId', None)
    phenotype: Phenotype = event.get('phenotype', None)

    if phenotype not in PHENOTYPE_LIST:
        raise ValueError(f"Phenotype must be one of {PHENOTYPE_LIST}")

    bam_file_obj = get_bam_from_dragen_workflow(portal_run_id, phenotype=phenotype)

    output_uri = f"s3://{bam_file_obj['bucket']}/{str(Path(bam_file_obj['key']))}"

    # Return the output keyed by phenotype
    if phenotype == 'TUMOR':
        return {
            "dragenTumorRnaBamUri": output_uri
        }

    return {
        "dragenNormalRnaBamUri": output_uri
    }
