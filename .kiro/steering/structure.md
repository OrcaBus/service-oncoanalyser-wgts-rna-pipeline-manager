# Project Structure

## Top-Level Layout

```
├── app/                        # Application logic (lambdas, ECS tasks, step functions, schemas)
├── bin/deploy.ts               # CDK entry point — initialises stateless + stateful root stacks
├── infrastructure/             # CDK infrastructure code
│   ├── stage/                  # Per-environment application stacks
│   └── toolchain/              # CodePipeline stacks (deploy to beta/gamma/prod)
├── test/                       # CDK/cdk-nag compliance tests
├── docs/                       # Draw.io exports, SOPs, workflow studio exports
├── .kiro/steering/             # AI steering documents
├── cdk.json                    # CDK app config (entry: `pnpx ts-node bin/deploy.ts`)
├── package.json / pnpm-workspace.yaml
└── Makefile                    # Common developer commands
```

## `app/` — Application Logic

```
app/
├── ecs/                        # ECS task definitions
│   ├── bam_to_fastq/          # Converts BAM files to FASTQ format
│   └── get_fastq_list_rows_from_bam/  # Extracts FASTQ list rows from BAM inputs
├── event-schemas/              # JSON schemas for event validation (versioned directory structure)
│   ├── complete-data-draft/
│   │   ├── 2025.08.05/
│   │   │   └── complete-data-draft-schema.json
│   │   └── 2026.05.12/
│   │       └── complete-data-draft-schema.json
│   └── data-succeeded/
├── lambdas/                    # Python Lambda functions
│   ├── add_populate_draft_comment_py/
│   ├── add_wes_failure_comment_py/
│   ├── check_ntsm_internal_py/
│   ├── collect_read_count_stats_py/
│   ├── compare_payload_py/
│   ├── convert_fastq_list_rows_object_to_cache_uri_py/
│   ├── convert_icav2_wes_event_to_wrsc_event_py/
│   ├── convert_ready_event_inputs_to_icav2_wes_event_inputs_py/
│   ├── find_latest_workflow_py/
│   ├── generate_wru_event_object_with_merged_data_py/
│   ├── get_draft_payload_py/
│   ├── get_fastq_id_list_from_fastq_rgid_list_py/
│   ├── get_fastq_id_list_from_rgid_list_py/
│   ├── get_fastq_list_rows_from_rgid_list_py/
│   ├── get_fastq_rgids_from_library_id_py/
│   ├── get_libraries_py/
│   ├── get_metadata_tags_py/
│   ├── get_missing_schema_fields_py/
│   ├── get_qc_summary_stats_from_rgid_list_py/
│   ├── get_workflow_run_object_py/
│   ├── post_schema_validation_py/
│   └── validate_draft_complete_schema_py/
└── step-functions-templates/   # ASL JSON Step Functions definitions
    ├── icav2_wes_event_to_wrsc_event_sfn_template.asl.json
    ├── populate_draft_data_sfn_template.asl.json
    ├── ready_event_to_icav2_wes_request_event_sfn_template.asl.json
    └── validate_draft_data_and_put_ready_event_sfn_template.asl.json
```

### Lambda Naming Convention

Lambda directories use `snake_case` with a `_py` suffix (e.g. `get_libraries_py`). The CDK infrastructure converts camelCase names to snake_case automatically via `camelCaseToSnakeCase()`.

### Lambda Pattern

- Single file per Lambda, named `<function_name>.py`
- Must export `handler(event, context) -> Dict[str, Any]`
- Extensive docstrings describing input/output event shapes
- Business logic only — no AWS SDK calls for infrastructure wiring (IAM, SSM lookups are CDK-managed)
- Commented-out `if __name__ == "__main__"` blocks for local testing

## `infrastructure/` — CDK Code

```
infrastructure/
├── stage/
│   ├── config.ts               # Environment configs (beta, gamma, prod)
│   ├── constants.ts            # All app constants (SSM paths, event names, workflow versions, S3 refs)
│   ├── interfaces.ts           # Shared TypeScript interfaces for the stack
│   ├── stateless-application-stack.ts
│   ├── stateful-application-stack.ts
│   ├── ecs/                    # ECS task construct builders
│   ├── lambda/                 # Lambda construct builders
│   │   ├── index.ts            # buildAllLambdas() — iterates lambdaNameList
│   │   └── interfaces.ts       # Lambda name list + requirements map
│   ├── step-functions/         # Step Function construct builders
│   ├── event-rules/            # EventBridge rule builders
│   ├── event-targets/          # EventBridge target builders
│   ├── event-schemas/          # Schema registry construct builders
│   ├── ssm/                    # SSM parameter construct builders
│   └── utils/                  # Shared utilities (camelCase ↔ kebab/snake conversions)
└── toolchain/
    ├── constants.ts            # Toolchain-specific constants
    ├── stateless-stack.ts      # CodePipeline for stateless deployments
    └── stateful-stack.ts       # CodePipeline for stateful deployments
```

### Infrastructure Patterns

- Each resource type (lambda, step-functions, event-rules, etc.) has its own `index.ts` (builder) and `interfaces.ts` (types)
- All constants (SSM paths, event names, bucket names, workflow versions) live in `infrastructure/stage/constants.ts` — do not hardcode these elsewhere
- Lambdas are built with `PythonUvFunction` from `@orcabus/platform-cdk-constructs`
- IAM permissions are granted inline in `infrastructure/stage/lambda/index.ts` based on per-Lambda requirement flags in `interfaces.ts`
- `NagSuppressions` are added inline with justification comments wherever `cdk-nag` rules are suppressed

## Key Conventions

- **Event source**: `orcabus.oncoanalyserwgtsrna`
- **Event bus**: `OrcaBusMain`
- **SSM prefix**: `/orcabus/workflows/oncoanalyser-wgts-rna/`
- **Stack prefix**: `orca-oncoanalyser-wgts-rna`
- **Workflow name**: `oncoanalyser-wgts-rna`
- **Lambda runtime**: Python 3.14 on ARM64
- **Upstream workflow name**: None (non-downstream service — uses FASTQ inputs directly)
- When adding a new Lambda: add the directory under `app/lambdas/<name>_py/`, register it in `infrastructure/stage/lambda/interfaces.ts`, and declare its IAM requirement flags there
- When adding a new workflow version: update `WORKFLOW_VERSION_TO_DEFAULT_ICAV2_PIPELINE_ID_MAP` and related maps in `constants.ts`
