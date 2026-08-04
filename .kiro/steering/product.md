# Product: Oncoanalyser WGTS RNA Pipeline Manager

## Summary

This is an OrcaBus microservice that manages the lifecycle of the **Oncoanalyser WGTS RNA pipeline** — a somatic RNA analysis pipeline that performs RNA-based variant calling, gene expression analysis, and fusion detection using the Oncoanalyser toolchain (ISOFOX) on ICAv2.

The service handles orchestration on ICAv2 (Illumina Connected Analytics v2) via Nextflow workflows. It follows the standard ICAv2-centric Pipeline Architecture used across OrcaBus. This is a **non-downstream (top-level) service** — it has no upstream pipeline dependencies and is triggered directly by analysis events. It runs in parallel with Dragen WGTS RNA (both consume FASTQ inputs independently).

## Core Responsibilities

- Accept `WorkflowRunStateChange` DRAFT events and validate/populate them into READY events
- Submit READY events to ICAv2 as `Icav2WesRequest` events via a Step Functions state machine
- Monitor ICAv2 analysis state changes and convert them to `WorkflowRunUpdate` events
- Validate draft schemas against a registered JSON schema before promotion
- Perform post-schema validation of engine parameters and URI formats
- Convert BAM inputs to FASTQ via ECS tasks when required (research use only)

## Event Flow

```
DRAFT event (WorkflowRunStateChange)
  → populate draft data (Step Functions)
  → validate draft schema
  → post-schema validation (engine params, URIs)
  → emit READY event
  → submit to ICAv2 WES
  → monitor ICAv2 state changes
  → emit WorkflowRunUpdate events
```

## Input Modes

The pipeline accepts two input modes (via `oneOf` in the draft schema):

- **Primary (FASTQ)**: `fastqListRows` — array of FASTQ read pairs. This is the default production path.
- **Alternative (BAM)**: `bamUri` — a pre-aligned BAM file. Research use only context; BAMs are converted to FASTQ via ECS tasks before submission.

## Upstream / Downstream

- **Upstream**: None (non-downstream service — triggered directly by analysis events, uses FASTQ inputs)
- **Downstream**: Oncoanalyser WGTS DNA-RNA
- **Key dependencies**: ICAv2 WES Manager, Workflow Manager

## Environments

Deploys to `beta`, `gamma`, and `prod` via AWS CodePipeline. The toolchain account hosts the CodePipeline; application stacks deploy cross-account.
