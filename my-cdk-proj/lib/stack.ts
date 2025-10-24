

// External imports
import * as cdk from "aws-cdk-lib";

// Config imports
import { EnvConfig } from "@fastcdk-root/config/configSchema";

// Construct imports
import { GitOidc } from "@fastcdk-lib/git-oidc.root";
import { HostedZone } from "@fastcdk-lib/hosted-zone.root";
import { Network } from "@fastcdk-lib/network.root";
import { S3cfFrontend } from "@fastcdk-lib/s3based-cloudfront-frontend/main.s3cf";



// fastcdk:keep-start id=StackRoot.OtherImports sig=v0.0.1>
// fastcdk:keep-end


export class StackRoot extends cdk.Stack {
  // Holder of all root constructs
  //
  public readonly gitOidc: GitOidc;
  public readonly hostedZone: HostedZone;
  public readonly network: Network;
  public readonly s3cfFrontend: S3cfFrontend;
  

  // fastcdk:keep-start id=StackRoot.OtherConstructsInit sig=v0.0.1>
  // fastcdk:keep-end

  constructor(
    scope: cdk.App,
    id: string,
    envConfig: EnvConfig,
  ) {
    super(
      scope,
      id,
      {
        env: {
          account: envConfig.AwsAccountId,
          region: envConfig.AwsRegion,
        }
      }
    );

    // Construct inits
    this.gitOidc = new GitOidc(this, envConfig);
    this.hostedZone = new HostedZone(this, envConfig);
    this.network = new Network(
      this, 
      envConfig,
      
      // fastcdk:keep-start id=Network.OtherExternalConstructorVars sig=v0.0.1
      // fastcdk:keep-end
    );
    this.s3cfFrontend = new S3cfFrontend(
      this, 
      envConfig,
    
      this.hostedZone,
      this.gitOidc,
    
      // fastcdk:keep-start id=S3cfFrontend.OtherExternalConstructorVars sig=v0.0.1>
      // fastcdk:keep-end
    );
    


    // fastcdk:keep-start id=StackRoot.OtherConstructs sig=v0.0.1>
    // fastcdk:keep-end
  }
}