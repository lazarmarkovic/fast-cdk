

// External imports
import * as cdk from "aws-cdk-lib";
import * as iam from "aws-cdk-lib/aws-iam";
import * as codedeploy from "aws-cdk-lib/aws-codedeploy";

// Config imports
import { EnvConfig } from "@fastcdk-root/config/configSchema";

// Root imports
import { GitOidc } from "@fastcdk-lib/git-oidc.root";

// Local imports
import { S3cfS3Bucket } from "@fastcdk-lib/s3based-cloudfront-frontend/s3_bucket.s3cf";
import { S3RandomCF } from "@fastcdk-lib/s3based-cloudfront-frontend/cloudfront.s3cf";


// fastcdk:keep-start id=S3cfFrontend.OtherImports sig=v0.0.1>
// fastcdk:keep-end


export class S3cfOidcRoles {
  public readonly codeDeployApp: codedeploy.ServerApplication;
  public readonly deploymentGroup: codedeploy.ServerDeploymentGroup;
  public readonly gitPlatformActionsRole: iam.Role;

  // fastcdk:keep-start id=S3cfFrontend.OtherConstructsInit sig=v0.0.1>
  // fastcdk:keep-end

  constructor(
    mainStack: cdk.Stack,
    envConfig: EnvConfig,

    rootGitOidc: GitOidc,
    s3: S3cfS3Bucket,
    scfCloudFront: S3RandomCF,

    // fastcdk:keep-start id=S3cfFrontend.OtherConstructorVars sig=v0.0.1>
    // fastcdk:keep-end
  ) {
    this.gitPlatformActionsRole = new iam.Role(mainStack, "S3cfGitPlatformActionsDeployRole", {
      roleName: "s3cf-frontend.github-actions-deploy-role",
      assumedBy: new iam.FederatedPrincipal(
        rootGitOidc.oidcProvider.openIdConnectProviderArn,
        {
          "StringEquals": {
            "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
            "token.actions.githubusercontent.com:sub": `repo:${envConfig.BuildParams.Root.GitOwner}/${envConfig.BuildParams.S3BasedCF.GitRepoName}:ref:refs/heads/${envConfig.BuildParams.S3BasedCF.GitRepoPullBranchName}`,
          },
        },
        "sts:AssumeRoleWithWebIdentity"
      ),

      maxSessionDuration: cdk.Duration.hours(1),
    });


    this.gitPlatformActionsRole.addToPolicy(new iam.PolicyStatement({
      actions: [
        "cloudfront:CreateInvalidation",
      ],
      resources: [`arn:aws:cloudfront::${mainStack.account}:distribution/${scfCloudFront.cfDist.distributionId}`],
    }));
    this.gitPlatformActionsRole.addToPolicy(new iam.PolicyStatement({
      actions: [
        "s3:DeleteObject",
        "s3:GetObject",
        "s3:PutObject"
      ],
      resources: [`arn:aws:s3:::${s3.frontendBucket.bucketName}/*`],
    }));
    this.gitPlatformActionsRole.addToPolicy(new iam.PolicyStatement({
      actions: ["s3:ListBucket"],
      resources: [`arn:aws:s3:::${s3.frontendBucket.bucketName}`],
    }));

    // fastcdk:keep-start id=S3cfFrontend.ExtraPolicy sig=v0.0.1>
    // fastcdk:keep-end


    // Outputs - generated after deployment
    new cdk.CfnOutput(mainStack, "S3cfOutGitPlatformActionsRoleArn", {
      description: "FA ARN of the GitHub OIDC IAM Role",
      value: this.gitPlatformActionsRole.roleArn
    });

    new cdk.CfnOutput(mainStack, "S3cfOutS3BucketName", {
      description: "FA S3 Bucket Name",
      value: s3.frontendBucket.bucketName
    });

    new cdk.CfnOutput(mainStack, "S3cfOutCfDistributionId", {
      description: "FA CloudFront Distribution ID",
      value: scfCloudFront.cfDist.distributionId
    });

    // fastcdk:keep-start id=S3cfFrontend.ExtraOutput sig=v0.0.1>
    // fastcdk:keep-end
  }
}