# Running Workflow Validations

- Version: 1.0
- Contact: Alexis Lucattini, [alexisl@unimelb.edu.au](mailto:alexisl@unimelb.edu.au)

This SOP describes how to run workflow validations for the Oncoanalyser WGTS RNA pipeline.

- [Introduction](#introduction)
- [Requirements](#requirements)
- [Procedure](#procedure)
- [Expected Outputs](#expected-outputs)
- [Validation Criteria](#validation-criteria)


## Introduction

When deploying a new version of the Oncoanalyser WGTS RNA pipeline (new workflow version or parameter changes),
validation runs should be performed against known test datasets to confirm expected behaviour.

## Requirements

- AWS credentials for the beta/gamma environment
- Access to the OrcaBus Portal
- A known test dataset with expected outcomes (e.g. SEQC-II RNA library)
- The pipeline version to validate has been deployed (see [PM.OWR.2][sop_2_rel_path])

## Procedure

1. **Identify test libraries** — Use the standard validation RNA library.

2. **Submit a validation DRAFT event** — Follow [PM.OWR.1][sop_1_rel_path] to submit a DRAFT event targeting the new pipeline version:
   ```json5
   {
     "payload": {
       "version": "<PAYLOAD_VERSION>",
       "data": {
         "engineParameters": {
           "pipelineId": "<NEW_PIPELINE_ID>"
         }
       }
     }
   }
   ```

3. **Monitor execution** — Track the workflow run through the OrcaBus Portal or AWS Step Functions console. Ensure it transitions through DRAFT → READY → SUBMITTED → SUCCEEDED.

4. **Compare outputs** — Compare the analysis outputs against the expected reference outputs for the test dataset.

## Expected Outputs

The Oncoanalyser WGTS RNA pipeline produces:
- ISOFOX gene expression results
- Fusion detection results
- RNA-based variant calls
- Quality control metrics

## Validation Criteria

A validation run is considered successful when:
1. The workflow run reaches SUCCEEDED status without manual intervention.
2. All expected output files are present in the output URI.
3. Key metrics (gene expression correlation, fusion detection sensitivity) are within acceptable ranges of the reference run.
4. No unexpected errors or warnings appear in the execution logs.

If validation fails, consult [PM.OWR.5 - Troubleshooting][sop_5_rel_path] for guidance.


[sop_1_rel_path]: ../PM.OWR.1/PM.OWR.1-ManualPipelineExecution.md
[sop_2_rel_path]: ../PM.OWR.2/PM.OWR.2-NewPipelineDeployment.md
[sop_5_rel_path]: ../PM.OWR.5/PM.OWR.5-TroubleShooting.md
