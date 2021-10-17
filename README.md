# nat-gateway-fqdn-target-lambda

> This page should be treated as a draft, a more detailed version will come up later.

This is an AWS lambda function written in Python that allows you to resolve FQDN and update the VPC route table with the FQDN IP addresses.

## What is it for? 
When working with NAT Gateway, you are charged $ 0.045 per gigabyte for traffic passing through the NAT Gateway (Ingress/Egress).

In some cases, the use of NAT Gateway is only for a specific API. So instead of routing all the traffic through the NAT Gateway, you can route only the endpoint IP addresses (a specific API provider, for example) and save costs.

## Limitations
Please review the [maximum amount of routes in the VPC route table](https://docs.aws.amazon.com/vpc/latest/userguide/amazon-vpc-limits.html#vpc-limits-route-tables)


## How to install
- Create a lambda function with Python runtime.
- Set the function timeout to 60 seconds. (the average runtime is 450ms)
- Define the following Environment variables:

route_table_id - the route table id. (starts with *rtb-*).

endpoints_name_list - the FQDN you would like to resolve (for example: google.com).
For multiple endpoints, please use the comma sign between endpoints (for example: google.com,bing.com)

nat_gw_id - that nat gateway id (starts with *nat-*)

- Use the following IAM Policy:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ec2:CreateRoute",
                "ec2:DeleteRoute",
                "ec2:DescribeRouteTables"
            ],
            "Resource": "*"
        }
    ]
}
```
- Create an EventBridge rule to invoke the function every few minutes.
- Check that the tutorial works using an endpoint traceroute.


Important note:
If you use a Geo based FQDN (GeoDNS) address like ALB/ELB/RDS/Redshift. Please run the function from the **same region** where the servers are located.
If you use this script to resolver CloudFront addresses, you might need to run the script from each availibility zone with a dedicated route table, because CloudFront might return different addresses per availability zones.

Credits: 
The script was written by Or Zaida in collaboration with Avi Keinan from DoiT IL office.
