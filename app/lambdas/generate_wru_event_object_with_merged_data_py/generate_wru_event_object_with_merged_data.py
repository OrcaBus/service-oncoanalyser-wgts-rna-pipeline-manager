#!/usr/bin/env python3

"""
Generate a WRU event object with merged data from upstream pipelines
"""
# Layer imports
from orcabus_api_tools.workflow import (
    get_workflow_run_from_portal_run_id
)


def handler(event, context):
    """
    Generate WRU event object with merged data
    :param event:
    :param context:
    :return:
    """

    # Get the event inputs
    portal_run_id = event.get("portalRunId", None)
    libraries = event.get("libraries", None)
    payload = event.get("payload", None)
    upstream_data = event.get("upstreamData", {})

    # Get the bam uri from upstream dragen-wgts-dna
    dragen_tumor_rna_bam_uri = upstream_data.get('dragenTumorRnaBamUri', None)

    # Create a copy of the draft workflow run object to update
    draft_workflow_run = get_workflow_run_from_portal_run_id(
        portal_run_id=portal_run_id
    )

    # Make a copy
    draft_workflow_update = draft_workflow_run.copy()

    # Remove 'currentState' and replace with 'status'
    draft_workflow_update['status'] = draft_workflow_update.pop('currentState')['status']

    # Add in the libraries if provided
    if libraries is not None:
        draft_workflow_update["libraries"] = list(map(
            lambda library_iter: {
                "libraryId": library_iter['libraryId'],
                "orcabusId": library_iter['orcabusId'],
                "readsets": library_iter.get('readsets', [])
            },
            libraries
        ))

    # Check if the draft payload already has the fields we would update
    if (
            payload['data'].get("inputs", {}).get("tumorRnaBamUri", None) is not None
    ):
        # Return the OG, we dont want to overwrite existing data
        draft_workflow_update["payload"] = {
            "version": payload['version'],
            "data": payload['data']
        }
        return {
            "workflowRunUpdate": draft_workflow_update
        }

    # Merge the upstream data into the draft payload
    new_data_object = payload['data'].copy()
    if new_data_object.get("inputs", None) is None:
        new_data_object["inputs"] = {}
    new_data_object["inputs"]["tumorRnaBamUri"] = dragen_tumor_rna_bam_uri

    # Drop null keys in inputs
    new_data_object["inputs"] = dict(filter(
        lambda kv_iter_: kv_iter_[1] is not None,
        new_data_object["inputs"].copy().items()
    ))

    # Update the payload
    draft_workflow_update["payload"] = {
        "version": payload['version'],
        "data": new_data_object
    }

    return {
        "workflowRunUpdate": draft_workflow_update
    }
