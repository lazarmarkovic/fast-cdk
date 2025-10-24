//External imports
import * as cdk from "aws-cdk-lib";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as alb from "aws-cdk-lib/aws-elasticloadbalancingv2";
import * as cert from "aws-cdk-lib/aws-certificatemanager";

// Config imports
import { EnvConfig } from "@fastcdk-root/config/configSchema";

// Root imports
import { Network } from "@fastcdk-lib/network.root";

// fastcdk:keep-start id=AppLoadBalancer.OtherImports sig=v0.0.1
// fastcdk:keep-end


export class AppLoadBalancer {
  public readonly alb: alb.ApplicationLoadBalancer;
  public readonly albSg: ec2.SecurityGroup;
  public readonly albTg: alb.ApplicationTargetGroup;
  public readonly albListener: alb.ApplicationListener;
  public readonly albListenerHttps: alb.ApplicationListener;
  public readonly albCertificate: cert.ICertificate;

  constructor(
    mainStack: cdk.Stack,
    envConfig: EnvConfig,
    
    alb_net: Network,

    // fastcdk:keep-start id=AppLoadBalancer.OtherConstructorVars sig=v0.0.1
    // fastcdk:keep-end
  ) {

    this.albCertificate = cert.Certificate.fromCertificateArn(
      mainStack,
      "$RootAlbCertificate",
      envConfig.BuildParams.SimpleECSBackend.AlbCertificateARN
    );

    this.albSg = new ec2.SecurityGroup(mainStack, "RootAlbSg", {
      vpc: alb_net.vpc,
      allowAllOutbound: true,
      securityGroupName: "root.alb.sg",
    });
    this.albSg.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(443));
    this.albSg.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(80));
    // fastcdk:keep-start id=AppLoadBalancer.ALBSgCustomPorts sig=v0.0.1
    // fastcdk:keep-end

    this.alb = new alb.ApplicationLoadBalancer(mainStack, "RootAlb", {
      loadBalancerName: "root-alb",
      internetFacing: true,
      vpc: alb_net.vpc,vpcSubnets: alb_net.vpc.selectSubnets({ subnetType: ec2.SubnetType.PUBLIC }),securityGroup: this.albSg,
      idleTimeout: cdk.Duration.seconds(4000),
      // fastcdk:keep-start id=AppLoadBalancer.ALBProps sig=v0.0.1
      // fastcdk:keep-end
    });

    this.albTg = new alb.ApplicationTargetGroup(mainStack, "RootAlbTg", {stickinessCookieDuration: cdk.Duration.days(7),
      stickinessCookieName: "StickySocketSession",targetGroupName: "root-alb-tg",
      vpc: alb_net.vpc,
      port: envConfig.envConfig.BuildParams.SimpleECSBackend.HostPort,
      protocol: alb.ApplicationProtocol.HTTP,
      targetType: alb.TargetType.IP,

      // fastcdk:keep-start id=AppLoadBalancer.ALBTGProps sig=v0.0.1
      // fastcdk:keep-end

      healthCheck: {
        interval: cdk.Duration.seconds(5),
        timeout: cdk.Duration.seconds(3),
        path: envConfig.BuildParams.SimpleECSBackend.AlbHealthCheckApiPath,
        port: envConfig.envConfig.BuildParams.SimpleECSBackend.HostPort.toString(),
        protocol: alb.Protocol.HTTP,
        healthyThresholdCount: 2,
        unhealthyThresholdCount: 2,
        healthyHttpCodes: "200"
      // fastcdk:keep-start id=AppLoadBalancer.ALBTGHealthCheckProps sig=v0.0.1
      // fastcdk:keep-end
      },
      deregistrationDelay: cdk.Duration.seconds(1) // Important for change and scaling and stuff (should be 300)
    });


    this.albListenerHttps = new alb.ApplicationListener(mainStack, "RootAlbListenerHttps", {
      loadBalancer: this.alb,
      certificates: [this.albCertificate],
      sslPolicy: alb.SslPolicy.TLS12,
      port: 443,
      protocol: alb.ApplicationProtocol.HTTPS,
      // fastcdk:keep-start id=AppLoadBalancer.ALBListenerHttpsProps sig=v0.0.1
      // fastcdk:keep-end
    });
    this.albListenerHttps.addAction("DefaultAction", {
      action: alb.ListenerAction.forward([this.albTg]),
    });
    // fastcdk:keep-start id=AppLoadBalancer.ALBListenerHttpsCustomActions sig=v0.0.1
    // fastcdk:keep-end


    // fastcdk:keep-start id=AppLoadBalancer.CustomConstructs sig=v0.0.1
    // fastcdk:keep-end


    // Tag resources
    cdk.Tags.of(this.albSg).add("Name", "root.alb.sg");
    cdk.Tags.of(this.alb).add("Name", "$root.alb");
    cdk.Tags.of(this.albTg).add("Name", "$root.alb.target-group");
    cdk.Tags.of(this.albListenerHttps).add("Name", "root.alb.https-listener");

    // fastcdk:keep-start id=AppLoadBalancer.ExtraTags sig=v0.0.1
    // fastcdk:keep-end
  }
}