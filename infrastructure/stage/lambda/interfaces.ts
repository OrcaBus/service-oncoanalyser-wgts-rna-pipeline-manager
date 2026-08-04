import { PythonUvFunction } from '@orcabus/platform-cdk-constructs/lambda';

export type LambdaName =
  // Shared pre-ready lambdas
  | 'comparePayload'
  | 'generateWruEventObjectWithMergedData'
  | 'getMissingSchemaFields'
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
  | 'postSchemaValidation'
  // Commentary lambdas
  | 'addPopulateDraftComment'
  // Ready to ICAv2 WES lambdas
  | 'collectReadCountStats'
  | 'convertFastqListRowsObjectToCacheUri'
  | 'getFastqIdListFromFastqRgidList'
  | 'convertReadyEventInputsToIcav2WesEventInputs'
  // ICAv2 WES to WRSC Event lambdas
  | 'convertIcav2WesEventToWrscEvent'
  | 'addWesFailureComment';

export const lambdaNameList: LambdaName[] = [
  // Shared pre-ready lambdas
  'comparePayload',
  'generateWruEventObjectWithMergedData',
  'getMissingSchemaFields',
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
  'postSchemaValidation',
  // Commentary lambdas
  'addPopulateDraftComment',
  // Ready to ICAv2 WES lambdas
  'collectReadCountStats',
  'convertFastqListRowsObjectToCacheUri',
  'getFastqIdListFromFastqRgidList',
  'convertReadyEventInputsToIcav2WesEventInputs',
  // ICAv2 WES to WRSC Event lambdas
  'convertIcav2WesEventToWrscEvent',
  'addWesFailureComment',
];

// Requirements interface for Lambda functions
export interface LambdaRequirements {
  needsOrcabusApiTools?: boolean;
  needsIcav2Tools?: boolean;
  needsHigherMemory?: boolean;
  needsSsmParametersAccess?: boolean;
  needsSchemaRegistryAccess?: boolean;
  needsExternalBucketInfo?: boolean;
  needsWorkflowInfo?: boolean;
  needsRepoUrl?: boolean;
}

// Lambda requirements mapping
export const lambdaRequirementsMap: Record<LambdaName, LambdaRequirements> = {
  // Shared pre-ready lambdas
  comparePayload: {},
  generateWruEventObjectWithMergedData: {
    needsOrcabusApiTools: true,
  },
  getMissingSchemaFields: {
    needsSchemaRegistryAccess: true,
    needsSsmParametersAccess: true,
  },
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
    needsExternalBucketInfo: true,
  },
  getQcSummaryStatsFromRgidList: {
    needsOrcabusApiTools: true,
  },
  checkNtsmInternal: {
    needsOrcabusApiTools: true,
  },
  // Validate Draft data
  validateDraftCompleteSchema: {
    needsOrcabusApiTools: true,
    needsSsmParametersAccess: true,
    needsSchemaRegistryAccess: true,
    needsWorkflowInfo: true,
  },
  postSchemaValidation: {
    needsOrcabusApiTools: true,
    needsIcav2Tools: true,
    needsExternalBucketInfo: true,
    needsWorkflowInfo: true,
  },
  // Commentary lambdas
  addPopulateDraftComment: {
    needsOrcabusApiTools: true,
    needsWorkflowInfo: true,
    needsRepoUrl: true,
  },
  // Convert ready to ICAv2 WES Event
  collectReadCountStats: {
    needsIcav2Tools: true,
  },
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
    needsWorkflowInfo: true,
  },
  addWesFailureComment: {
    needsOrcabusApiTools: true,
    needsWorkflowInfo: true,
  },
};

export interface LambdaInput {
  lambdaName: LambdaName;
}

export interface LambdaObject extends LambdaInput {
  lambdaFunction: PythonUvFunction;
}
