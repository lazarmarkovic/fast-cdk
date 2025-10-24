
// External imports
import * as cdk from "aws-cdk-lib";
import * as secretsmanager from "aws-cdk-lib/aws-secretsmanager";

// Config import
import { EnvConfig } from "@fastcdk-root/config/configSchema";
import { CustomSecret } from "@fastcdk-root/misc/customSecret";


export class EcsSecret extends CustomSecret {
  constructor(mainStack: cdk.Stack, envConfig: EnvConfig) {
    super();

    this.secret = secretsmanager.Secret.fromSecretCompleteArn(
      mainStack,
       "RootSecret",
      envConfig.BuildParams.SimpleECSBackend.SecretARN
    );

    // Tag resources
    cdk.Tags.of(this.secret).add("Name", "root.secret");
  }
}