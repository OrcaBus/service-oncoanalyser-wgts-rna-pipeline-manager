/*
Interfaces
*/

import { IParameter } from 'aws-cdk-lib/aws-ssm';
import { ISecret } from 'aws-cdk-lib/aws-secretsmanager';
import { EcsFargateTaskConstruct } from '@orcabus/platform-cdk-constructs/ecs';

export type EcsTaskName = 'bamToFastq' | 'getFastqListRowsFromBam';

export const ecsTaskNameList: EcsTaskName[] = ['bamToFastq', 'getFastqListRowsFromBam'];

export interface BuildAllFargateEcsTasksProps {
  icav2AccessTokenSecretObj: ISecret;
  orcabusTokenSecretObj: ISecret;
  hostnameSsmParameter: IParameter;
}

export interface EcsRequirements {
  cpus: number;
  memoryGiB: number;
}

export interface BuildFargateEcsTaskProps extends BuildAllFargateEcsTasksProps {
  taskName: EcsTaskName;
}

export const ecsResourcesMap: Record<EcsTaskName, EcsRequirements> = {
  getFastqListRowsFromBam: {
    cpus: 2,
    memoryGiB: 4,
  },
  bamToFastq: {
    cpus: 8,
    memoryGiB: 16,
  },
};

export interface EcsTaskObject {
  taskName: EcsTaskName;
  ecsFargateTaskConstruct: EcsFargateTaskConstruct;
}
