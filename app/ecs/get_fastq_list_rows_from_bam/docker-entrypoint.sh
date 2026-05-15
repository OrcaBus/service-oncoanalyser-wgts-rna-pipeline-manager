#!/usr/bin/env bash

set -euo pipefail

: '
Get fastq list row ids from bam

Collect the ID from @RG\tID given a samtools header,
We overwrite the SM as the sample name provided in the inputs
We also overwrite the LB as the library id provided in the inputs
We then write this file to the cache dir as a json so that we can then "map" the bam_to_fastq step

We want to know the read counts per readgroup and the filesizes per readgroup
'

echo_stderr(){
  echo "$@" 1>&2
}

get_filemanager_id_from_uri(){
  : '
  Given an s3 uri get the filemanager id of the file
  '
  local s3_uri="${1}"
  local bucket
  local key

  # Get bucket and key
  key="${s3_uri#s3://*/}"
  bucket="${s3_uri#s3:\/\/}"
  bucket="${bucket%/"$key"}"

  curl --show-error --fail-with-body --silent --location \
    --header "Accept: application/json" \
    --header "Authorization: Bearer ${ORCABUS_TOKEN}" \
    --request "GET" \
    "https://file.${HOSTNAME}/api/v1/s3?bucket=$bucket&key=$key" | \
  jq --raw-output \
    '.results[0].s3ObjectId'
}

get_presigned_url(){
  : '
  This will be a filemanager call
  '
  local s3_uri="${1}"
  local s3_object_id

  # Generate an s3 object id
  s3_object_id="$( \
  	get_filemanager_id_from_uri "${s3_uri}" \
  )"

  # Return presigned values
  curl --show-error --fail-with-body --silent --location \
    --header "Accept: application/json" \
    --header "Authorization: Bearer ${ORCABUS_TOKEN}" \
    --request "GET" \
    "https://file.${HOSTNAME}/api/v1/s3/presign/${s3_object_id}" | \
  jq --raw-output
}

generate_access_credentials(){
  : '
  Generate access credentials
  '
  local s3_uri="${1}"
  local output_location="${2}"

  uv run python3 scripts/generate_access_creds.py \
    --uri "${s3_uri}" \
    --destination "${output_location}"
}

check_is_paired_end(){
  : '
  Get presigned url
  '
  local s3_uri="${1}"
  local rgid="${2}"
  local is_paired_end
  local presigned_url

  # Get the presigned url
  presigned_url="$(get_presigned_url "${s3_uri}")"

  is_paired_end="$(
    (
      # Take the header
      samtools view \
        --header-only \
        "${presigned_url}"; \
      # And the first 10000 reads of a given readgroup
      samtools view \
        --no-header \
        --read-group "${rgid}" \
        "${presigned_url}" | \
      head -n10000 \
    ) | \
    samtools view \
      --count \
      --require-flags 1 \
      - \
  )"

  if [[ "${is_paired_end}" -gt "0" ]]; then
    return 0
  else
    return 1
  fi
}


# Get input vars
if [[ -z "${BAM_URI}" ]]; then
  echo_stderr "BAM_URI not found"
  exit 1
fi

# Get output vars
if [[ -z "${OUTPUT_URI}" ]]; then
  echo_stderr "OUTPUT_URI not found"
  exit 1
fi

# Set hostname
HOSTNAME="$( \
  aws ssm get-parameter \
    --name "${HOSTNAME_SSM_PARAMETER_NAME}" \
    --output 'json' | \
  jq --raw-output '.Parameter.Value'
)"

# Set orcabus token
ORCABUS_TOKEN="$( \
  aws secretsmanager get-secret-value \
    --secret-id "${ORCABUS_TOKEN_SECRET_ID}" \
    --output json \
    --query SecretString | \
  jq --raw-output 'fromjson | .id_token' \
)"

# Set ICAV2_ACCESS_TOKEN environment variable
ICAV2_ACCESS_TOKEN="$( \
  aws secretsmanager get-secret-value \
    --secret-id "${ICAV2_ACCESS_TOKEN_SECRET_ID}" \
    --output json \
    --query SecretString | \
  jq --raw-output
)"

# Export icav2 env vars (as its used by python script)
export ICAV2_BASE_URL="https://ica.illumina.com/ica/rest"
export ICAV2_ACCESS_TOKEN

# Globals
SPLIT_PREFIX="rgid"
THREADS=8
BAM_INDEX_FILE_NAME="bam_index.bai"
ICAV2_ACCESS_CREDS_FILE="access_creds.sh"

# Get the presigned url of the bam file
presigned_url="$(get_presigned_url "${BAM_URI}")"

# Set argument arrays
SAMTOOLS_STATS_ARGS_ARRAY=( \
  "--split" "RG" \
  "--split-prefix" "${SPLIT_PREFIX}" \
  "--threads" "${THREADS}" \
  "-X" \
  "${presigned_url}" \
  "${BAM_INDEX_FILE_NAME}" \
)

# Download bam index
wget \
  --quiet \
  --output-document "${BAM_INDEX_FILE_NAME}" \
  "$(get_presigned_url "${BAM_URI}.bai")"

# Generate access credentials script
generate_access_credentials "$(dirname "${OUTPUT_URI}")/" "${ICAV2_ACCESS_CREDS_FILE}"

# Get RGIDs
rgid_list="$(
  samtools view \
    --header-only \
    "${presigned_url}" | \
  grep '^@RG' | \
  jq \
    --raw-input --raw-output \
    '
      split("\t") |
      map(select(startswith("ID:"))) |
      map(gsub("^ID:";""))[]
    ' \
)"

# Samtools stats by read group
samtools stats \
  "${SAMTOOLS_STATS_ARGS_ARRAY[@]}" \
  1> /dev/null

# Collect the read count for each rgid and upload the jsonl to the OUTPUT_URI
lane=0
while read -r rgid; do
  # Add one to lane
  lane="$(( lane + 1 ))"

  # Check if is paired end data for this read group
  if check_is_paired_end "${BAM_URI}" "${rgid}"; then
    is_paired_end="true"
  else
    is_paired_end="false"
  fi

  # Write to jsonl
  jq --null-input \
    --raw-output --compact-output \
    --argjson read_count "$(grep $'^SN\tsequences:' "${SPLIT_PREFIX}_${rgid}.bamstat" | cut -f3)" \
    --arg rgid "${rgid}" \
    --argjson lane "${lane}" \
    --argjson is_paired_end "${is_paired_end}" \
    '
      {
        "rgid": $rgid,
        "lane": $lane,
        "readCount": $read_count,
        "isPairedEnd": $is_paired_end
      }
    '
done <<< "${rgid_list}" | \
( \
	# shellcheck disable=SC1090
	source "${ICAV2_ACCESS_CREDS_FILE}"; \
	aws s3 cp - "${OUTPUT_URI}" \
)
