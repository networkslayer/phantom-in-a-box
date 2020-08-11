variable "private_key_path" {
  description = <<DESCRIPTION
Path to the SSH private key to be used for authentication.
Ensure this keypair is added to your local SSH agent so provisioners can
connect.

Example: ~/.ssh/terraform.key
Defaults to: ~/.ssh/id_rsa
DESCRIPTION
  default = "~/.ssh/id_rsa"
}

variable "key_name" {
  description = "Desired name of AWS key pair"
}


variable "ip_whitelist" {
  description = "A list of CIDRs that will be allowed to access the EC2 instances"
  type        = list(string)
}


#environment variables
variable "phantom_server" {
  default = "1"
}


variable "phantom_server_private_ip" { }
variable "use_packer_amis" { }
variable "phantom_packer_ami" { }


#ansible variables
# ---------------------- #
# general
variable "region" { }


# Phantom server
variable "phantom_admin_password" { }
variable "phantom_community_username" { }
variable "phantom_community_password" { }
