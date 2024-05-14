import os
from aws_cdk import (
    # Duration,
    CfnCondition,
    aws_s3 as s3,
    CfnOutput,
    Fn,
    Stack,
    Tags,
    aws_ec2 as ec2,
)

from constructs import Construct

class CromwellInfraCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC
        vpc = ec2.Vpc(self, "VPC",
            max_azs=1,
            nat_gateways=1
        )

        # Add S3 VPC endpoint
        vpc.add_gateway_endpoint("S3Endpoint",
            service=ec2.GatewayVpcEndpointAwsService.S3
        )

        # Create a DHCP options set
        dhcp_options = ec2.CfnDHCPOptions(self, "DHCPOptions",
            domain_name=f"{os.getenv('CDK_DEFAULT_REGION')}.compute.internal",
            domain_name_servers=["AmazonProvidedDNS"]
        )

        # Associate the DHCP options set with the VPC
        ec2.CfnVPCDHCPOptionsAssociation(self, "DHCPOptionsAssociation",
            vpc_id=vpc.vpc_id,
            dhcp_options_id=dhcp_options.ref
        )

        # Define conditions
        bucket_does_not_exist = CfnCondition(
            self, "BucketDoesNotExist",
            expression=Fn.condition_equals("", self.node.try_get_context("S3BucketName"))
        )

        # Define resources
        s3_bucket = s3.CfnBucket(
            self, "S3Bucket",
            bucket_name=self.node.try_get_context("S3BucketName"),
            tags=[{"key": "architecture", "value": "default"}]
        )

        # Define outputs
        CfnOutput(
            self, "BucketName",
            value=Fn.condition_if(
                bucket_does_not_exist.logical_id,
                s3_bucket.ref,
                self.node.try_get_context("S3BucketName")
            ).to_string()
        )

        CfnOutput(
            self, "BucketArn",
            value=Fn.condition_if(
                bucket_does_not_exist.logical_id,
                s3_bucket.attr_arn,
                Fn.sub("arn:aws:s3:::${S3BucketName}", {"S3BucketName": self.node.try_get_context("S3BucketName")})
            ).to_string()
        )

        Tags.of(self).add("Name", "GenomicsWorkflowStack")
        Tags.of(self).add("Environment", "Production")
