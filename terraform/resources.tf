provider "aws" {
  region     =  var.region
}

module "networkModule" {
  source			  = "./modules/network"
	key_name		  = var.key_name
  ip_whitelist  = var.ip_whitelist
}

module "phantom-server" {
  source                     = "./modules/phantom-server"
  phantom_server             = var.phantom_server
  private_key_path           = var.private_key_path
  key_name                   = var.key_name
  vpc_security_group_ids     = module.networkModule.sg_vpc_id
  ec2_subnet_id              = module.networkModule.ec2_subnet_id
  phantom_server_private_ip  = var.phantom_server_private_ip
  phantom_admin_password     = var.phantom_admin_password
  phantom_community_username = var.phantom_community_username
  phantom_community_password = var.phantom_community_password
  use_packer_amis            = var.use_packer_amis
  phantom_packer_ami         = var.phantom_packer_ami
}

