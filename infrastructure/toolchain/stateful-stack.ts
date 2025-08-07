import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { DeploymentStackPipeline } from '@orcabus/platform-cdk-constructs/deployment-stack-pipeline';
import { REPO_NAME } from './constants';
import { getStatefulStackProps } from '../stage/config';
import { StatefulApplicationStack } from '../stage/stateful-application-stack';

export class StatefulStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new DeploymentStackPipeline(this, 'StatefulOncoanalyserWgtsRnaPipeline', {
      githubBranch: 'main',
      githubRepo: REPO_NAME,
      stack: StatefulApplicationStack,
      stackName: 'StatefulOncoanalyserWgtsRnaPipeline',
      stackConfig: {
        beta: getStatefulStackProps('BETA'),
        gamma: getStatefulStackProps('GAMMA'),
        prod: getStatefulStackProps('PROD'),
      },
      pipelineName: 'OrcaBus-StatefulOncoanalyserWgtsRnaPipeline',
      cdkSynthCmd: ['pnpm install --frozen-lockfile --ignore-scripts', 'pnpm cdk-stateful synth'],
      enableSlackNotification: false,
    });
  }
}
