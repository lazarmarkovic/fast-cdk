

import * as Joi from "joi";

export const configValidationSchema = Joi.object({
  AwsStackName: Joi.string().required(),
  AwsAccountId: Joi.string().required().length(12),
  AwsRegion: Joi.string().required(),

  Project: Joi.string().required(),
  Environment: Joi.string().required(),
  Version: Joi.string().required(),

  // fastcdk:keep-start id=OtherSchemaVars0 sig=v0.0.1>
  // fastcdk:keep-end

  BuildParams: Joi.object({
    // fastcdk:keep-start id=OtherSchemaVars1 sig=v0.0.1>
    // fastcdk:keep-end
    Root: Joi.object({
      // fastcdk:keep-start id=OtherSchemaVars2 sig=v0.0.1>
      // fastcdk:keep-end
      BaseDomainName1: Joi.string().required(),
      DomainName: Joi.string().required(),
      GitOwner: Joi.string().required(),
      OpenIdConnectProviderARN: Joi.string().required(),
      VpcCidr: Joi.string().required()
    }).required(),
    S3BasedCF: Joi.object({
      // fastcdk:keep-start id=OtherSchemaVars2 sig=v0.0.1>
      // fastcdk:keep-end
      CloudFrontCertificateARN: Joi.string().required(),
      CloudFrontConnectionSecret: Joi.string().required(),
      GitRepoName: Joi.string().required(),
      GitRepoPullBranchName: Joi.string().required(),
      S3BucketName: Joi.string().required()
    }).required()
  }).required()
}).required();





export interface EnvConfig { 
AwsStackName: string;
  AwsAccountId: string;
  AwsRegion: string;

  Project: string;
  Environment: string;
  Version: string;

  // fastcdk:keep-start id=OtherInterfaceVars0 sig=v0.0.1>
  // fastcdk:keep-end

  BuildParams: { 
    // fastcdk:keep-start id=OtherInterfaceVars1 sig=v0.0.1>
    // fastcdk:keep-end
    Root: { 
      // fastcdk:keep-start id=OtherInterfaceVars2 sig=v0.0.1>
      // fastcdk:keep-end
      BaseDomainName1: string;
      DomainName: string;
      GitOwner: string;
      OpenIdConnectProviderARN: string;
      VpcCidr: string;
    };
    S3BasedCF: { 
      // fastcdk:keep-start id=OtherInterfaceVars2 sig=v0.0.1>
      // fastcdk:keep-end
      CloudFrontCertificateARN: string;
      CloudFrontConnectionSecret: string;
      GitRepoName: string;
      GitRepoPullBranchName: string;
      S3BucketName: string;
    };
  };
}
