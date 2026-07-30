#!/usr/bin/env python3

"""
Given workflow search criteria (libraries, analysisRunId, workflow name/version/status),
find matching workflow runs from the Workflow Manager API.

Used by:
- glueSucceededEventsToDraftUpdate: finding existing DRAFT runs for this service to update
- populateDraftData: finding upstream SUCCEEDED workflows to collect outputs as inputs

"""
# Standard imports
from typing import List

# Local imports
from orcabus_api_tools.workflow import (
    get_workflow_runs_from_metadata
)
from orcabus_api_tools.workflow.models import WorkflowRunDetail

# Globals
# Terminal states that indicate a run has been superseded or is no longer relevant
NON_SUCCEEDED_TERMINATED_STATUS_LIST = [
    'FAILED',
    'ABORTED',
    'RESOLVED'
]


def handler(event, context):
    """
    Query the Workflow Manager API for workflow runs matching the given criteria.

    Input:
      {
        "workflowName": "oncoanalyser-wgts-rna",   # Required
        "workflowVersion": "1.0.0",                # Optional
        "status": "DRAFT" | "SUCCEEDED" | ...,     # Optional
        "libraries": [{"libraryId": "L1234"}],     # Conditional (required if no analysisRunId)
        "analysisRunId": "anr.xxx",                # Conditional (required if no libraries)
        "rgidList": ["RGID1", "RGID2"]             # Optional
      }

    Output:
      {"workflowRunList": [...]}  — sorted by orcabusId descending (most recent first)
      {"workflowRunList": []}     — if no match or newer run supersedes

    :param event: Input event with search criteria
    :param context: Lambda context (unused)
    :return: Dictionary with workflowRunList
    """

    # Get the workflow type, name is mandatory
    workflow_name = event['workflowName']
    workflow_version = event.get('workflowVersion', None)

    # Workflow state
    workflow_status = event.get('status', None)

    # Get the libraries / and/or the analysis run id
    analysis_run_id = event.get('analysisRunId', None)
    libraries = event.get('libraries', [])
    rgid_list = event.get('rgidList', None)

    # Check not both analysis run id and libraries are empty/None
    if analysis_run_id is None and not libraries:
        raise ValueError("Either analysisRunId or libraries must be provided")

    # Build library_id_list from libraries input
    library_id_list = list(map(
        lambda library_iter_: library_iter_['libraryId'],
        libraries
    )) if libraries else []

    # Query the Workflow Manager API for matching workflow runs
    workflows_list: List[WorkflowRunDetail]
    workflows_list = get_workflow_runs_from_metadata(
        analysis_run_id=analysis_run_id,
        workflow_name=workflow_name,
        workflow_version=workflow_version,
        library_id_list=library_id_list,
        rgid_list=rgid_list
    )

    # Filter to workflow state if provided
    if workflow_status is not None:
        # DRAFT deduplication: when looking for SUCCEEDED runs,
        # check if a newer non-terminated run supersedes them
        if (
            workflow_status == 'SUCCEEDED' and
            len(workflows_list) > 1
        ):
            active_workflows = list(filter(
                lambda workflow_run_iter: workflow_run_iter['currentState']['status'] not in NON_SUCCEEDED_TERMINATED_STATUS_LIST,
                workflows_list
            ))

            if active_workflows:
                recent_run_status = sorted(
                    active_workflows,
                    key=lambda workflow_iter_: workflow_iter_['currentState']['orcabusId'],
                    reverse=True
                )[0]['currentState']['status']

                if (
                    recent_run_status != workflow_status and
                    recent_run_status not in NON_SUCCEEDED_TERMINATED_STATUS_LIST
                ):
                    return {
                        "workflowRunList": []
                    }

        # Filter by the requested status
        workflows_list = list(filter(
            lambda workflow_iter_: workflow_iter_['currentState']['status'] == workflow_status,
            workflows_list
        ))

    if len(workflows_list) == 0:
        return {
            "workflowRunList": []
        }

    # Return results sorted by orcabusId descending (most recent first)
    return {
        "workflowRunList": sorted(
            workflows_list,
            key=lambda workflow_iter_: workflow_iter_['orcabusId'],
            reverse=True
        )
    }
