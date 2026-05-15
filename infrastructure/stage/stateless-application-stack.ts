import * as cdk from 'aws-cdk-lib';
import * as events from 'aws-cdk-lib/aws-events';
import * as secretsManager from 'aws-cdk-lib/aws-secretsmanager';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import { Construct } from 'constructs';
import { StatelessApplicationStackConfig } from './interfaces';
import { buildAllLambdas } from './lambda';
import { buildAllStepFunctions } from './step-functions';
import { buildAllEventRules } from './event-rules';
import { buildAllEventBridgeTargets } from './event-targets';
import { StageName } from '@orcabus/platform-cdk-constructs/shared-config/accounts';
import { buildAllEcsFargateTasks } from './ecs';

export type StatelessApplicationStackProps = cdk.StackProps & StatelessApplicationStackConfig;

export class StatelessApplicationStack extends cdk.Stack {
  public readonly stageName: StageName;

  constructor(scope: Construct, id: string, props: StatelessApplicationStackProps) {
    super(scope, id, props);

    /**
     * Oncoanalyser WGTS rna Stack
     * Deploys the Oncoanalyser WGTS RNA orchestration services
     */

    // Set the stage name
    this.stageName = props.stageName;

    // Get the event bus as a construct
    const orcabusMainEventBus = events.EventBus.fromEventBusName(
      this,
      props.eventBusName,
      props.eventBusName
    );

    // Get the icav2 secret
    const icav2AccessTokenSecretObj = secretsManager.Secret.fromSecretNameV2(
      this,
      props.icav2AccessTokenSecretId,
      props.icav2AccessTokenSecretId
    );

    const orcabusTokenSecretObj = secretsManager.Secret.fromSecretNameV2(
      this,
      props.orcabusTokenSecretId,
      props.orcabusTokenSecretId
    );

    const hostnameSsmParameter = ssm.StringParameter.fromStringParameterName(
      this,
      props.hostnameSsmParameterName,
      props.hostnameSsmParameterName
    );

    // Build the lambdas
    const lambdas = buildAllLambdas(this, {
      testDataBucketName: props.testDataBucketName,
      refDataBucketName: props.refDataBucketName,
    });

    // Part 2 - Build ECS Tasks / Fargate Clusters
    const ecsFargateTasks = buildAllEcsFargateTasks(this, {
      icav2AccessTokenSecretObj: icav2AccessTokenSecretObj,
      orcabusTokenSecretObj: orcabusTokenSecretObj,
      hostnameSsmParameter: hostnameSsmParameter,
    });

    // Build the state machines
    const stateMachines = buildAllStepFunctions(this, {
      lambdaObjects: lambdas,
      eventBus: orcabusMainEventBus,
      /* Ecs stuff */
      ecsFargateTaskObjects: ecsFargateTasks,
      ssmParameterPaths: props.ssmParameterPaths,
    });

    // Add event rules
    const eventRules = buildAllEventRules(this, {
      eventBus: orcabusMainEventBus,
    });

    // Add event targets
    buildAllEventBridgeTargets({
      eventBridgeRuleObjects: eventRules,
      stepFunctionObjects: stateMachines,
    });
  }
}
