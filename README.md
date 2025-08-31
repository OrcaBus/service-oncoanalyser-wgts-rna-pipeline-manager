Oncoanalyser WGTS RNA Pipeline Orchestration Service
================================================================================

- [Description](#description)
    - [Summary](#summary)
    - [Events Overview](#events-overview)
    - [API Endpoints](#api-endpoints)
    - [Consumed Events](#consumed-events)
    - [Published Events](#published-events)
    - [Ready Event Example](#ready-event-example)
        - [Manually Validating Schemas,](#manually-validating-schemas)
        - [Release management :construction:](#release-management-construction)
- [Infrastructure \& Deployment](#infrastructure--deployment)
    - [Stateful](#stateful)
    - [Stateless](#stateless)
    - [CDK Commands](#cdk-commands)
    - [Stacks](#stacks)
- [Development](#development)
    - [Project Structure](#project-structure)
    - [Setup](#setup)
        - [Requirements](#requirements)
        - [Install Dependencies](#install-dependencies)
        - [First Steps](#first-steps)
    - [Conventions](#conventions)
    - [Linting \& Formatting](#linting--formatting)
    - [Testing](#testing)
- [Glossary \& References](#glossary--references)

Description
--------------------------------------------------------------------------------

### Summary

This is the Oncoanalyser WGTS RNA Pipeline Management service,
responsible for orchestrating the Oncoanalyser WGTS RNA analyses.

The pipeline runs on ICAv2 through Nextflow (version 24.10)

### Events Overview

**Ready Event**
We listen to READY WRSC events where the workflow name is equal to `oncoanalyser-wgts-rna`

**ICAv2 WES Analysis State Change**
We then parse ICAv2 Analysis State Change events to update the state of the workflow in our service.

![events-overview](docs/draw-io-exports/oncoanalyser-wgts-rna-pipeline.drawio.svg)

### API Endpoints

This service provides a RESTful API following OpenAPI conventions.
The Swagger documentation of the production endpoint is available here:

### Consumed Events

| Name / DetailType             | Source             | Schema Link   | Description                           |
|-------------------------------|--------------------|---------------|---------------------------------------|
| `WorkflowRunStateChange`      | `orcabus.any`      | <schema link> | READY statechange // TODO             |
| `Icav2WesAnalysisStateChange` | `orcabus.icav2wes` | <schema link> | ICAv2 WES Analysis State Change event |

### Published Events

| Name / DetailType        | Source                        | Schema Link   | Description           |
|--------------------------|-------------------------------|---------------|-----------------------|
| `WorkflowRunStateChange` | `orcabus.oncoanalyserwgtsrna` | <schema link> | Analysis state change |

### Ready Event Example

Ready event minimal example

<details>

<summary>Click to expand</summary>

```json5
{
  "EventBusName": "OrcaBusMain",
  "Source": "orcabus.manual",
  "DetailType": "WorkflowRunUpdate",
  "Detail": {
    "status": "READY",
    "timestamp": "2025-08-29T03:44:03Z",
    "workflow": {
      "name": "oncoanalyser-wgts-rna",
      "version": "2.1.0"
    },
    "workflowRunName": "umccr--automated--oncoanalyser-wgts-rna--2-1-0--20250829e69122bd",
    "portalRunId": "20250829e69122bd",  // pragma: allowlist secret
    "libraries": [
      {
        "orcabusId": "lib.01JVM8CX3SC5QBY0GJYFX1QRW7",
        "libraryId": "L2500568",
        "readsets": [
          {
            "rgid": "CGCCATATCT+ATCTCCGGTC.1.250530_A01052_0264_BHFGKTDSXF",
            "orcabusId": "fqr.01JWM22657AFRXAGR6RG18W94P"
          }
        ]
      }
    ],
    "payload": {
      "version": "2025.08.05",
      "data": {
        "tags": {
          "libraryId": "L2500568",
          "subjectId": "HCC1395",
          "individualId": "SBJ00480",
          "fastqRgidList": [
            "GGACTTGG+CGTCTGCG.2.241024_A00130_0336_BHW7MVDSXC"
          ]
        },
        "inputs": {
          "mode": "wgts",
          "groupId": "L2500568",
          "subjectId": "L2500568",
          "sampleId": "L2500568",
          "fastqListRows": [
            {
              "rgid": "CGCCATATCT+ATCTCCGGTC.1.250530_A01052_0264_BHFGKTDSXF",
              "rglb": "L2500568",
              "rgsm": "L2500568",
              "lane": 1,
              "rgcn": "UMCCR",
              "rgds": "Library ID: L2500568 / Sequenced on 30 May 2025 at UMCCR / Phenotype: tumor / Assay: ISTRL / Type: WTS",
              "rgdt": "2025-05-30",
              "rgpl": "Illumina",
              "read1FileUri": "s3://test-data-503977275616-ap-southeast-2/testdata/input/fastq/L2500568/L2500568_S1_L001_R1_001.fastq.ora",
              "read2FileUri": "s3://test-data-503977275616-ap-southeast-2/testdata/input/fastq/L2500568/L2500568_S1_L001_R2_001.fastq.ora"
            }
          ],
          "genome": "GRCh38_umccr",
          "genomeVersion": "38",
          "genomeType": "alt",
          "forceGenome": true,
          "refDataHmfDataPath": "s3://reference-data-503977275616-ap-southeast-2/refdata/hartwig/hmf-reference-data/hmftools/hmf_pipeline_resources.38_v2.1.0--1/",
          "genomes": {
            "GRCh38_umccr": {
              "fasta": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/GRCh38_full_analysis_set_plus_decoy_hla.fa",
              "fai": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/samtools_index/1.16/GRCh38_full_analysis_set_plus_decoy_hla.fa.fai",
              "dict": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/samtools_index/1.16/GRCh38_full_analysis_set_plus_decoy_hla.fa.dict",
              "img": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/bwa_index_image/0.7.17-r1188/GRCh38_full_analysis_set_plus_decoy_hla.fa.img",
              "bwamem2Index": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/bwa-mem2_index/2.2.1/",
              "gridssIndex": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/gridss_index/2.13.2/",
              "starIndex": "s3://reference-data-503977275616-ap-southeast-2/refdata/genomes/GRCh38_umccr/star_index/gencode_38/2.7.3a/"
            }
          }
        },
        "engineParameters": {
          "projectId": "ea19a3f5-ec7c-4940-a474-c31cd91dbad4",
          "pipelineId": "ab6e1d62-1b5a-4b24-86b8-81ccf4bdc7a2",
          "outputUri": "s3://pipeline-dev-cache-503977275616-ap-southeast-2/byob-icav2/development/analysis/oncoanalyser-wgts-rna/20250829e69122bd/",
          "logsUri": "s3://pipeline-dev-cache-503977275616-ap-southeast-2/byob-icav2/development/logs/oncoanalyser-wgts-rna/20250829e69122bd/",
          "cacheUri": "s3://pipeline-dev-cache-503977275616-ap-southeast-2/byob-icav2/development/cache/oncoanalyser-wgts-rna/20250829e69122bd/"
        }
      }
    }
  }
}
```

</details>

#### Manually Validating Schemas,

We have generated JSON Schemas for the complete draft event which you can find in the [
`./app/event-schemas`](app/event-schemas) directory.

You can interactively check if your DRAFT or READY event matches the schema using the following links: :construction:

#### Making your own draft events with BASH / JQ

There may be circumstances where you wish to generate WRSC events manually, the below is a quick solution for
generating a draft for a somatic wgts dna workflow. Omit setting the TUMOR_LIBRARY_ID variabler for running a germline
only workflow.

The draft populator step function will also pull necessary fastq files out of archive.

<details>

<summary>Click to expand</summary>

```shell
# Globals
EVENT_BUS_NAME="OrcaBusMain"
DETAIL_TYPE="WorkflowRunUpdate"
SOURCE="orcabus.manual"

WORKFLOW_NAME="oncoanalyser-wgts-rna"
WORKFLOW_VERSION="2.1.0"
EXECUTION_ENGINE="ICA"

PAYLOAD_VERSION="2025.08.05"

# Glocals
LIBRARY_ID="L2500568"

# Functions
get_hostname_from_ssm(){
  aws ssm get-parameter \
    --name "/hosted_zone/umccr/name" \
    --output json | \
  jq --raw-output \
    '.Parameter.Value'
}

get_orcabus_token(){
  aws secretsmanager get-secret-value \
    --secret-id orcabus/token-service-jwt \
    --output json \
    --query SecretString | \
  jq --raw-output \
    'fromjson | .id_token'
}

get_pipeline_id_from_workflow_version(){
  local workflow_version="$1"
  aws ssm get-parameter \
    --name "/orcabus/workflows/oncoanalyser-wgts-rna/pipeline-ids-by-workflow-version/${workflow_version}" \
    --output json | \
  jq --raw-output \
    '.Parameter.Value'
}

get_library_obj_from_library_id(){
  local library_id="$1"
  curl --silent --fail --show-error --location \
    --header "Authorization: Bearer $(get_orcabus_token)" \
    --url "https://metadata.$(get_hostname_from_ssm)/api/v1/library?libraryId=${library_id}" | \
  jq --raw-output \
    '
      .results[0] |
      {
        "libraryId": .libraryId,
        "orcabusId": .orcabusId
      }
    '
}

generate_portal_run_id(){
  echo "$(date -u +'%Y%m%d')$(openssl rand -hex 4)"
}

get_linked_libraries(){
  local library_id="$1"
  local tumor_library_id="${2-}"

  linked_library_obj=$(get_library_obj_from_library_id "$library_id")

  if [ -n "$tumor_library_id" ]; then
    tumor_linked_library_obj=$(get_library_obj_from_library_id "$tumor_library_id")
  else
    tumor_linked_library_obj="{}"
  fi

  jq --null-input --compact-output --raw-output \
    --argjson libraryObj "$linked_library_obj" \
    --argjson tumorLibraryObj "$tumor_linked_library_obj" \
    '
      [
          $libraryObj,
          $tumorLibraryObj
      ] |
      # Filter out empty values, tumorLibraryId is optional
      # Then write back to JSON
      map(select(length > 0))
    '
}

get_workflow(){
  local workflow_name="$1"
  local workflow_version="$2"
  local execution_engine="$3"
  local execution_engine_pipeline_id="$4"

  # Ignore this for now, return a default workflow object
  jq --null-input --raw-output --compact-output \
    '
      {
        "orcabusId": "wfl.01K3QDJECAKYXZ6XRHQVW2MG2X",
        "name": "oncoanalyser-wgts-rna",
        "version": "2.1.0",
        "executionEngine": "ICA",
      }
    '

  #  curl --silent --fail --show-error --location \
  #    --header "Authorization: Bearer $(get_orcabus_token)" \
  #    --url "https://workflow.$(get_hostname_from_ssm)/api/v1/workflow?workflowName=${workflow_name}&workflowVersion=${workflow_version}&executionEngine=${execution_engine}&executionEnginePipelineId=${execution_engine_pipeline_id}" | \
  #  jq --compact-output --raw-output \
  #    '
  #      .results[0] |
  #      with_entries(
  #        if (.key | startswith("workflow")) then
  #          .key |= (sub("workflow"; "") | ascii_downcase)
  #        else
  #          .
  #        end
  #      )
  #    '
}

# Generate the event
event_cli_json="$( \
  jq --null-input --raw-output \
    --arg eventBusName "$EVENT_BUS_NAME" \
    --arg detailType "$DETAIL_TYPE" \
    --arg source "$SOURCE" \
    --argjson workflow "$(get_workflow \
      "${WORKFLOW_NAME}" "${WORKFLOW_VERSION}" \
      "${EXECUTION_ENGINE}" "$(get_pipeline_id_from_workflow_version "$WORKFLOW_VERSION")" \
    )" \
    --arg payloadVersion "$PAYLOAD_VERSION" \
    --arg portalRunId "$(generate_portal_run_id)" \
    --argjson libraries "$(get_linked_libraries "$LIBRARY_ID" "$TUMOR_LIBRARY_ID")" \
    '
      {
        # Standard fields for the event
        "EventBusName": $eventBusName,
        "DetailType": $detailType,
        "Source": $source,
        # Detail must be a JSON object in string format
        "Detail": (
          {
            "status": "DRAFT",
            "timestamp": (now | todateiso8601),
            "workflow": $workflow,
            "workflowRunName": ("umccr--automated--" + $workflow["name"] + "--" + ($workflow["version"] | gsub("\\."; "-")) + "--" + $portalRunId),
            "portalRunId": $portalRunId,
            "libraries": $libraries,
          } |
          tojson
        )
      } |
      # Now wrap into an "entry" for the CLI
      {
        "Entries": [
          .
        ]
      }
    ' \
)"

aws events put-events --no-cli-pager --cli-input-json "${event_cli_json}"
```

</details>

#### Release management :construction:

The service employs a fully automated CI/CD pipeline that automatically builds and releases all changes to the `main`
code branch.


Infrastructure & Deployment
--------------------------------------------------------------------------------

Short description with diagrams where appropriate.
Deployment settings / configuration (e.g. CodePipeline(s) / automated builds).

Infrastructure and deployment are managed via CDK. This template provides two types of CDK entry points: `cdk-stateless`
and `cdk-stateful`.

### Stateful

- Queues
- Buckets
- Database
- ...

### Stateless

- Lambdas
- StepFunctions

### CDK Commands

You can access CDK commands using the `pnpm` wrapper script.

- **`cdk-stateless`**: Used to deploy stacks containing stateless resources (e.g., AWS Lambda), which can be easily
  redeployed without side effects.
- **`cdk-stateful`**: Used to deploy stacks containing stateful resources (e.g., AWS DynamoDB, AWS RDS), where
  redeployment may not be ideal due to potential side effects.

The type of stack to deploy is determined by the context set in the `./bin/deploy.ts` file. This ensures the correct
stack is executed based on the provided context.

For example:

```sh
# Deploy a stateless stack
pnpm cdk-stateless <command>

# Deploy a stateful stack
pnpm cdk-stateful <command>
```

### Stacks

This CDK project manages multiple stacks. The root stack (the only one that does not include `DeploymentPipeline` in its
stack ID) is deployed in the toolchain account and sets up a CodePipeline for cross-environment deployments to `beta`,
`gamma`, and `prod`.

To list all available stacks, run:

```sh
pnpm cdk-stateless ls
```

Example output:

```sh
OrcaBusStatelessServiceStack
OrcaBusStatelessServiceStack/DeploymentPipeline/OrcaBusBeta/DeployStack (OrcaBusBeta-DeployStack)
OrcaBusStatelessServiceStack/DeploymentPipeline/OrcaBusGamma/DeployStack (OrcaBusGamma-DeployStack)
OrcaBusStatelessServiceStack/DeploymentPipeline/OrcaBusProd/DeployStack (OrcaBusProd-DeployStack)
```

Development
--------------------------------------------------------------------------------

### Project Structure

The root of the project is an AWS CDK project where the main application logic lives inside the `./app` folder.

The project is organized into the following key directories:

- **`./app`**: Contains the main application logic. You can open the code editor directly in this folder, and the
  application should run independently.

- **`./bin/deploy.ts`**: Serves as the entry point of the application. It initializes two root stacks: `stateless` and
  `stateful`. You can remove one of these if your service does not require it.

- **`./infrastructure`**: Contains the infrastructure code for the project:
    - **`./infrastructure/toolchain`**: Includes stacks for the stateless and stateful resources deployed in the
      toolchain account. These stacks primarily set up the CodePipeline for cross-environment deployments.
    - **`./infrastructure/stage`**: Defines the stage stacks for different environments:
        - **`./infrastructure/stage/config.ts`**: Contains environment-specific configuration files (e.g., `beta`,
          `gamma`, `prod`).
        - **`./infrastructure/stage/stack.ts`**: The CDK stack entry point for provisioning resources required by the
          application in `./app`.

- **`.github/workflows/pr-tests.yml`**: Configures GitHub Actions to run tests for `make check` (linting and code
  style), tests defined in `./test`, and `make test` for the `./app` directory. Modify this file as needed to ensure the
  tests are properly configured for your environment.

- **`./test`**: Contains tests for CDK code compliance against `cdk-nag`. You should modify these test files to match
  the resources defined in the `./infrastructure` folder.

### Setup

#### Requirements

```sh
node --version
v22.9.0

# Update Corepack (if necessary, as per pnpm documentation)
npm install --global corepack@latest

# Enable Corepack to use pnpm
corepack enable pnpm

```

#### Install Dependencies

To install all required dependencies, run:

```sh
make install
```

#### First Steps

Before using this template, search for all instances of `TODO:` comments in the codebase and update them as appropriate
for your service. This includes replacing placeholder values (such as stack names).

### Conventions

### Linting & Formatting

Automated checks are enforces via pre-commit hooks, ensuring only checked code is committed. For details consult the
`.pre-commit-config.yaml` file.

Manual, on-demand checking is also available via `make` targets (see below). For details consult the `Makefile` in the
root of the project.

To run linting and formatting checks on the root project, use:

```sh
make check
```

To automatically fix issues with ESLint and Prettier, run:

```sh
make fix
```

### Testing

Unit tests are available for most of the business logic. Test code is hosted alongside business in `/tests/`
directories.

```sh
make test
```

Glossary & References
--------------------------------------------------------------------------------

For general terms and expressions used across OrcaBus services, please see the
platform [documentation](https://github.com/OrcaBus/wiki/blob/main/orcabus-platform/README.md#glossary--references).

Service specific terms:

| Term | Description |
|------|-------------|
| Foo  | ...         |
| Bar  | ...         |
