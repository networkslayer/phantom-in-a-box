

data "aws_availability_zones" "available" {}

locals {
  cluster_name = "cluster_${var.key_name}"
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "2.6.0"

  name                 = "vpc_${var.key_name}"
  cidr                 = "10.0.0.0/16"
  azs                  = data.aws_availability_zones.available.names
  public_subnets      = ["10.0.1.0/24", "10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
  private_subnets       = ["10.0.14.0/24", "10.0.15.0/24", "10.0.16.0/24"]
  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true


}


resource "aws_security_group" "default" {
  name        = "sg_public_subnets_${var.key_name}"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = concat(var.ip_whitelist, ["10.0.0.0/16"])
  }

  egress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    cidr_blocks     = ["0.0.0.0/0"]
  }
}

