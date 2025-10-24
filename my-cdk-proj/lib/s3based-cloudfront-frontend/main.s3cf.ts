


// External imports
import * as cdk from "aws-cdk-lib";

// Config import
import { EnvConfig } from "@fastcdk-root/config/configSchema";
import { DeploymentEnvEnum } from "@fastcdk-root/misc/deploymentEnvEnum";

// Root imports
import { HostedZone } from "@fastcdk-lib/hosted-zone.root";
import { GitOidc } from "@fastcdk-lib/git-oidc.root";

// Local imports
import { S3cfS3Bucket } from "@fastcdk-lib/s3based-cloudfront-frontend/s3_bucket.s3cf";
import { S3RandomCF } from "@fastcdk-lib/s3based-cloudfront-frontend/cloudfront.s3cf";
import { S3cfOidcRoles } from "@fastcdk-lib/s3based-cloudfront-frontend/oidc_roles.s3cf";


// fastcdk:keep-start id=S3cfFrontend.OtherImports sig=v0.0.1>
// fastcdk:keep-end


export class S3cfFrontend {
  public readonly s3cfS3Bucket: S3cfS3Bucket;
  public readonly s3cfCloudfront: S3RandomCF;
  public readonly s3cfOidcRoles: S3cfOidcRoles;

  // fastcdk:keep-start id=S3cfFrontend.OtherConstructsInit sig=v0.0.1>
  // fastcdk:keep-end

  constructor(
    mainStack: cdk.Stack,
    envConfig: EnvConfig,
    hostedZone: HostedZone,
    gitOidc: GitOidc,

    // fastcdk:keep-start id=S3cfFrontend.OtherConstructorVars sig=v0.0.1>
    // fastcdk:keep-end
  ) {
    // App frontend S3 bucket
    this.s3cfS3Bucket = new S3cfS3Bucket(mainStack, envConfig);


    // CloudFront holder
    this.s3cfCloudfront = new S3RandomCF(
      mainStack,
      envConfig,
      hostedZone,
      this.s3cfS3Bucket,
    );

    // GitHub Actions OIDC role
    this.s3cfOidcRoles = new S3cfOidcRoles(
      mainStack,
      envConfig,
      gitOidc,
      this.s3cfS3Bucket,
      this.s3cfCloudfront,
    );


    // fastcdk:keep-start id=S3cfFrontend.OtherConstructs sig=v0.0.1>
    // fastcdk:keep-end
  }
}