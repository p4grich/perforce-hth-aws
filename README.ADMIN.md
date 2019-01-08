Welcome to the Perforce AWS Prototype Template Administrative Notes.

November 14th. 2016  

Things you will need to know.
 - AWS Route 53 Basics
 - EC2 Basics
 - EC2 and EBS volumes, Pricing vs Performance 
 - AWS IAM Roles and policys.
 - CloudFormation and it's Caveats
 - How to install a SSL Certificate
 - Perforce Checkpoints

Things you should know.
 - Perforce Administration 
 - Linux Administration 
 - Json, Yaml, Python, SaltStack
 - GitHub - cloudtools/troposphere

Things not included but will need to be planned for appropriately.     
 - Backups of EBS Volumes
 - Backups of EC2 Hosts 
 - Perforce Checkpoint handling
   https://www.perforce.com/perforce/r15.1/manuals/p4sag/index.html
 - Your backup strategy is your responsibility.  

What has and has not been tested.
 - Deployment of the AWS Template. "Tested"
 - CloudFormation stack updating or change sets. "Not tested" 

Deployment types.
 - Production
   Valid 53 Domain for accessing your site.
   Elastic IP Address

 - Evaluation 
   AWS Public DNS Only
   DHCP Public IP

 - Development 
   AWS Public DNS Only
   DHCP Public IP

Common issues.
 - Broken yum repositories and or missing/changed pgp package keys that impede deployment.

   CloudFormation common errors when SaltStack fails to deploy the applications on your EC2 hosts because of yum or salt bootstrap related issues.  

   Status          Type                                Logical ID    Status reason

   CREATE_FAILED   AWS::CloudFormation::Stack          skunkworks    The following resource(s) failed to create: [WaitCondition].

   CREATE_FAILED   AWS::CloudFormation::WaitCondition                WaitCondition   WaitCondition received failed message: 'salt deploy complete' for uniqueId: i-xxxxxxxxxxxx
   
SSL Certificates. 

  This document will not discuss how to get or make an SSL Certificate. 

  But will cover the proper install of the certificate on HAProxy.
  
  - SSH to your "Prod - Perforce Helix Main Server - skunkworks" EC2 Host.

  - sudo to root. `sudo bash`

  - Make note of SSL Certificate location:
    Command: `cat /etc/haproxy/haproxy.cfg |grep ":443"`
    Result: "bind      *:443         ssl crt /etc/ssl/p4www.pem" 

  - Change working directory to:
    Command: `cd /etc/ssl/`

  - Review and ensure the file permissions of the SSL Certificate Pem file are mode 600 or 400:
    Command:  `ls -al /etc/ssl/p4www.pem`
    Result: "rw-------  1 root root 8440 Nov  8 18:37 p4www.pem"

  - For the SSL Certificate to work properly it must include the following supporting certificates in the correct order. 

    -----BEGIN RSA PRIVATE KEY----

      First: your private key here.

    -----END RSA PRIVATE KEY-----

    -----BEGIN CERTIFICATE-----

      Second: your issued certificate here.

    -----END CERTIFICATE-----

    -----BEGIN CERTIFICATE-----

      Third: your root or intermediate certificate authority here.

    -----END CERTIFICATE-----

    -----BEGIN CERTIFICATE-----

      Forth: your root or intermediate certificate authority here.

    -----END CERTIFICATE-----

    Etc........ 


**Pricing vs Performance**

  It's important that you read and understand the AWS documentation on Costs vs Performance when choosing to allocate both EC2 and EBS resources. 

  Getting it wrong means you can have both a deployment that does not perform and is expensive. 

  1: https://aws.amazon.com/ebs/pricing/ 

  2: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSVolumeTypes.html 
  
  Minimum Requirements for P4D on EC2 Host.

  Not including any requirements for effective use of EBS volumes.
   - Ram: 2GB ~ 50 to 100 Perforce Users 
   - CPU: 1

Debugging the CloudFormation deployment:
 - To prevent the EC2 hosts from auto deleting on deployment failure Set Rollback to "no"
   CloudFormation -> Options ->  Advanced -> Rollback on failure -> "No"
   This will allow you to ssh to the EC2 hosts and evaluate the appropriate log files. 

Safe operations tips & tricks
 - Review the CloudFormation template and ensure the EBS Volumes have an appropriate "DeletionPolicy" of Retain or Snapshot prior to any deployment, update, or change.
   CloudFormation can or will destroy EBS Volumes once a CloudFormation operation is made.

 - Halt p4broker on Main EC2 host, Checkpoint P4D then make backups or a snapshots of your EBS Volumes prior to making any CloudFormation changes.

 - Highly recommend running a second smaller production deployment in a different AWS region. 
   This will allow you to stage and evaluate all CloudFormation changes or other changes that may impact your primary site.


**Security Notes** 

  Post deployment considerations.     
  - The P4D Super password that is set at the time of deployment is stored in the CloudFormation stack.
    The same password is used to setup the deployed IAM credentials used by the 'aws' client tool as well as the P4D super user.
    It is strongly recommended you change the P4D super user password and the 'aws' credentials file on all EC2 hosts in the stack.    

Simple Stack policies:
  AWS Stack policies will not PREVENT deletion of your deployment.
  
  Deny: 

    aws cloudformation set-stack-policy --stack-name skunkworks --stack-policy-url https://s3-us-west-2.amazonaws.com/perforce-ami-policy/deny-updates-all.policy

  Allow: 

    aws cloudformation set-stack-policy --stack-name skunkworks --stack-policy-url https://s3-us-west-2.amazonaws.com/perforce-ami-policy/allow-updates-all.policy

 Notes: 

  https://www.perforce.com/perforce/r15.1/manuals/p4sag/index.html

  http://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#Using_CreateUser_console 

  http://docs.aws.amazon.com/codedeploy/latest/userguide/how-to-create-iam-instance-profile.html

  http://docs.aws.amazon.com/codedeploy/latest/userguide/getting-started-setup.html 

  https://aws.amazon.com/blogs/devops/aws-cloudformation-security-best-practices/

  http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/protect-stack-resources.html

