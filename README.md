# Cromwell on AWS


## Genomics Workflows on AWS CloudFormation templates

Contained herein are CloudFormation templates for creating AWS resources for working with large-scale biomedical data - e.g. genomics.

Create an S3 bucket in your AWS account to use for the distribution deployment

```bash
aws s3 mb <dist-bucketname>
```

Create and deploy a distribution from source

```bash
bash _scripts/deploy.sh --deploy-region <region> --asset-profile <profile-name> --asset-bucket s3://<dist-bucketname> test
```
This will create a `dist` folder in the root of the project with subfolders `dist/artifacts` and `dist/templates` that will be uploaded to the S3 bucket you created above.

Use `--asset-profile` option to specify an AWS profile to use to make the deployment.

**Note**: the region set for `--deploy-region` should match the region the bucket `<dist-bucketname>` is created in.

You can now use your deployed distribution to launch stacks using the AWS CLI. For example, to launch the GWFCore stack:

```bash
TEMPLATE_ROOT_URL=https://<dist-bucketname>.s3-<region>.amazonaws.com/test/templates

aws cloudformation create-stack \
    --region <region> \
    --stack-name <stackname> \
    --template-url $TEMPLATE_ROOT_URL/test/templates/cromwell/cromwell-and-core.template.yaml \
    --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
    --parameters \
        ParameterKey=VpcId,ParameterValue=<vpc-id> \
        ParameterKey=SubnetIds,ParameterValue=\"<subnet-id-1>,<subnet-id-2>,...\" \
        ParameterKey=ArtifactBucketName,ParameterValue=<dist-bucketname> \
        ParameterKey=TemplateRootUrl,ParameterValue=$TEMPLATE_ROOT_URL \
        ParameterKey=S3BucketName,ParameterValue=<store-buketname> \
        ParameterKey=ExistingBucket,ParameterValue=false

```

### Core Stack

Templates in `gwfcore` are the "core" stack.  The root template is:

| File | Description |
| :--- | :---------- |
| `gwfcore-root.template.yaml` | Root stack that invokes nested stacks (see below) |

Nested stacks are as follows and listed in order of creation:

| File | Description |
| :--- | :---------- |
| `gwfcore-s3.template.yaml` | Creates an S3 bucket for storing installed artifacts and workflow input and output data |
| `gwfcore-code.template.yaml` | Creates and installs code and artifacts used to run subsequent templates and provision EC2 instances |
| `gwfcore-launch-template.template.yaml` | Creates an EC2 Launch Template used in AWS Batch Compute Environments |
| `gwfcore-iam.template.yaml` | Creates IAM roles for AWS Batch resources |
| `gwfcore-batch.template.yaml` | Creates AWS Batch Job Queues and Compute Environments for job execution |


## Orchestration Stacks

The following Stack provide solutions that utilize:

* Cromwell

They build atop the Core Stack above. They provide the additional resources needed to run each orchestrator.

| File | Description |
| :--- | :---------- |
| `cromwell/cromwell-resources.template.yaml` | Creates an EC2 instance with Cromwell pre-installed and launched in "server" mode and an RDS Aurora Serverless database |


Note : As System Manager Parameter Store is being used, make sure to increase the throughput from console. To do that follow below :
AWS Systems Manager -> Parameter Store -> Settings -> Parameter Store throughput -> paid tier/higher throughput limit.




```shell
aws cloudformation create-stack \
  --stack-name my-stack \
  --template-body file://path/to/cromwell-and-core.template.yaml \
  --parameters \
    ParameterKey=Namespace,ParameterValue=my-namespace \
    ParameterKey=S3DataBucketName,ParameterValue=my-s3-data-bucket-name \
    ParameterKey=DBUsername,ParameterValue=my-db-username \
    ParameterKey=DBPassword,ParameterValue=my-db-password
```
