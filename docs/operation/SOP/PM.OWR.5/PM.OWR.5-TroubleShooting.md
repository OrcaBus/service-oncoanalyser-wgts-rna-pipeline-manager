# Trouble Shooting

- Version: 1.0
- Contact: Alexis Lucattini, [alexisl@unimelb.edu.au](mailto:alexisl@unimelb.edu.au)

Most processes within the Oncoanalyser WGTS RNA Orchestration use AWS Step Functions to manage the workflow.
We post all Step Function errors to the #alerts-prod Slack channel, a Centre staff member can
then click on the offending Step Function link in the Slack message to be taken to the AWS Step Functions console to investigate further.

- [Analysis Stuck in DRAFT state](#analysis-stuck-in-draft-state)
  - [Waiting for Upstream Dragen WGTS DNA](#waiting-for-upstream-dragen-wgts-dna)
  - [Payload Mismatch](#payload-mismatch)
- [Analysis Stuck in READY state](#analysis-stuck-in-ready-state)
- [Analysis Fails to Start](#analysis-fails-to-start)
  - [Project Not Set Up Correctly](#project-not-set-up-correctly)
  - [Invalid Pipeline ID](#invalid-pipeline-id)
  - [Data Not Available](#data-not-available)
- [Common Oncoanalyser RNA Failures](#common-oncoanalyser-rna-failures)
  - [Memory Issues](#memory-issues)
  - [FASTQ Input Issues](#fastq-input-issues)
  - [BAM-to-FASTQ Conversion Failures](#bam-to-fastq-conversion-failures)

## Analysis Stuck in DRAFT state

If the analysis is stuck in DRAFT mode, there may be a couple of reasons for this.
To determine which issue is causing the problem, head to the [AWS Step Functions Console][aws_step_functions_console_prod]
in the production account and look for any RUNNING executions in the `orca-oncoanalyser-wgts-rna--populateDraftData` step function.

### Waiting for Upstream Dragen WGTS DNA

The most common reason for a stuck DRAFT is that the upstream Dragen WGTS DNA pipeline has not yet completed.
The glue state machine (`glueSucceededEventsToDraftUpdate`) will automatically update the DRAFT run when the
upstream pipeline succeeds. Check the status of the corresponding Dragen WGTS DNA workflow run in the OrcaBus Portal.

If the upstream run has already SUCCEEDED but the DRAFT was not updated, you may need to manually provide
the missing inputs via a WorkflowRunUpdate event.

### Payload Mismatch

If the populate-draft-data execution completed but the run remains in DRAFT, check the workflow run comments
in the OrcaBus Portal. The state machine writes a comment listing any missing required fields.

You may need to manually provide the missing fields via a WorkflowRunUpdate DRAFT event as discussed in [SOP 1][sop_1_rel_path].

## Analysis Stuck in READY state

If the analysis is stuck in READY state, it is likely that the translation from the READY event to the ICAv2 WES event has failed.
This is a rare occurrence, but may be due to transient issues with the ICAv2 WES Manager.

Check the `orca-oncoanalyser-wgts-rna--readyEventToIcav2WesRequestEvent` state machine for failed executions.
You can redrive the execution from the AWS Step Functions console once the issue is resolved.

## Analysis Fails to Start

The ICAv2 WES Manager may fail to create an analysis for any of the following reasons:

### Project Not Set Up Correctly

Common issues with new projects:

- Ensure that the ICAv2 Production Service User has been added to the project with the correct permissions.
- Ensure that the Notifications Channels have been set up correctly for the project.

### Invalid Pipeline ID

> The pipeline id specified is not available in the project id

Mitigate with:

```shell
icav2 projects enter <project_id>
icav2 projectpipeline link <pipeline_id>
```

You will need to create a new workflow run after this change.

### Data Not Available

> Data .x. is not available in the project id <project_id>

If the FASTQ data is not accessible in the ICAv2 project, you may need to:

1. Confirm the FASTQ URIs exist in S3
2. Ensure the data is linked to the ICAv2 project
3. Check that the FASTQ files have not been archived to Glacier

## Common Oncoanalyser RNA Failures

### Memory Issues

If the pipeline fails with an out-of-memory error, this may be due to high-coverage RNA samples.
Check the analysis logs for memory-related failure messages.

### FASTQ Input Issues

If the pipeline fails because FASTQ inputs are not accessible:

1. Verify the FASTQ URIs are valid and accessible
2. Check that the Fastq Glue service has resolved the FASTQ list rows correctly
3. Confirm the FASTQ files are not in ORA format that requires decompression

### BAM-to-FASTQ Conversion Failures

If the pipeline requires BAM-to-FASTQ conversion (via ECS tasks) and this step fails:

1. Check the ECS task logs in CloudWatch for the specific error
2. Verify the input BAM file is accessible and not corrupted
3. Ensure the ECS cluster has sufficient capacity

[aws_step_functions_console_prod]: https://472057503814.ap-southeast-2.console.aws.amazon.com/states/home?region=ap-southeast-2#/statemachines
[sop_1_rel_path]: ../PM.OWR.1/PM.OWR.1-ManualPipelineExecution.md
