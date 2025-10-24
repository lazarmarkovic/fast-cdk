

// External imports
import * as cdk from "aws-cdk-lib";
import * as cert from "aws-cdk-lib/aws-certificatemanager";
import * as cf from "aws-cdk-lib/aws-cloudfront";
import * as origins from "aws-cdk-lib/aws-cloudfront-origins";
import * as r53 from "aws-cdk-lib/aws-route53";
import * as r53_targets from "aws-cdk-lib/aws-route53-targets"

// Config import
import { EnvConfig } from "@fastcdk-root/config/configSchema";
import { DeploymentEnvEnum } from "@fastcdk-root/misc/deploymentEnvEnum";

// Root imports
import { HostedZone } from "@fastcdk-lib/hosted-zone.root";

// Local imports
import { S3cfS3Bucket } from "@fastcdk-lib/s3based-cloudfront-frontend/s3_bucket.s3cf";


// fastcdk:keep-start id=S3cfFrontend.OtherImports sig=v0.0.1>
// fastcdk:keep-end

export class S3RandomCF {
  private readonly deploymentEnv: string;
  public readonly cfDist: cf.Distribution;
  public readonly dnsRecord: r53.RecordSet;
  public readonly dnsRecord2: r53.RecordSet;
  public readonly cloudFrontCertificate: cert.ICertificate;

  // fastcdk:keep-start id=S3cfFrontend.OtherConstructsInit sig=v0.0.1>
  // fastcdk:keep-end
  
  constructor(
    mainStack: cdk.Stack,
    envConfig: EnvConfig,
    hostedZone: HostedZone,
    s3: S3cfS3Bucket,

    // fastcdk:keep-start id=S3cfFrontend.OtherConstructorVars sig=v0.0.1>
    // fastcdk:keep-end
  ) {
    let mainDomainNames = [envConfig.BuildParams.Root.DomainName];
    if (envConfig.Environment === DeploymentEnvEnum.BLUE_PROD) {
      mainDomainNames = [
        envConfig.BuildParams.Root.DomainName, 
        `www.${envConfig.BuildParams.Root.DomainName}`,
          // fastcdk:keep-start id=S3cfFrontend.OtherDomains sig=v0.0.1>
          // fastcdk:keep-end
        ]
    }

    // Must be in us-east-1, always
    this.cloudFrontCertificate = cert.Certificate.fromCertificateArn(
      mainStack,
      "S3cfCloudfrontCertificate",
      envConfig.BuildParams.S3BasedCF.CloudFrontCertificateARN);

    this.cfDist = new cf.Distribution(mainStack, "S3cfCloudFrontDistribution", {
      domainNames: mainDomainNames,
      defaultBehavior: {
        origin: new origins.HttpOrigin(s3.frontendBucket.bucketWebsiteDomainName, {
          customHeaders: { "User-Agent": envConfig.BuildParams.S3BasedCF.CloudFrontConnectionSecret },
          originShieldRegion: mainStack.region,
          protocolPolicy: cf.OriginProtocolPolicy.HTTP_ONLY,
          
          // fastcdk:keep-start id=S3cfFrontend.OtherOriginProps sig=v0.0.1>
          // fastcdk:keep-end
        }),
        cachePolicy: cf.CachePolicy.CACHING_OPTIMIZED,
        allowedMethods: cf.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
        cachedMethods: cf.CachedMethods.CACHE_GET_HEAD,
        viewerProtocolPolicy: cf.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        compress: true

        // fastcdk:keep-start id=S3cfFrontend.OtherDefaultBehaviorProps sig=v0.0.1>
        // fastcdk:keep-end
      },
      defaultRootObject: "index.html",
      enabled: true,
      certificate: this.cloudFrontCertificate,
      minimumProtocolVersion: cf.SecurityPolicyProtocol.TLS_V1_2_2021,
      priceClass: cf.PriceClass.PRICE_CLASS_ALL

      // fastcdk:keep-start id=S3cfFrontend.OtherDistributionProps sig=v0.0.1>
      // fastcdk:keep-end
    });


    this.dnsRecord = new r53.ARecord(mainStack, "S3cfCloudfrontDNSRecord", {
      recordName: envConfig.BuildParams.Root.DomainName,
      zone: hostedZone.appHostedZone,
      target: r53.RecordTarget.fromAlias(new r53_targets.CloudFrontTarget(this.cfDist)),
      ttl: cdk.Duration.minutes(30),
      comment: "Frontend",

      // fastcdk:keep-start id=S3cfFrontend.OtherARecordProps sig=v0.0.1>
      // fastcdk:keep-end
    });


    // fastcdk:keep-start id=S3cfFrontend.OtherConstructs sig=v0.0.1>
    // fastcdk:keep-end


    // Tag resources
    cdk.Tags.of(this.cfDist).add("Name", "S3cf.cf-distribution");


    // fastcdk:keep-start id=S3cfFrontend.ExtraTags sig=v0.0.1>
    // fastcdk:keep-end
  }
}