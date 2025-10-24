
// External imports
import * as cdk from "aws-cdk-lib";
import * as r53 from "aws-cdk-lib/aws-route53";

// Config imports
import { EnvConfig } from "@fastcdk-root/config/configSchema";


export class HostedZone {
  public readonly appHostedZone: r53.IHostedZone;

  constructor(
    mainStack: cdk.Stack,
    envConfig: EnvConfig,
  ) {
    this.appHostedZone = r53.HostedZone.fromLookup(
      mainStack,
      "RootHostedZone",
      { domainName: envConfig.BuildParams.Root.BaseDomainName1 }
    );

    // Tag resources
    cdk.Tags.of(this.appHostedZone).add("Name", "root.hosting-zone");
  }
}