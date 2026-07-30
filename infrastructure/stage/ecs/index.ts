/*
Build the ecs fargate task
*/

import { Construct } from 'constructs';
import {
  CPU_ARCHITECTURE_MAP,
  EcsFargateTaskConstruct,
} from '@orcabus/platform-cdk-constructs/ecs';
import * as path from 'path';
import { ECS_DIR } from '../constants';
import {
  BuildAllFargateEcsTasksProps,
  BuildFargateEcsTaskProps,
  ecsResourcesMap,
  ecsTaskNameList,
  EcsTaskObject,
} from './interfaces';
import { NagSuppressions } from 'cdk-nag';
import { ICAV2_BASE_URL } from '@orcabus/platform-cdk-constructs/shared-config/icav2';
import { camelCaseToSnakeCase } from '../utils';

function buildEcsFargateTask(scope: Construct, props: BuildFargateEcsTaskProps) {
  /*
    Build the Upload SinglePart File Fargate task.

    We use 8 CPUs for this task as we are running a few components simultaneously
  */

  /*
  Generate an ECS Fargate task construct with the provided properties.
  */

  const ecsTask = new EcsFargateTaskConstruct(scope, `${props.taskName}-ecs`, {
    containerName: props.taskName,
    dockerPath: path.join(ECS_DIR, camelCaseToSnakeCase(props.taskName)),
    nCpus: ecsResourcesMap[props.taskName].cpus,
    memoryLimitGiB: ecsResourcesMap[props.taskName].memoryGiB,
    architecture: 'ARM64',
    runtimePlatform: CPU_ARCHITECTURE_MAP['ARM64'],
  });

  // Needs access to the secrets manager
  props.icav2AccessTokenSecretObj.grantRead(ecsTask.taskDefinition.taskRole);
  ecsTask.containerDefinition.addEnvironment(
    'ICAV2_ACCESS_TOKEN_SECRET_ID',
    props.icav2AccessTokenSecretObj.secretName
  );
  ecsTask.containerDefinition.addEnvironment('ICAV2_BASE_URL', ICAV2_BASE_URL);

  // Needs access to ORCABUS_TOKEN_SECRET_ID and HOSTNAME_SSM_PARAMETER_NAME
  props.orcabusTokenSecretObj.grantRead(ecsTask.taskDefinition.taskRole);
  ecsTask.containerDefinition.addEnvironment(
    'ORCABUS_TOKEN_SECRET_ID',
    props.orcabusTokenSecretObj.secretName
  );
  props.hostnameSsmParameter.grantRead(ecsTask.taskDefinition.taskRole);
  ecsTask.containerDefinition.addEnvironment(
    'HOSTNAME_SSM_PARAMETER_NAME',
    props.hostnameSsmParameter.parameterName
  );

  // Add suppressions for the task role
  // Since the task role needs to access the S3 bucket prefix
  NagSuppressions.addResourceSuppressions(
    [ecsTask.taskDefinition, ecsTask.taskExecutionRole],
    [
      {
        id: 'AwsSolutions-IAM5',
        reason:
          'Wildcard covers Secrets Manager GetSecretValue sub-resources; secret ARNs include version IDs and staging labels that cannot be enumerated at deploy time',
      },
      {
        id: 'AwsSolutions-IAM4',
        reason:
          'Standard ECS task execution role managed policy provides ECR pull and CloudWatch Logs permissions required by all Fargate tasks',
      },
      {
        id: 'AwsSolutions-ECS2',
        reason:
          'Environment variables contain non-sensitive configuration values (secret names, SSM parameter names, base URLs) that are safe to pass as plaintext',
      },
    ],
    true
  );

  return {
    taskName: props.taskName,
    ecsFargateTaskConstruct: ecsTask,
  };
}

export function buildAllEcsFargateTasks(
  scope: Construct,
  props: BuildAllFargateEcsTasksProps
): EcsTaskObject[] {
  // Iterate over lambdaLayerToMapping and create the lambda functions
  const ecsTaskObjects: EcsTaskObject[] = [];
  for (const ecsTaskName of ecsTaskNameList) {
    ecsTaskObjects.push(
      buildEcsFargateTask(scope, {
        ...props,
        taskName: ecsTaskName,
      })
    );
  }

  return ecsTaskObjects;
}
