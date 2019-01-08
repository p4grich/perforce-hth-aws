from troposphere import Parameter, Output, Template
from troposphere import Base64, FindInMap, GetAtt, Ref, Join, If, Tags, Equals
from troposphere import cloudformation
from troposphere.cloudformation import WaitCondition, WaitConditionHandle
from troposphere.ec2 import Instance
from troposphere.ec2 import VPCGatewayAttachment, NetworkInterfaceProperty, SecurityGroup, SubnetRouteTableAssociation, RouteTable, Route, Subnet, InternetGateway, VPC, EIP
from troposphere.iam import AccessKey, User, Policy
from troposphere.route53 import RecordSetType
import awacs.aws

t = Template()

# Header
t.add_description("Perforce Helix Deployment for EC2")

# Header End

# Metadata
t.add_metadata({
    "Comments": "Perforce Helix Deployment for EC2",
    "LastUpdated": "Sep 14th 2016",
    "UpdatedBy": "Graeme Rich",
    "Version": "2016.1",
})

# Metadata End

# Conditions
ProdNotify = t.add_condition(
    "ProdNotify",
    Equals(Ref("EnvironmentType"), "Production")
),

EvalNotify = t.add_condition(
    "EvalNotify",
    Equals(Ref("EnvironmentType"), "Evaluationn")
),

DevNotify = t.add_condition(
    "DevNotify",
    Equals(Ref("EnvironmentType"), "Development")
),
# Exp josn
# "Conditions": {
#     "ProdNotify": {
#       "Fn::Equals": [
#         {
#           "Ref": "EnvironmentType"
#         },
#         "Production"
#       ]
#     },
#     "EvalNotify": {
#       "Fn::Equals": [
#         {
#           "Ref": "EnvironmentType"
#         },
#         "Evaluation"
#       ]
#     },
#     "DevNotify": {
#       "Fn::Equals": [
#         {
#           "Ref": "EnvironmentType"
#         },
#         "Development"
#       ]
#     }
#   },
# Conditions end

# Parameters
AvailabilityZone = t.add_parameter(Parameter(
    "AvailabilityZone",
    Type="AWS::EC2::AvailabilityZone::Name",
    Description="[Required]:: AWS EC2 Availability Zone",
))

SiteName = t.add_parameter(Parameter(
    "SiteName",
    AllowedPattern="^[_A-Za-z0-9][-A-Za-z0-9]*[A-Za-z0-9]$|^$",
    ConstraintDescription="Must be a valid HostName",
    Type="String",
    Description="[Production]:: *The DNS short name for an existing Amazon Route53 Domain | [Evaluation]: Leave empty. | [Development]: Leave empty. | [Example]: helix-cloud",
))

InstanceTypeP4D = t.add_parameter(Parameter(
    "InstanceTypeP4D",
    Default="t2.micro",
    ConstraintDescription="must be a valid EC2 instance type.",
    Type="String",
    Description="[Required]:: P4D Instance EC2 instance type",
    AllowedValues=["t1.micro", "t2.micro", "t2.small", "t2.medium", "m1.small", "m1.medium", "m1.large", "m1.xlarge", "m2.xlarge", "m2.2xlarge", "m2.4xlarge", "m3.medium", "m3.large", "m3.xlarge", "m3.2xlarge", "c1.medium", "c1.xlarge", "c3.large", "c3.xlarge", "c3.2xlarge", "c3.4xlarge", "c3.8xlarge", "c4.large", "c4.xlarge", "c4.2xlarge", "c4.4xlarge", "c4.8xlarge", "g2.2xlarge", "r3.large", "r3.xlarge", "r3.2xlarge", "r3.4xlarge", "r3.8xlarge", "i2.xlarge", "i2.2xlarge", "i2.4xlarge", "i2.8xlarge", "d2.xlarge", "d2.2xlarge", "d2.4xlarge", "d2.8xlarge", "hi1.4xlarge", "hs1.8xlarge", "cr1.8xlarge", "cc2.8xlarge", "cg1.4xlarge"],
))

SSHLocation = t.add_parameter(Parameter(
    "SSHLocation",
    ConstraintDescription="must be a valid IP CIDR range of the form x.x.x.x/x.",
    Description="The IP address range that can be used to access the web server using SSH.",
    Default="0.0.0.0/0",
    MinLength="9",
    AllowedPattern="(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})/(\\d{1,2})",
    MaxLength="18",
    Type="String",
))

RegistrationEMailAddress = t.add_parameter(Parameter(
    "RegistrationEMailAddress",
    AllowedPattern="([a-zA-Z0-9_\\-\\.]+)@((\\[[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.)|(([a-zA-Z0-9\\-]+\\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\\]?)",
    ConstraintDescription="Must be a valid EMail Address",
    Type="String",
    Description="[Required]:: Your EMail Address used for License and Registration of Perforce Helix Software and Services",
))

KeyName = t.add_parameter(Parameter(
    "KeyName",
    ConstraintDescription="must be the name of an existing EC2 KeyPair.",
    Type="AWS::EC2::KeyPair::KeyName",
    Description="[Required]:: Name of an EC2 KeyPair to enable SSH access to the instance.",
))

HostedZone = t.add_parameter(Parameter(
    "HostedZone",
    AllowedPattern="^(?!-)[a-zA-Z0-9-.]{1,63}(?<!-)$|^$",
    ConstraintDescription="Production:: Must be a valid Public Domain that is available in Route53 | Evaluation: NULL | Development: NULL",
    Type="String",
    Description="[Production]:: *The Domain of an pre-existing Amazon Route53 hosted zone. | [Evaluation]: Leave empty. | [Development]: Leave empty. | [Example]: perforce.com ",
))

EnvironmentType = t.add_parameter(Parameter(
    "EnvironmentType",
    Default="Evaluation",
    ConstraintDescription="Must specify Production, Evaluation, or Development.",
    Type="String",
    Description="[Required]:: Type of Environment to deploy: [Production]: Ready for preexisting Public Route53 Zone and Elastic IP Services. [Evaluation]: Ready for Software Evaluation at minimal costs. [Development]: Ready for Stack modifications.",
    AllowedValues=["Production", "Evaluation", "Development"],
))

InstanceType = t.add_parameter(Parameter(
    "InstanceType",
    Default="t2.micro",
    ConstraintDescription="must be a valid EC2 instance type.",
    Type="String",
    Description="[Required]:: MainInstance EC2 instance type",
    AllowedValues=["t1.micro", "t2.micro", "t2.small", "t2.medium", "m1.small", "m1.medium", "m1.large", "m1.xlarge", "m2.xlarge", "m2.2xlarge", "m2.4xlarge", "m3.medium", "m3.large", "m3.xlarge", "m3.2xlarge", "c1.medium", "c1.xlarge", "c3.large", "c3.xlarge", "c3.2xlarge", "c3.4xlarge", "c3.8xlarge", "c4.large", "c4.xlarge", "c4.2xlarge", "c4.4xlarge", "c4.8xlarge", "g2.2xlarge", "r3.large", "r3.xlarge", "r3.2xlarge", "r3.4xlarge", "r3.8xlarge", "i2.xlarge", "i2.2xlarge", "i2.4xlarge", "i2.8xlarge", "d2.xlarge", "d2.2xlarge", "d2.4xlarge", "d2.8xlarge", "hi1.4xlarge", "hs1.8xlarge", "cr1.8xlarge", "cc2.8xlarge", "cg1.4xlarge"],
))

P4DSuperPass = t.add_parameter(Parameter(
    "P4DSuperPass",
    Type="String",
    MaxLength="1024",
    NoEcho=True,
    Description="[Required]:: The P4D Super account password, 8 to 1024 characters in length",
    MinLength="8",
))
# Parameters End

# Mappings
t.add_mapping("AWSInstanceType2Arch",
{u'c1.medium': {u'Arch': u'PV64'},
 u'c1.xlarge': {u'Arch': u'PV64'},
 u'c3.2xlarge': {u'Arch': u'HVM64'},
 u'c3.4xlarge': {u'Arch': u'HVM64'},
 u'c3.8xlarge': {u'Arch': u'HVM64'},
 u'c3.large': {u'Arch': u'HVM64'},
 u'c3.xlarge': {u'Arch': u'HVM64'},
 u'c4.2xlarge': {u'Arch': u'HVM64'},
 u'c4.4xlarge': {u'Arch': u'HVM64'},
 u'c4.8xlarge': {u'Arch': u'HVM64'},
 u'c4.large': {u'Arch': u'HVM64'},
 u'c4.xlarge': {u'Arch': u'HVM64'},
 u'cc2.8xlarge': {u'Arch': u'HVM64'},
 u'cr1.8xlarge': {u'Arch': u'HVM64'},
 u'd2.2xlarge': {u'Arch': u'HVM64'},
 u'd2.4xlarge': {u'Arch': u'HVM64'},
 u'd2.8xlarge': {u'Arch': u'HVM64'},
 u'd2.xlarge': {u'Arch': u'HVM64'},
 u'g2.2xlarge': {u'Arch': u'HVMG2'},
 u'hi1.4xlarge': {u'Arch': u'HVM64'},
 u'hs1.8xlarge': {u'Arch': u'HVM64'},
 u'i2.2xlarge': {u'Arch': u'HVM64'},
 u'i2.4xlarge': {u'Arch': u'HVM64'},
 u'i2.8xlarge': {u'Arch': u'HVM64'},
 u'i2.xlarge': {u'Arch': u'HVM64'},
 u'm1.large': {u'Arch': u'PV64'},
 u'm1.medium': {u'Arch': u'PV64'},
 u'm1.small': {u'Arch': u'PV64'},
 u'm1.xlarge': {u'Arch': u'PV64'},
 u'm2.2xlarge': {u'Arch': u'PV64'},
 u'm2.4xlarge': {u'Arch': u'PV64'},
 u'm2.xlarge': {u'Arch': u'PV64'},
 u'm3.2xlarge': {u'Arch': u'HVM64'},
 u'm3.large': {u'Arch': u'HVM64'},
 u'm3.medium': {u'Arch': u'HVM64'},
 u'm3.xlarge': {u'Arch': u'HVM64'},
 u'r3.2xlarge': {u'Arch': u'HVM64'},
 u'r3.4xlarge': {u'Arch': u'HVM64'},
 u'r3.8xlarge': {u'Arch': u'HVM64'},
 u'r3.large': {u'Arch': u'HVM64'},
 u'r3.xlarge': {u'Arch': u'HVM64'},
 u't1.micro': {u'Arch': u'PV64'},
 u't2.medium': {u'Arch': u'HVM64'},
 u't2.micro': {u'Arch': u'HVM64'},
 u't2.small': {u'Arch': u'HVM64'}}
)

t.add_mapping("Environments",
{u'Development': {u'ValueTags': u'Dev'},
 u'Evaluation': {u'ValueTags': u'Eval'},
 u'Production': {u'ValueTags': u'Prod'}}
)

t.add_mapping("AWSRegionArch2AMI",
{u'ap-northeast-1': {u'HVM64': u'ami-cbf90ecb',
                     u'HVMG2': u'ami-6318e863',
                     u'PV64': u'ami-27f90e27'},
 u'ap-southeast-1': {u'HVM64': u'ami-68d8e93a',
                     u'HVMG2': u'ami-3807376a',
                     u'PV64': u'ami-acd9e8fe'},
 u'ap-southeast-2': {u'HVM64': u'ami-fd9cecc7',
                     u'HVMG2': u'ami-89790ab3',
                     u'PV64': u'ami-ff9cecc5'},
 u'cn-north-1': {u'HVM64': u'ami-f239abcb',
                 u'HVMG2': u'NOT_SUPPORTED',
                 u'PV64': u'ami-fa39abc3'},
 u'eu-central-1': {u'HVM64': u'ami-a8221fb5',
                   u'HVMG2': u'ami-7cd2ef61',
                   u'PV64': u'ami-ac221fb1'},
 u'eu-west-1': {u'HVM64': u'ami-a10897d6',
                u'HVMG2': u'ami-d5bc24a2',
                u'PV64': u'ami-bf0897c8'},
 u'sa-east-1': {u'HVM64': u'ami-b52890a8',
                u'HVMG2': u'NOT_SUPPORTED',
                u'PV64': u'ami-bb2890a6'},
 u'us-east-1': {u'HVM64': u'ami-1ecae776',
                u'HVMG2': u'ami-8c6b40e4',
                u'PV64': u'ami-1ccae774'},
 u'us-west-1': {u'HVM64': u'ami-d114f295',
                u'HVMG2': u'ami-f31ffeb7',
                u'PV64': u'ami-d514f291'},
 u'us-west-2': {u'HVM64': u'ami-e7527ed7',
                u'HVMG2': u'ami-abbe919b',
                u'PV64': u'ami-ff527ecf'}}
)
# Mappings End

# Resources
VPCGatewayAttachment = t.add_resource(VPCGatewayAttachment(
    "VPCGatewayAttachment",
    VpcId=Ref("VPC"),
    InternetGatewayId=Ref("InternetGateway"),
))

AppInstance = t.add_resource(Instance(
    "AppInstance",
    # Incorrect interpretation from cfn2py
    # Metadata=Init(
    #     { "SaltMinion": { "files": { "/tmp/init.sh": { "source": "https://s3-us-west-2.amazonaws.com/perforce-ami-us-west-2/init.sh", "mode": "0755" } }, "commands": { "setupMinion": { "command": "/tmp/init.sh 10.0.0.101 p4d-host" } } }, "configSets": { "All": ["SaltMinion"] } },
    # ),
    Metadata=cloudformation.Metadata(
        cloudformation.Init(
            cloudformation.InitConfigSets(
                DeploySalt=['SaltMinion'],
            ),
            SaltMinion=cloudformation.InitConfig(
                commands={
                    "SaltMinion": {
                        "files": { "/tmp/init.sh": {
                            "source": "https://s3-us-west-2.amazonaws.com/perforce-ami-us-west-2/init.sh", "mode": "0755" } },
                        "commands": {
                            "setupMinion": {
                                "command": "/tmp/init.sh 10.0.0.101 app-host" } } },
                        "configSets": { "All": ["SaltMinion"] },
                },
            ),
        )
    ),
    # Expedited Json Obj,
    # "AWS::CloudFormation::Init": {
    #     "configSets": {
    #         "All": [
    #             "SaltMinion"
    #         ]
    #     },
    #     "SaltMinion": {
    #         "files": {
    #             "/tmp/init.sh": {
    #                 "source": "https://s3-us-west-2.amazonaws.com/perforce-ami-us-west-2/init.s",
    #                 "mode": "0755"
    #             }
    #         },
    #         "commands": {
    #             "setupMinion": {
    #                 "command": "/tmp/init.sh 10.0.0.101 p4d-host"
    #             }
    #         }
    #     }
    # }
    # },
    UserData=Base64(
        Join("", ["#!/bin/bash -v\n",
                  "yum update -y aws-cfn-bootstrap\n",
                  "# Install the files and packages from the metadata\n",
                  "\n", "# Helper function\n",
                  "function error_exit\n",
                  "{\n",
                  "  /opt/aws/bin/cfn-signal -e 1 -r \"$1\" '", Ref("WaitHandle"),
                  "'\n",
                  "  exit 1\n",
                  "}\n",
                  "\n",
                  "# Install local config\n",
                  "/opt/aws/bin/cfn-init -v ",
                  "         --stack ",
                  Ref("AWS::StackName"),
                  "         --resource MainInstance ",
                  "         --configsets All ",
                  "         --access-key ", Ref("HostKeys"),
                  "         --secret-key ", GetAtt("HostKeys", "SecretAccessKey"),
                  "         --region ", Ref("AWS::Region"),
                  "\n",
                  "# Signal the status from cfn-init\n",
                  "/opt/aws/bin/cfn-signal -e $? ",
                  "         --stack ", Ref("AWS::StackName"),
                  "         --resource MainInstance ",
                  "         --region ", Ref("AWS::Region"),
                  "\n",
                  " > /var/tmp/cfn-init.output || error_exit 'Failed to run cfn-init'\n",
                  "# All is well so signal success\n",
                  "/opt/aws/bin/cfn-signal -e 0 -r \"Main Instance Stack setup complete\" '",
                  Ref("WaitHandle"),
                  "'\n"]
             )
    ),
    # Expedited Json Obj
    # "UserData": {
    #           "Fn::Base64": {
    #             "Fn::Join": [
    #               "",
    #               [
    #                 "#!/bin/bash -v\n",
    #                 "yum update -y aws-cfn-bootstrap\n",
    #                 "# Install the files and packages from the metadata\n",
    #                 "\n",
    #                 "# Helper function\n",
    #                 "function error_exit\n",
    #                 "{\n",
    #                 "  /opt/aws/bin/cfn-signal -e 1 -r \"$1\" '",
    #                 {
    #                   "Ref": "WaitHandle"
    #                 },
    #                 "'\n",
    #                 "  exit 1\n",
    #                 "}\n",
    #                 "\n",
    #                 "# Install local config\n",
    #                 "/opt/aws/bin/cfn-init -v ",
    #                 "         --stack ",
    #                 {
    #                   "Ref": "AWS::StackName"
    #                 },
    #                 "         --resource MainInstance ",
    #                 "         --configsets All ",
    #                 "         --access-key ",
    #                 {
    #                   "Ref": "HostKeys"
    #                 },
    #                 "         --secret-key ",
    #                 {
    #                   "Fn::GetAtt": [
    #                     "HostKeys",
    #                     "SecretAccessKey"
    #                   ]
    #                 },
    #                 "         --region ",
    #                 {
    #                   "Ref": "AWS::Region"
    #                 },
    #                 "\n",
    #                 "# Signal the status from cfn-init\n",
    #                 "/opt/aws/bin/cfn-signal -e $? ",
    #                 "         --stack ",
    #                 {
    #                   "Ref": "AWS::StackName"
    #                 },
    #                 "         --resource MainInstance ",
    #                 "         --region ",
    #                 {
    #                   "Ref": "AWS::Region"
    #                 },
    #                 "\n",
    #                 " > /var/tmp/cfn-init.output || error_exit 'Failed to run cfn-init'\n",
    #                 "# All is well so signal success\n",
    #                 "/opt/aws/bin/cfn-signal -e 0 -r \"Main Instance Stack setup complete\" '",
    #                 {
    #                   "Ref": "WaitHandle"
    #                 },
    #                 "'\n"
    #               ]
    #             ]
    #           }
    #         }
    #       },
    Tags=Tags(
        Name=Join(" - ", [FindInMap("Environments", Ref("EnvironmentType"), "ValueTags"), "Perforce Helix App Server", Ref("AWS::StackName")]),
    ),
    ImageId=FindInMap("AWSRegionArch2AMI", Ref("AWS::Region"), FindInMap("AWSInstanceType2Arch", Ref("InstanceType"), "Arch")),
    KeyName=Ref("KeyName"),
    InstanceType=Ref("InstanceType"),
    NetworkInterfaces=[
    NetworkInterfaceProperty(
        DeviceIndex="0",
        GroupSet=[Ref("VPCGroup")],
        DeleteOnTermination="true",
        AssociatePublicIpAddress="true",
        SubnetId=Ref("PublicSubnet"),
        PrivateIpAddress="10.0.0.51",
    ),
    ],
    DependsOn=["MainInstance"],
))

HostRecord = t.add_resource(RecordSetType(
    "HostRecord",
    Comment="DNS name for my instance.",
    Name=Join("", [Ref("SiteName"), ".", Ref("HostedZone"), "."]),
    HostedZoneName=Join("", [Ref("HostedZone"), "."]),
    ResourceRecords=[GetAtt("MainInstance", "PublicIp")],
    TTL="900",
    Type="A",
    DependsOn=["MainEIP"],
))

HostKeys = t.add_resource(AccessKey(
    "HostKeys",
    UserName=Ref("PerforceHelixIAMUser"),
))

MainServerSecurityGroup = t.add_resource(SecurityGroup(
    "MainServerSecurityGroup",
    SecurityGroupIngress=[{ "ToPort": "80", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "80" }, { "ToPort": "22", "IpProtocol": "tcp", "CidrIp": Ref("SSHLocation"), "FromPort": "22" }, { "ToPort": "1667", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "1667" }, { "ToPort": "443", "IpProtocol": "tcp", "CidrIp": "0.0.0.0/0", "FromPort": "443" }],
    VpcId=Ref("VPC"),
    GroupDescription="Allow access from HTTP/HTTPS and SSH and P4D over SSL traffic",
    Tags=Tags(
        Name=Join(" - ", [FindInMap("Environments", Ref("EnvironmentType"), "ValueTags"), "Perforce Helix Main Server SecurityGroup", Ref("AWS::StackName")]),
    ),
))

P4D = t.add_resource(Instance(
    "P4D",
    # Incorrect interpretation from cfn2py
    # Metadata=Init(
    #     { "SaltMinion": { "files": { "/tmp/init.sh": { "source": "https://s3-us-west-2.amazonaws.com/perforce-ami-us-west-2/init.sh", "mode": "0755" } }, "commands": { "setupMinion": { "command": "/tmp/init.sh 10.0.0.101 p4d-host" } } }, "configSets": { "All": ["SaltMinion"] } },
    # ),
    Metadata=cloudformation.Metadata(
        cloudformation.Init(
            cloudformation.InitConfigSets(
                DeploySalt=['SaltMinion'],
            ),
            SaltMinion=cloudformation.InitConfig(
                commands={
                    "configSets": {
                        "All": ["SaltMinion"]
                    },
                    "SaltMinion": {
                        "files": { "/tmp/init.sh": {
                            "source": "https://s3-us-west-2.amazonaws.com/perforce-ami-us-west-2/init.sh", "mode": "0755" } },
                        "commands": {
                            "setupMinion": {
                                "command": "/tmp/init.sh 10.0.0.101  p4d-host"
                            }
                        }
                    },
                },
            ),
        )
    ),
    # Expedited Json Obj
    # "AWS::CloudFormation::Init": {
    #     "configSets": {
    #         "All": [
    #             "SaltMinion"
    #         ]
    #     },
    #     "SaltMinion": {
    #         "files": {
    #             "/tmp/init.sh": {
    #                 "source": "https://s3-us-west-2.amazonaws.com/perforce-ami-us-west-2/init.sh",
    #                 "mode": "0755"
    #             }
    #         },
    #         "commands": {
    #             "setupMinion": {
    #                 "command": "/tmp/init.sh 10.0.0.101 p4d-host"
    #             }
    #         }
    #     }
    # }
    # },
    UserData=Base64(
        Join("", ["#!/bin/bash -v\n",
                  "yum update -y aws-cfn-bootstrap\n",
                  "# Install the files and packages from the metadata\n",
                  "\n", "# Helper function\n",
                  "function error_exit\n",
                  "{\n",
                  "  /opt/aws/bin/cfn-signal -e 1 -r \"$1\" '", Ref("WaitHandle"),
                  "'\n",
                  "  exit 1\n",
                  "}\n",
                  "\n",
                  "# Install local config\n",
                  "/opt/aws/bin/cfn-init -v ",
                  "         --stack ",
                  Ref("AWS::StackName"),
                  "         --resource MainInstance ",
                  "         --configsets All ",
                  "         --access-key ", Ref("HostKeys"),
                  "         --secret-key ", GetAtt("HostKeys", "SecretAccessKey"),
                  "         --region ", Ref("AWS::Region"),
                  "\n",
                  "# Signal the status from cfn-init\n",
                  "/opt/aws/bin/cfn-signal -e $? ",
                  "         --stack ", Ref("AWS::StackName"),
                  "         --resource MainInstance ",
                  "         --region ", Ref("AWS::Region"),
                  "\n",
                  " > /var/tmp/cfn-init.output || error_exit 'Failed to run cfn-init'\n",
                  "# All is well so signal success\n",
                  "/opt/aws/bin/cfn-signal -e 0 -r \"Main Instance Stack setup complete\" '",
                  Ref("WaitHandle"),
                  "'\n"]
             )
    ),
    # Expedited Json Obj
    # "UserData": {
    #           "Fn::Base64": {
    #             "Fn::Join": [
    #               "",
    #               [
    #                 "#!/bin/bash -v\n",
    #                 "yum update -y aws-cfn-bootstrap\n",
    #                 "# Install the files and packages from the metadata\n",
    #                 "\n",
    #                 "# Helper function\n",
    #                 "function error_exit\n",
    #                 "{\n",
    #                 "  /opt/aws/bin/cfn-signal -e 1 -r \"$1\" '",
    #                 {
    #                   "Ref": "WaitHandle"
    #                 },
    #                 "'\n",
    #                 "  exit 1\n",
    #                 "}\n",
    #                 "\n",
    #                 "# Install local config\n",
    #                 "/opt/aws/bin/cfn-init -v ",
    #                 "         --stack ",
    #                 {
    #                   "Ref": "AWS::StackName"
    #                 },
    #                 "         --resource MainInstance ",
    #                 "         --configsets All ",
    #                 "         --access-key ",
    #                 {
    #                   "Ref": "HostKeys"
    #                 },
    #                 "         --secret-key ",
    #                 {
    #                   "Fn::GetAtt": [
    #                     "HostKeys",
    #                     "SecretAccessKey"
    #                   ]
    #                 },
    #                 "         --region ",
    #                 {
    #                   "Ref": "AWS::Region"
    #                 },
    #                 "\n",
    #                 "# Signal the status from cfn-init\n",
    #                 "/opt/aws/bin/cfn-signal -e $? ",
    #                 "         --stack ",
    #                 {
    #                   "Ref": "AWS::StackName"
    #                 },
    #                 "         --resource MainInstance ",
    #                 "         --region ",
    #                 {
    #                   "Ref": "AWS::Region"
    #                 },
    #                 "\n",
    #                 " > /var/tmp/cfn-init.output || error_exit 'Failed to run cfn-init'\n",
    #                 "# All is well so signal success\n",
    #                 "/opt/aws/bin/cfn-signal -e 0 -r \"Main Instance Stack setup complete\" '",
    #                 {
    #                   "Ref": "WaitHandle"
    #                 },
    #                 "'\n"
    #               ]
    #             ]
    #           }
    #         }
    #       },
    Tags=Tags(
        Name=Join(" - ", [FindInMap("Environments", Ref("EnvironmentType"), "ValueTags"), "Perforce Helix P4D Server", Ref("AWS::StackName")]),
    ),
    ImageId=FindInMap("AWSRegionArch2AMI", Ref("AWS::Region"), FindInMap("AWSInstanceType2Arch", Ref("InstanceType"), "Arch")),
    KeyName=Ref("KeyName"),
    InstanceType=Ref("InstanceTypeP4D"),
    NetworkInterfaces=[
    NetworkInterfaceProperty(
        DeviceIndex="0",
        GroupSet=[Ref("VPCGroup")],
        DeleteOnTermination="true",
        AssociatePublicIpAddress="true",
        SubnetId=Ref("PublicSubnet"),
        PrivateIpAddress="10.0.0.201",
    ),
    ],
    DependsOn=["MainInstance"],
))

SubnetRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
    "SubnetRouteTableAssociation",
    SubnetId=Ref("PublicSubnet"),
    RouteTableId=Ref("PublicRouteTable"),
))

PublicRouteTable = t.add_resource(RouteTable(
    "PublicRouteTable",
    VpcId=Ref("VPC"),
    Tags=Tags(
        Name=Join(" - ", [FindInMap("Environments", Ref("EnvironmentType"), "ValueTags"), "Perforce Helix PublicRouteTable", Ref("AWS::StackName")]),
    ),
))

PublicRoute = t.add_resource(Route(
    "PublicRoute",
    GatewayId=Ref("InternetGateway"),
    DestinationCidrBlock="0.0.0.0/0",
    RouteTableId=Ref("PublicRouteTable"),
    DependsOn=["InternetGateway"],
))

PublicSubnet = t.add_resource(Subnet(
    "PublicSubnet",
    VpcId=Ref("VPC"),
    CidrBlock="10.0.0.0/24",
    Tags=Tags(
        Name=Join(" - ", [FindInMap("Environments", Ref("EnvironmentType"), "ValueTags"), "Perforce Helix Subnet", Ref("AWS::StackName")]),
    ),
))

MainInstance = t.add_resource(Instance(
    "MainInstance",
    # Incorrect interpretation from cfn2py
    # Metadata=Init(
    #     { "SaltMaster": { "files": { "/tmp/key_wait.sh": { "source": "https://s3-us-west-1.amazonaws.com/perforce-doug-test/salt-for-aws-cf/setup/key_wait.sh", "mode": "0755" }, "/tmp/init.sh": { "source": "https://s3-us-west-2.amazonaws.com/perforce-ami-us-west-2/init.sh", "mode": "0755" } }, "commands": { "setupMinion": { "command": "/tmp/init.sh 10.0.0.101 master" } } }, "configSets": { "All": ["SaltMaster"] } },
    # ),
    Metadata=cloudformation.Metadata(
        cloudformation.Init(
            cloudformation.InitConfigSets(
                DeploySalt=['SaltMaster'],
            ),
            SaltMinion=cloudformation.InitConfig(
                commands={
                    "configSets": {
                        "All": ["SaltMaster"]
                    },
                    "SaltMaster": {
                        "files": {
                            "/tmp/init.sh": {
                                "source": "https://s3-us-west-2.amazonaws.com/perforce-ami-us-west-2/init.sh",
                                "mode": "0755"
                        },
                            "/tmp/key_wait.sh": {
                                "source": "https://s3-us-west-2.amazonaws.com/perforce-ami-us-west-2/key_wait.sh",
                                "mode": "0755"
                            }
                        },
                        "commands": {
                            "setupMinion": {
                                "command": "/tmp/init.sh 10.0.0.101 master"
                            }
                        }
                    },
                },
            ),
        )
    ),
    # Expedited Json Object
    # "AWS::CloudFormation::Init": {
    # "configSets": {
    #     "All": [
    #         "SaltMaster"
    #     ]
    # },
    # "SaltMaster": {
    #     "files": {
    #         "/tmp/init.sh": {
    #             "source": "https://s3-us-west-2.amazonaws.com/perforce-ami-us-west-2/init.sh",
    #             "mode": "0755"
    #         },
    #         "/tmp/key_wait.sh": {
    #             "source": "https://s3-us-west-2.amazonaws.com/perforce-ami-us-west-2/key_wait.sh",
    #             "mode": "0755"
    #         }
    #     },
    #     "commands": {
    #         "setupMinion": {
    #             "command": "/tmp/init.sh 10.0.0.101 master"
    #         }
    #     }
    # }
    # }
    # },
    UserData=Base64(
        Join("", ["#!/bin/bash -v\n",
                  "yum update -y aws-cfn-bootstrap\n",
                  "# Install the files and packages from the metadata\n",
                  "\n", "# Helper function\n",
                  "function error_exit\n",
                  "{\n",
                  "  /opt/aws/bin/cfn-signal -e 1 -r \"$1\" '", Ref("WaitHandle"),
                  "'\n",
                  "  exit 1\n",
                  "}\n",
                  "\n",
                  "# Install local config\n",
                  "/opt/aws/bin/cfn-init -v ",
                  "         --stack ",
                  Ref("AWS::StackName"),
                  "         --resource MainInstance ",
                  "         --configsets All ",
                  "         --access-key ", Ref("HostKeys"),
                  "         --secret-key ", GetAtt("HostKeys", "SecretAccessKey"),
                  "         --region ", Ref("AWS::Region"),
                  "\n",
                  "# Signal the status from cfn-init\n",
                  "/opt/aws/bin/cfn-signal -e $? ",
                  "         --stack ", Ref("AWS::StackName"),
                  "         --resource MainInstance ",
                  "         --region ", Ref("AWS::Region"),
                  "\n",
                  " > /var/tmp/cfn-init.output || error_exit 'Failed to run cfn-init'\n",
                  "# All is well so signal success\n",
                  "/opt/aws/bin/cfn-signal -e 0 -r \"Main Instance Stack setup complete\" '",
                  Ref("WaitHandle"),
                  "'\n"]
             )
    ),
    # Expedited Json Obj
    # "UserData": {
    #           "Fn::Base64": {
    #             "Fn::Join": [
    #               "",
    #               [
    #                 "#!/bin/bash -v\n",
    #                 "yum update -y aws-cfn-bootstrap\n",
    #                 "# Install the files and packages from the metadata\n",
    #                 "\n",
    #                 "# Helper function\n",
    #                 "function error_exit\n",
    #                 "{\n",
    #                 "  /opt/aws/bin/cfn-signal -e 1 -r \"$1\" '",
    #                 {
    #                   "Ref": "WaitHandle"
    #                 },
    #                 "'\n",
    #                 "  exit 1\n",
    #                 "}\n",
    #                 "\n",
    #                 "# Install local config\n",
    #                 "/opt/aws/bin/cfn-init -v ",
    #                 "         --stack ",
    #                 {
    #                   "Ref": "AWS::StackName"
    #                 },
    #                 "         --resource MainInstance ",
    #                 "         --configsets All ",
    #                 "         --access-key ",
    #                 {
    #                   "Ref": "HostKeys"
    #                 },
    #                 "         --secret-key ",
    #                 {
    #                   "Fn::GetAtt": [
    #                     "HostKeys",
    #                     "SecretAccessKey"
    #                   ]
    #                 },
    #                 "         --region ",
    #                 {
    #                   "Ref": "AWS::Region"
    #                 },
    #                 "\n",
    #                 "# Signal the status from cfn-init\n",
    #                 "/opt/aws/bin/cfn-signal -e $? ",
    #                 "         --stack ",
    #                 {
    #                   "Ref": "AWS::StackName"
    #                 },
    #                 "         --resource MainInstance ",
    #                 "         --region ",
    #                 {
    #                   "Ref": "AWS::Region"
    #                 },
    #                 "\n",
    #                 " > /var/tmp/cfn-init.output || error_exit 'Failed to run cfn-init'\n",
    #                 "# All is well so signal success\n",
    #                 "/opt/aws/bin/cfn-signal -e 0 -r \"Main Instance Stack setup complete\" '",
    #                 {
    #                   "Ref": "WaitHandle"
    #                 },
    #                 "'\n"
    #               ]
    #             ]
    #           }
    #         }
    #       },
    Tags=Tags(
        Name=Join(" - ", [FindInMap("Environments", Ref("EnvironmentType"), "ValueTags"), "Perforce Helix Main Server", Ref("AWS::StackName")]),
    ),
    ImageId=FindInMap("AWSRegionArch2AMI", Ref("AWS::Region"), FindInMap("AWSInstanceType2Arch", Ref("InstanceType"), "Arch")),
    KeyName=Ref("KeyName"),
    InstanceType=Ref("InstanceType"),
    NetworkInterfaces=[
    NetworkInterfaceProperty(
        DeviceIndex="0",
        GroupSet=[Ref("MainServerSecurityGroup"), Ref("VPCGroup")],
        DeleteOnTermination="true",
        AssociatePublicIpAddress="true",
        SubnetId=Ref(PublicSubnet),
        PrivateIpAddress="10.0.0.101",
    ),
    ],
    DependsOn=["PublicRoute"],
))

InternetGateway = t.add_resource(InternetGateway(
    "InternetGateway",
    Tags=Tags(
        Name=Join(" - ", [FindInMap("Environments", Ref("EnvironmentType"), "ValueTags"), "Perforce Helix InternetGateway", Ref("AWS::StackName")]),
    ),
))

VPC = t.add_resource(VPC(
    "VPC",
    EnableDnsSupport="true",
    CidrBlock="10.0.0.0/16",
    EnableDnsHostnames="true",
    Tags=Tags(
        Name=Join(" - ", [FindInMap("Environments", Ref("EnvironmentType"), "ValueTags"), "Perforce Helix VPC", Ref("AWS::StackName")]),
    ),
))

RegionRecord = t.add_resource(RecordSetType(
    "RegionRecord",
    Comment="DNS name for my instance.",
    Name=Join("", [Ref("SiteName"), ".", Ref("AWS::Region"), ".", Ref("HostedZone"), "."]),
    HostedZoneName=Join("", [Ref("HostedZone"), "."]),
    ResourceRecords=[GetAtt("MainInstance", "PublicIp")],
    TTL="900",
    Type="A",
    DependsOn=["MainEIP"],
))

MainEIP = t.add_resource(EIP(
    "MainEIP",
    InstanceId=Ref("MainInstance"),
    Domain="vpc",
))

VPCGroup = t.add_resource(SecurityGroup(
    "VPCGroup",
    SecurityGroupIngress=[{ "ToPort": 65535, "IpProtocol": "tcp", "CidrIp": "10.0.0.0/16", "FromPort": 0 }],
    VpcId=Ref(VPC),
    GroupDescription="Allow access to things on the VPC",
    Tags=Tags(
        Name=Join(" - ", [FindInMap("Environments", Ref("EnvironmentType"), "ValueTags"), "Perforce Helix VPC Group", Ref("AWS::StackName")]),
    ),
))

WaitCondition = t.add_resource(WaitCondition(
    "WaitCondition",
    Handle=Ref("WaitHandle"),
    Timeout="350",
    DependsOn=["P4D", "MainInstance", "AppInstance"],
))

PerforceHelixIAMUser = t.add_resource(User(
   "PerforceHelixIAMUser",
    Path="/",
    Policies=[
        Policy(
            PolicyName="PerforceHelixR53DNSPolicy",
            PolicyDocument=awacs.aws.Policy(
                Statement=[
                    awacs.aws.Statement(
                        Effect=awacs.aws.Allow,
                        Action=[awacs.aws.Action("route53", "ChangeResourceRecordSets")],
                        Resource=["arn:aws:route53:::change/*"],
                    ),
                ],
            )
        ),
        Policy(
            PolicyName="PerforceHelixDescribeStackResource",
            PolicyDocument=awacs.aws.Policy(
                Statement=[
                    awacs.aws.Statement(
                        Effect=awacs.aws.Allow,
                        Action=[awacs.aws.Action("cloudformation", "DescribeStackResource")],
                        Resource=["*"],
                    ),
                ],
            )
        ),
    ]
))

WaitHandle = t.add_resource(WaitConditionHandle(
    "WaitHandle",
))

# Resources End

# Outputs
HostedZoneFQDN = t.add_output(Output(
    "HostedZoneFQDN",
    Value=Ref("HostRecord"),
    Description="FQDN.",
    Condition="ProdNotify",
))

AvailabilityZoneMainInstance = t.add_output(Output(
    "AvailabilityZoneMainInstance",
    Description="MainInstance Deployed to Availability Zone.",
    Value=GetAtt("AppInstance", "AvailabilityZone"),
))

PrivateDnsNameMainInstance = t.add_output(Output(
    "PrivateDnsNameMainInstance",
    Value=GetAtt("MainInstance", "PrivateDnsName"),
    Description="Private Domain Name.",
    Condition="DevNotify",
))

P4PORT = t.add_output(Output(
    "P4PORT",
    Description="Perforce P4PORT.",
    Value=If("ProdNotify", Join("", [ Ref("HostRecord"), ":1666"]), Join("", [GetAtt("MainInstance", "PublicIp"), ":1666"])),
    # Expedited Json Obj
    # "Value": {
    #     "Fn::If": [
    #         "ProdNotify",
    #         {
    #             "Fn::Join": [
    #                 "",
    #                 [
    #                     {
    #                         "Ref": "HostRecord"
    #                     },
    #                     ":1666"
    #                 ]
    #             ]
    #         },
    #         {
    #             "Fn::Join": [
    #                 "",
    #                 [
    #                     {
    #                         "Fn::GetAtt": [
    #                             "MainInstance",
    #                             "PublicIp"
    #                         ]
    #                     },
    #                     ":1666"
    #                 ]
    #             ]
    #         }
    #     ]
    # }
))

SiteName = t.add_output(Output(
    "SiteName",
    Value=Ref(SiteName),
    Description="Site name.",
    Condition="ProdNotify",
))

PrivateDnsNameP4D = t.add_output(Output(
    "PrivateDnsNameP4D",
    Value=GetAtt("P4D", "PrivateDnsName"),
    Description="Private Domain Name.",
    Condition="DevNotify",
))

PrivateDnsNameAppInstance = t.add_output(Output(
    "PrivateDnsNameAppInstance",
    Value=GetAtt("AppInstance", "PrivateDnsName"),
    Description="Private Domain Name.",
    Condition="DevNotify",
))

PrivateIpMainInstance = t.add_output(Output(
    "PrivateIpMainInstance",
    Value=GetAtt("MainInstance", "PrivateIp"),
    Description="Private IP Address for MainInstance.",
    Condition="DevNotify",
))

PrivateIpAppInstance = t.add_output(Output(
    "PrivateIpAppInstance",
    Value=GetAtt("AppInstance", "PrivateIp"),
    Description="Private IP Address for AppInstance.",
    Condition="DevNotify",
))

PublicIp = t.add_output(Output(
    "PublicIp",
    Description="Public IP Address for your Deployment.",
    Value=GetAtt("MainInstance", "PublicIp"),
))


URL = t.add_output(Output(
    "URL",
    Description="Perforce Helix application URL.",
    Value=If("ProdNotify", Join("", ["http://", Ref("HostRecord")]), Join("", ["http://", GetAtt("MainInstance", "PublicDnsName")])),
    # Expedited Json Obj
    #       "Value": {
    #         "Fn::If": [
    #           "ProdNotify",
    #           {
    #             "Fn::Join": [
    #               "",
    #               [
    #                 "http://",
    #                 {
    #                   "Ref": "HostRecord"
    #                 }
    #               ]
    #             ]
    #           },
    #           {
    #             "Fn::Join": [
    #               "",
    #               [
    #                 "http://",
    #                 {
    #                   "Fn::GetAtt": [
    #                     "MainInstance",
    #                     "PublicDnsName"
    #                   ]
    #                 }
    #               ]
    #             ]
    #           }
    #         ]
    #       }
    #     },
))

RegistrationEMailAddress = t.add_output(Output(
    "RegistrationEMailAddress",
    Description="Registration EMail Address.",
    Value=Ref("RegistrationEMailAddress"),
))

HostedZone = t.add_output(Output(
    "HostedZone",
    Value=Ref("HostedZone"),
    Description="Route 53 Domain.",
    Condition="ProdNotify",
))

AvailabilityZoneAppInstance = t.add_output(Output(
    "AvailabilityZoneAppInstance",
    Description="AppInstance Deployed to Availability Zone.",
    Value=GetAtt("AppInstance", "AvailabilityZone"),
))

PublicDnsMainInstance = t.add_output(Output(
    "PublicDnsMainInstance",
    Description="Public Domain Name for your deployment.",
    Value=If("ProdNotify", Ref("HostRecord"), GetAtt("MainInstance", "PublicDnsName")),
    # Expedited Json Obj
    # "Value": {
    #         "Fn::If": [
    #           "ProdNotify",
    #           {
    #             "Ref": "HostRecord"
    #           },
    #           {
    #             "Fn::GetAtt": [
    #               "MainInstance",
    #               "PublicDnsName"
    #             ]
    #           }
    #         ]
    #       }
))

EnvironmentType = t.add_output(Output(
    "EnvironmentType",
    Description="Deployment Type.",
    Value=Ref("EnvironmentType"),
))

AvailabilityZoneP4D = t.add_output(Output(
    "AvailabilityZoneP4D",
    Description="P4D Deployed to Availability Zone.",
    Value=GetAtt("P4D", "AvailabilityZone"),
))

PrivateIpP4D = t.add_output(Output(
    "PrivateIpP4D",
    Value=GetAtt("P4D", "PrivateIp"),
    Description="Private IP Address for P4D.",
    Condition="DevNotify",
))

# Outputs End

print(t.to_json())
