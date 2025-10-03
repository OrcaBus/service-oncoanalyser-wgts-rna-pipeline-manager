import { PythonUvFunction } from '@orcabus/platform-cdk-constructs/lambda';

export type LambdaName =
  // Populate Draft lambdas
  | 'getLibraries'
  | 'getMetadataTags'
  | 'getFastqRgidsFromLibraryId'
  | 'getFastqIdListFromRgidList'
  | 'getFastqListRowsFromRgidList'
  | 'getQcSummaryStatsFromRgidList'
  | 'checkNtsmInternal'
  // Validate draft lambdas
  | 'validateDraftCompleteSchema'
  // Ready to ICAv2 WES lambdas
  | 'convertFastqListRowsObjectToCacheUri'
  | 'getFastqIdListFromFastqRgidList'
  | 'convertReadyEventInputsToIcav2WesEventInputs'
  // ICAv2 WES to WRSC Event lambdas
  | 'convertIcav2WesEventToWrscEvent';

export const lambdaNameList: LambdaName[] = [
  // Populate Draft lambdas
  'getLibraries',
  'getMetadataTags',
  'getFastqRgidsFromLibraryId',
  'getFastqIdListFromRgidList',
  'getFastqListRowsFromRgidList',
  'getQcSummaryStatsFromRgidList',
  'checkNtsmInternal',
  // Validate draft lambdas
  'validateDraftCompleteSchema',
  // Ready to ICAv2 WES lambdas
  'convertFastqListRowsObjectToCacheUri',
  'getFastqIdListFromFastqRgidList',
  'convertReadyEventInputsToIcav2WesEventInputs',
  // ICAv2 WES to WRSC Event lambdas
  'convertIcav2WesEventToWrscEvent',
];

// Requirements interface for Lambda functions
export interface LambdaRequirements {
  needsOrcabusApiTools?: boolean;
  needsSsmParametersAccess?: boolean;
  needsSchemaRegistryAccess?: boolean;
}

// Lambda requirements mapping
export const lambdaRequirementsMap: Record<LambdaName, LambdaRequirements> = {
  // Populate Draft data
  getLibraries: {
    needsOrcabusApiTools: true,
  },
  getMetadataTags: {
    needsOrcabusApiTools: true,
  },
  getFastqRgidsFromLibraryId: {
    needsOrcabusApiTools: true,
  },
  getFastqIdListFromRgidList: {
    needsOrcabusApiTools: true,
  },
  getFastqListRowsFromRgidList: {
    needsOrcabusApiTools: true,
  },
  getQcSummaryStatsFromRgidList: {
    needsOrcabusApiTools: true,
  },
  checkNtsmInternal: {
    needsOrcabusApiTools: true,
  },
  // Validate Draft data
  validateDraftCompleteSchema: {
    needsSsmParametersAccess: true,
    needsSchemaRegistryAccess: true,
  },
  // Convert ready to ICAv2 WES Event - no requirements
  convertFastqListRowsObjectToCacheUri: {
    needsOrcabusApiTools: true,
  },
  getFastqIdListFromFastqRgidList: {
    needsOrcabusApiTools: true,
  },
  convertReadyEventInputsToIcav2WesEventInputs: {},
  // Needs OrcaBus toolkit to get the wrsc event
  convertIcav2WesEventToWrscEvent: {
    needsOrcabusApiTools: true,
  },
};

export interface LambdaInput {
  lambdaName: LambdaName;
}

export interface LambdaObject extends LambdaInput {
  lambdaFunction: PythonUvFunction;
}
