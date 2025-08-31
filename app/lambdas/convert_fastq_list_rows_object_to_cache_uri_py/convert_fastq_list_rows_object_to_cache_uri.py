#!/usr/bin/env python3

"""
Convert fastq list rows object to cache URI.

Given the inputs
* decompressedFileList
  - fastqId: "fqr.1234456",
    decompressedFileUriByOraFileIngestIdList:
    - ingestId": "INGEST_ID",
      gzipFileUri": "s3://bucket/path/to/output/prefix/<INSTRUMENT_RUN_ID>/Samples/Lane_<lane_number>/<Library_ID>/<Library_ID>_S1_L00<lane_number>_R1_001.fastq.gz"

Regenerate the fastq list rows for each object in the decompressedFileList,
remap the ingest ids from each object to the values in the decompressedFileList

"""

# Imports
from orcabus_api_tools.fastq import (
    get_fastq,
    get_fastq_by_rgid
)


def handler(event, context):
    """
    Convert fastq list rows object to cache URI.
    """
    decompressed_file_list = event.get("decompressedFileList", [])
    fastq_list_rows = event.get("fastqListRows", [])
    new_fastq_list_rows = []

    # Iterate through each decompressed file in the list
    for decompressed_file_iter_ in decompressed_file_list:
        # Get each attribute
        fastq_id = decompressed_file_iter_.get("fastqId")
        decompressed_file_uri_by_ingest_id_list = decompressed_file_iter_.get("decompressedFileUriByOraFileIngestIdList", [])

        # Get fastq object from the fastq id
        # We don't need the s3 details since we already have the ingest id
        fastq_obj = get_fastq(
            fastq_id
        )

        fastq_list_row = next(filter(
            lambda fastq_iter_: get_fastq_by_rgid(fastq_iter_["rgid"])['id'] == fastq_id,
            fastq_list_rows
        ))

        for decompressed_file_uri_by_ingest_id in decompressed_file_uri_by_ingest_id_list:
            ingest_id = decompressed_file_uri_by_ingest_id.get("ingestId")
            gzip_file_uri = decompressed_file_uri_by_ingest_id.get("gzipFileUri")
            # Either ingest id for r1 or r2
            if ingest_id == fastq_obj['readSet']['r1']['ingestId']:
                fastq_list_row["read1FileUri"] = gzip_file_uri
            elif ingest_id == fastq_obj['readSet']['r2']['ingestId']:
                fastq_list_row["read2FileUri"] = gzip_file_uri
            else:
                # Not sure how we got here
                raise ValueError(f"Unexpected ingestId {ingest_id} for fastqId {fastq_id}")

        new_fastq_list_rows.append(fastq_list_row)


    # Return the new fastq list rows
    return {"fastqListRows": new_fastq_list_rows}
