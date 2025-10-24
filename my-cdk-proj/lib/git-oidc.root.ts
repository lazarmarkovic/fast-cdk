
// External imports
import * as cdk from "aws-cdk-lib";
import * as iam from "aws-cdk-lib/aws-iam";

// Config imports
import { EnvConfig } from "@fastcdk-root/config/configSchema";


export class GitOidc {
  public readonly oidcProvider: iam.IOpenIdConnectProvider;

  constructor(
    mainStack: cdk.Stack,
    envConfig: EnvConfig,
  ) { 
    this.oidcProvider = iam.OpenIdConnectProvider.fromOpenIdConnectProviderArn(
      mainStack,
      "RootOpenIdConnectProvider",
      envConfig.BuildParams.Root.OpenIdConnectProviderARN
    );
  }
}