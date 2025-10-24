

// External imports
import * as cdk from 'aws-cdk-lib';
import { RemovalPolicy } from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';

// Config import
import { EnvConfig } from "@fastcdk-root/config/configSchema";


// fastcdk:keep-start id=S3cfFrontend.OtherImports sig=v0.0.1>
// fastcdk:keep-end


export class S3cfS3Bucket {
  public readonly frontendBucket: s3.Bucket;

  // fastcdk:keep-start id=S3cfFrontend.OtherConstructsInit sig=v0.0.1>
  // fastcdk:keep-end

  constructor(
    mainStack: cdk.Stack,
    envConfig: EnvConfig,

    // fastcdk:keep-start id=S3cfFrontend.OtherConstructorVars sig=v0.0.1>
    // fastcdk:keep-end
  ) {
    this.frontendBucket = new s3.Bucket(mainStack, "S3cfS3Bucket", {
      bucketName: envConfig.BuildParams.S3BasedCF.S3BucketName,
      removalPolicy: RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      publicReadAccess: true,
      blockPublicAccess: new s3.BlockPublicAccess({
        blockPublicPolicy: false,
        blockPublicAcls: false,
        ignorePublicAcls: false,
        restrictPublicBuckets: false
      }),
      websiteIndexDocument: "index.html",
      websiteErrorDocument: "index.html",

      // fastcdk:keep-start id=S3cfFrontend.ExtraS3BucketProps sig=v0.0.1>
      // fastcdk:keep-end
    });

    const policyStatement = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['s3:GetObject'],
      resources: [`${this.frontendBucket.bucketArn}/*`],
      principals: [new iam.AnyPrincipal()],
    });
    policyStatement.addCondition(
      "StringEquals",
      { "aws:UserAgent": envConfig.BuildParams.S3BasedCF.CloudFrontConnectionSecret }
    );
    this.frontendBucket.addToResourcePolicy(policyStatement);
    // fastcdk:keep-start id=S3cfFrontend.ExtraPolicy sig=v0.0.1>
    // fastcdk:keep-end


    // fastcdk:keep-start id=S3cfFrontend.OtherConstructs sig=v0.0.1>
    // fastcdk:keep-end


    // Tag resources
    cdk.Tags.of(this.frontendBucket).add("Name", "s3cf-frontend.s3-bucket");

    // fastcdk:keep-start id=S3cfFrontend.ExtraTags sig=v0.0.1>
    // fastcdk:keep-end
  }
}