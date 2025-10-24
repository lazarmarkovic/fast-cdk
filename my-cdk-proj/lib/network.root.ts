// External imports
import * as cdk from "aws-cdk-lib";
import * as ec2 from "aws-cdk-lib/aws-ec2";

// Config imports
import { EnvConfig } from "@fastcdk-root/config/configSchema";

// fastcdk:keep-start id=Network.OtherImports sig=v0.0.1
// fastcdk:keep-end

export class Network {
  public readonly vpc: ec2.Vpc;
  public readonly publicVpcSubnetsSelection: ec2.SubnetSelection;
  public readonly publicSubnets: ec2.ISubnet[];
  public readonly privateWithEgressVpcSubnetsSelection: ec2.SubnetSelection;
  public readonly privateWithEgressSubnets: ec2.ISubnet[];
  public readonly privateIsolatedVpcSubnetsSelection: ec2.SubnetSelection;
  public readonly privateIsolatedSubnets: ec2.ISubnet[];

  // fastcdk:keep-start id=Network.OtherConstructsInit sig=v0.0.1
  // fastcdk:keep-end

  constructor(
    mainStack: cdk.Stack, 
    envConfig: EnvConfig,
    // fastcdk:keep-start id=Network.OtherConstructorVars sig=v0.0.1
    // fastcdk:keep-end
    ) {
    this.vpc = new ec2.Vpc(mainStack, "RootVPC", {
      vpcName: "root.vpc",
      ipAddresses: ec2.IpAddresses.cidr(envConfig.BuildParams.Root.VpcCidr),
      maxAzs: 3,
      natGateways: 1,
      enableDnsSupport: true,
      enableDnsHostnames: true,

      // fastcdk:keep-start id=Network.VpcProps sig=v0.0.1
      // fastcdk:keep-end

      subnetConfiguration: [
        {
          name: "root.vpc.public.subnet",
          subnetType: ec2.SubnetType.PUBLIC,
        }, 
        {
          name: "root.vpc.private-with-nat.subnet",
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
        }, 
        {
          name: "root.vpc.private-isolated.subnet",
          subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
        }
      ],
    });

    // fastcdk:keep-start id=Network.OtherConstructs sig=v0.0.1
    // fastcdk:keep-end
    this.publicVpcSubnetsSelection = this.vpc.selectSubnets({ subnetType: ec2.SubnetType.PUBLIC });
    this.publicSubnets = this.publicVpcSubnetsSelection.subnets || [];
    
    this.privateWithEgressVpcSubnetsSelection = this.vpc.selectSubnets({ subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS });
    this.privateWithEgressSubnets = this.privateWithEgressVpcSubnetsSelection.subnets || [];
    
    this.privateIsolatedVpcSubnetsSelection = this.vpc.selectSubnets({ subnetType: ec2.SubnetType.PRIVATE_ISOLATED });
    this.privateIsolatedSubnets = this.privateIsolatedVpcSubnetsSelection.subnets || [];
    const endpointSubnets: ec2.SubnetSelection[] = [ this.publicVpcSubnetsSelection,  this.privateWithEgressVpcSubnetsSelection,  this.privateIsolatedVpcSubnetsSelection];
    this.vpc.addGatewayEndpoint("RootS3Endpoint", {
      service: ec2.GatewayVpcEndpointAwsService.S3,
      subnets: endpointSubnets,
    });

    // Resource tagging section
    cdk.Tags.of(this.vpc).add("Name", "root.vpc");
    for (const subnet of this.publicSubnets) {
      cdk.Tags.of(subnet).add("Name", "root.vpc.public.subnet-${subnet.availabilityZone.slice(-1)}");
    }
    for (const subnet of this.privateWithEgressSubnets) {
      cdk.Tags.of(subnet).add("Name", "root.vpc.private-with-nat.subnet-${subnet.availabilityZone.slice(-1)}");
    }
    for (const subnet of this.privateIsolatedSubnets) {
      cdk.Tags.of(subnet).add("Name", "root.vpc.private-isolated.subnet-${subnet.availabilityZone.slice(-1)}");
    }

    // fastcdk:keep-start id=Network.ExtraTags sig=v0.0.3
    // fastcdk:keep-end
  }
}