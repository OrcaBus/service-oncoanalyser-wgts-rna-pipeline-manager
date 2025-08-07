"""
FROM

{
  "groupId": "SBJ12345",
  "subjectId": "SBJ12345",
  "sampleId": "L2500971",
  "fastqListRows": [
    {
      "lane": 1,
      "rgcn": "UMCCR",
      "rgds": "Library ID: L2500971 / Sequenced on 4 Aug 2025 at UMCCR / Phenotype: tumor / Assay: ISTRL / Type: WTS",
      "rgdt": "2025-08-04",
      "rgid": "CCATCTCGCC+AACCATAGAA.1.250804_A01052_0270_AHFGLKDSXF",
      "rglb": "L2500971",
      "rgpl": "Illumina",
      "rgsm": "L2500971",
      "read1FileUri": "s3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/production/primary/250804_A01052_0270_AHFGLKDSXF/202508054990a85a/Samples/Lane_1/L2500971/L2500971_S8_L001_R1_001.fastq.ora",
      "read2FileUri": "s3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/production/primary/250804_A01052_0270_AHFGLKDSXF/202508054990a85a/Samples/Lane_1/L2500971/L2500971_S8_L001_R2_001.fastq.ora"
    }
  ]
}

TO

{
  "mode": "wgts",
  "subject_id": "SBJ12345",
  "tumor_rna_sample_id": "L2500971",
  "samplesheet": [
    {
      "group_id": $inputs.groupId,
      "subject_id": $inputs.subjectId,
      "sample_id": $inputs.sampleId,
      "sample_type": "tumor",
      "sequence_type": "rna",
      "filetype": "fastq",
      "info": "library_id:\(.rglb);lane:\(.lane)",
      "filepath": "\(.read1FileUri);\(.read2FileUri)"
    }
  ]
}

"""
from typing import Dict

# Globals
DEFAULT_MODE = "wgts"
DEFAULT_MONOCHROME_LOGS = True
DEFAULT_GENOME = "GRCh38_hmf"
DEFAULT_GENOME_VERSION = "38"
DEFAULT_GENOME_TYPE = "no_alt"

# Default columns for the samplesheet
DEFAULT_SAMPLESHEET_COLUMNS = [
    "group_id",
    "subject_id",
    "sample_id",
    "sample_type",
    "sequence_type",
    "filetype",
    "info",
    "filepath",
]


def map_fastq_list_row_to_samplesheet_row(
        group_id: str,
        subject_id: str,
        fastq_list_row: Dict[str, str]
) -> Dict[str, str]:
    return {
      "group_id": group_id,
      "subject_id": subject_id,
      "sample_id": fastq_list_row['rglb'],
      "sample_type": "tumor",
      "sequence_type": "rna",
      "filetype": "fastq",
      "info": f"library_id:{fastq_list_row['rglb']};lane:{fastq_list_row['lane']}",
      "filepath": f"{fastq_list_row['read1FileUri']};{fastq_list_row['read2FileUri']}"
    }


def genome_keys_to_snake_case(genome: Dict[str, str]) -> Dict[str, str]:
    """
    Input genome keys are in camelCase, this function converts them to snake_case.
    :param genome:
    :return:
    """
    return dict(map(
        lambda kv_iter_: (kv_iter_[0].replace("Index", "_index").lower(), kv_iter_[1]),
        genome.items()
    ))


def convert_ready_event_inputs_to_icav2_wes_event_inputs(
        inputs: Dict[str, any]
) -> Dict[str, any]:
    """
    Convert the ready event inputs to ICAv2 WES event inputs.
    """
    samplesheet = list(map(
        lambda row: map_fastq_list_row_to_samplesheet_row(
            inputs['groupId'],
            inputs['subjectId'],
            row
        ),
        inputs['fastqListRows']
    ))

    return dict(filter(
        lambda kv_iter_: kv_iter_[1] is not None,
        {
            "mode": DEFAULT_MODE,
            "monochrome_logs": inputs.get("monochromeLogs", DEFAULT_MONOCHROME_LOGS),
            "samplesheet": samplesheet,
            "genome": inputs.get("genome", DEFAULT_GENOME),
            "genome_version": inputs.get("genomeVersion", DEFAULT_GENOME_VERSION),
            "genome_type": inputs.get("genomeType", DEFAULT_GENOME_TYPE),
            "force_genome": inputs.get("forceGenome", None),
            "ref_data_hmf_data_path": inputs["refDataHmfDataPath"],
            "genomes": (
                dict(map(
                    lambda kv_iter_: (kv_iter_[0], genome_keys_to_snake_case(kv_iter_[1])),
                    inputs.get("genomes").items()
                ))
                if inputs.get("genomes") is not None
                else None
            ),
        }.items()
    ))


def handler(event, context):
    """
    Convert the ready event inputs to ICAv2 WES event inputs.
    :param event:
    :param context:
    :return:
    """

    return {
        "inputs": convert_ready_event_inputs_to_icav2_wes_event_inputs(
            event
        )
    }


if __name__ == "__main__":
    import json

    print(json.dumps(
        handler(
            {
                "groupId": "SBJ12345",
                "subjectId": "SBJ12345",
                "sampleId": "L2500971",
                "fastqListRows": [
                    {
                        "lane": 1,
                        "rgcn": "UMCCR",
                        "rgds": "Library ID: L2500971 / Sequenced on 4 Aug 2025 at UMCCR / Phenotype: tumor / Assay: ISTRL / Type: WTS",
                        "rgdt": "2025-08-04",
                        "rgid": "CCATCTCGCC+AACCATAGAA.1.250804_A01052_0270_AHFGLKDSXF",
                        "rglb": "L2500971",
                        "rgpl": "Illumina",
                        "rgsm": "L2500971",
                        "read1FileUri": "s3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/production/primary/250804_A01052_0270_AHFGLKDSXF/202508054990a85a/Samples/Lane_1/L2500971/L2500971_S8_L001_R1_001.fastq.ora",
                        "read2FileUri": "s3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/production/primary/250804_A01052_0270_AHFGLKDSXF/202508054990a85a/Samples/Lane_1/L2500971/L2500971_S8_L001_R2_001.fastq.ora"
                    }
                ],
                "refDataHmfDataPath": "s3://pipeline-prod-cache-503977275616-ap-southeast-2/byob-icav2/production/ref-data/",
            },
            None
        ),
        indent=4
    ))
