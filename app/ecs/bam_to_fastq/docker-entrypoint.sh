#!/usr/bin/env bash

set -euo pipefail

: '
Given a presigned url bam file,
convert to fastq through a stream
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
  curl --fail-with-body --silent --location \
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

get_estimate_file_size_from_read_count(){
  local read_count="${1}"
  jq --null-input \
    --raw-output \
    --argjson read_count "${read_count}" \
    '
      # Multiply total by 151 (estimated read size)
      $read_count * 151 |
      # Reduce by 75% as estimated gzip compression
      . * 0.25 |
      # Convert to int
      round
    '
}

get_content_length(){
  : '
  Get the output content length of a file
  '
  local s3_uri="${1}"
  local bucket
  local key

  # Get bucket and key
  key="${s3_uri#s3://*/}"
  bucket="${s3_uri#s3:\/\/}"
  bucket="${bucket%/"$key"}"

  # Get access credentials to output directory
  # shellcheck disable=SC1090
  source "${ICAV2_ACCESS_CREDS_FILE}"

  aws s3api head-object \
    --bucket "${bucket}" \
    --key "${key}" \
    --output json | \
  jq --raw-output \
    '.ContentLength'
}

# Globals
THREADS=8
ICAV2_ACCESS_CREDS_FILE="access_creds.sh"

# FIFOS
FASTQ_PRE_FIFO="fastq.pre.fifo"
FASTQ_LINE_COUNT_FIFO="fastq.lc.fifo"
FASTQ_FIFO="fastq.fifo"
FASTQ_PRE_2_FIFO="fastq2.pre.fifo"
FASTQ_2_FIFO="fastq2.fifo"
FASTQ_LINE_COUNT_2_FIFO="fastq2.lc.fifo"
FASTQ_GZIP_PRE_FIFO="fastq.gzip.pre.fifo"
FASTQ_GZIP_WC_FIFO="fastq.gzip.wc.fifo"
FASTQ_GZIP_FIFO="fastq.gzip.fifo"
FASTQ_GZIP_PRE_2_FIFO="fastq2.gzip.pre.fifo"
FASTQ_GZIP_WC_2_FIFO="fastq2.gzip.wc.fifo"
FASTQ_GZIP_2_FIFO="fastq2.gzip.fifo"

# Static environment variable checks
if [[ -z "${ICAV2_ACCESS_TOKEN_SECRET_ID:-}" ]]; then
  echo_stderr "ICAV2_ACCESS_TOKEN_SECRET_ID is not set. Exiting."
  exit 1
fi
if [[ -z "${HOSTNAME_SSM_PARAMETER_NAME}" ]]; then
  echo_stderr "HOSTNAME_SSM_PARAMETER_NAME is not set, exiting"
  exit 1
fi
if [[ -z "${ORCABUS_TOKEN_SECRET_ID}" ]]; then
  echo_stderr "Orcabus token secret id not found, exiting"
  exit 1
fi

# Check input vars
if [[ -z "${READ_GROUP_ID-}" ]]; then
  echo_stderr "Cannot find READ_GROUP_ID"
  exit 1
fi
if [[ -z "${READ_COUNT-}" ]]; then
  echo_stderr "Cannot find read count"
  exit 1
fi
if [[ -z "${IS_PAIRED_END-}" ]]; then
  echo_stderr "Is paired end not set"
  exit 1
fi
if [[ -z "${BAM_FILE-}" ]]; then
  echo_stderr "Cannot find BAM_FILE"
  exit 1
fi
# Check output vars
if [[ -z "${FASTQ_OUTPUT_URI-}" ]]; then
  echo_stderr "Cannot find FASTQ_OUTPUT_URI"
  exit 1
fi
# Ensure FASTQ_OUTPUT_2_URI is not null if data is paired end data
if [[ "${IS_PAIRED_END}" == "true" ]]; then
  if [[ -z "${FASTQ_OUTPUT_2_URI-}" ]]; then
    echo_stderr "Cannot find FASTQ_OUTPUT_2_URI and we have paired end data"
    exit 1
  fi
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

# Generate presigned url of s3 file
presigned_url="$(get_presigned_url "${BAM_FILE}")"
est_file_size="$(get_estimate_file_size_from_read_count "${READ_COUNT}")"
generate_access_credentials "$(dirname "${FASTQ_OUTPUT_URI}")/" "${ICAV2_ACCESS_CREDS_FILE}"

FIFOS_ARRAY=(
  "${FASTQ_PRE_FIFO}" \
  "${FASTQ_LINE_COUNT_FIFO}" \
  "${FASTQ_FIFO}" \
  "${FASTQ_GZIP_PRE_FIFO}" \
  "${FASTQ_GZIP_WC_FIFO}" \
  "${FASTQ_GZIP_FIFO}" \
)

# Update fifos if paired end data
if [[ "${IS_PAIRED_END}" == "true" ]]; then
  FIFOS_ARRAY+=(
    "${FASTQ_PRE_2_FIFO}" \
    "${FASTQ_LINE_COUNT_2_FIFO}" \
    "${FASTQ_2_FIFO}" \
    "${FASTQ_GZIP_PRE_2_FIFO}" \
    "${FASTQ_GZIP_WC_2_FIFO}" \
    "${FASTQ_GZIP_2_FIFO}" \
  )
fi

# Create FIFOs
mkfifo "${FIFOS_ARRAY[@]}"

# Samtools view options
SAMTOOLS_VIEW_ARRAY=( \
  # Uncompressed
  "-u" \
  # Set the read group
  "--read-group" "${READ_GROUP_ID}" \
  # Input presigned url
  "${presigned_url}"
)

# Samtools sort options
SAMTOOLS_SORT_OPTIONS_ARRAY=( \
  # Uncompressed
  "-u" \
  # Sort by name
  "-n" \
  # To stdout
  "-o" "-" \
  # Set threads
  "--threads" "${THREADS}" \
  # Set stdin as the input
  "-" \
)

# Set samtools fastq options
# Where -2 is only set if paired end data is set to true
SAMTOOLS_FASTQ_OPTIONS_ARRAY=( \
  # Fastq outputs to fifo
  "-1" "${FASTQ_PRE_FIFO}" \
)
if [[ "${IS_PAIRED_END}" == "true" ]]; then
  SAMTOOLS_FASTQ_OPTIONS_ARRAY+=(
    "-2" "${FASTQ_PRE_2_FIFO}" \
  )
fi
SAMTOOLS_FASTQ_OPTIONS_ARRAY+=( \
  # Singleton reads cannot be rescued
  "-s" "/dev/null" \
  # Set threads
  "--threads" "${THREADS}" \
  # From stdin
  "-" \
)

PIGZ_OPTIONS_ARRAY=( \
  # Write to stdout
  "--stdout" \
  # Use half the processes since pigz will
  # be running for both fq1 and fq2 simultaneously
  "--processes" "$( \
    jq --null-input --raw-output \
      --argjson threads "${THREADS}" \
      '$threads/2' \
  )"
)
AWS_S3_CP_OPTIONS_ARRAY=( \
  # Set the expected file size
  # Required for large files being written from stdout
  "--expected-size" "${est_file_size}" \
  # Write from stdout
  "-" \
)

# While also compressing and uploading
(
  # Run samtools view to select only those files in the readgroup
  samtools view \
    "${SAMTOOLS_VIEW_ARRAY[@]}" \
  | \
  # Run samtools sort to samtools fastq
  samtools sort \
    "${SAMTOOLS_SORT_OPTIONS_ARRAY[@]}" \
  | \
  samtools fastq \
    "${SAMTOOLS_FASTQ_OPTIONS_ARRAY[@]}" \
) & \
(
  # Split samtools fastq output into two pipes
  # one for data, one for validation
  tee -p "${FASTQ_FIFO}" "${FASTQ_LINE_COUNT_FIFO}" 1>/dev/null < "${FASTQ_PRE_FIFO}"
) & \
(
  # Count lines for fastq
  wc -l < "${FASTQ_LINE_COUNT_FIFO}" > "fastq.lc.txt"
) & \
(
  # Compress fastq
  pigz "${PIGZ_OPTIONS_ARRAY[@]}" < "${FASTQ_FIFO}" > "${FASTQ_GZIP_PRE_FIFO}"
) & \
(
  # Split pigz output into two paths
  # one for upload, one for size calculation
  tee -p "${FASTQ_GZIP_FIFO}" "${FASTQ_GZIP_WC_FIFO}" 1>/dev/null < "${FASTQ_GZIP_PRE_FIFO}"
) & \
(
  # Count characters for compressed files
  wc -c < "${FASTQ_GZIP_WC_FIFO}" > "fastq.gzip.wc.txt"
) & \
(
  # Upload compressed fastq data to s3
  # shellcheck disable=SC1090
  source "${ICAV2_ACCESS_CREDS_FILE}";
  aws s3 cp \
    "${AWS_S3_CP_OPTIONS_ARRAY[@]}" \
    "${FASTQ_OUTPUT_URI}" < "${FASTQ_GZIP_FIFO}" \
) & \
(
  if [[ "${IS_PAIRED_END}" == "true" ]]; then \
    (
  		# Split samtools fastq output into two pipes
  		# one for data, one for validation
  		tee -p "${FASTQ_2_FIFO}" "${FASTQ_LINE_COUNT_2_FIFO}" 1>/dev/null < "${FASTQ_PRE_2_FIFO}"
    ) & \
    (
  		# Count lines for fastq2
  		wc -l < "${FASTQ_LINE_COUNT_2_FIFO}" > "fastq2.lc.txt"
    ) & \
    (
  		# Compress fastq 2
  		pigz "${PIGZ_OPTIONS_ARRAY[@]}" < "${FASTQ_2_FIFO}" > "${FASTQ_GZIP_PRE_2_FIFO}"
    ) & \
    (
  		# Split samtools fastq output into two pipes
  		# one for upload, one for size calculation
  		tee -p "${FASTQ_GZIP_2_FIFO}" "${FASTQ_GZIP_WC_2_FIFO}" 1>/dev/null < "${FASTQ_GZIP_PRE_2_FIFO}"
    ) & \
    (
  		# Count characters for compressed files
  		wc -c < "${FASTQ_GZIP_WC_2_FIFO}" > "fastq2.gzip.wc.txt"
    ) & \
    (
  		# Upload compressed fastq 2 data to s3
  		# shellcheck disable=SC1090
  		source "${ICAV2_ACCESS_CREDS_FILE}";
  		aws s3 cp \
  		  "${AWS_S3_CP_OPTIONS_ARRAY[@]}" \
  		  "${FASTQ_OUTPUT_2_URI}" < "${FASTQ_GZIP_2_FIFO}" \
    ) & \
    wait
  fi \
) & \
wait

# Delete fifos
rm "${FIFOS_ARRAY[@]}"

# Check line counts
if [[ "${IS_PAIRED_END}" == "true" ]]; then
  if [[ ! "$(cat < "fastq.lc.txt")" == "$(cat < "fastq2.lc.txt")" ]]; then
    echo_stderr "Line counts for fastq and fastq2 do not match, something went wrong with the conversion"
    exit 1
  fi
fi

# Check file sizes
if [[ ! "$(cat < "fastq.gzip.wc.txt")" == "$(get_content_length "${FASTQ_OUTPUT_URI}")" ]]; then
  echo_stderr "File uploaded does not match expected"
  exit 1
fi

if [[ "${IS_PAIRED_END}" == "true" ]]; then
  # Check file sizes
  if [[ ! "$(cat < "fastq2.gzip.wc.txt")" == "$(get_content_length "${FASTQ_OUTPUT_2_URI}")" ]]; then
    echo_stderr "File2 uploaded does not match expected"
    exit 1
  fi
fi

# Delete access creds
rm "${ICAV2_ACCESS_CREDS_FILE}"