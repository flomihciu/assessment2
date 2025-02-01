# Define the provider
provider "aws" {
  region = "us-east-1"  # Change this to your desired region
}

# Create a security group that allows inbound traffic on port 80 (HTTP), 22 (SSH), and 5432 (PostgreSQL)
resource "aws_security_group" "web_sg" {
  name        = "flo-exam2-sg"
  description = "Allow inbound HTTP, SSH, and PostgreSQL traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Adjust as necessary for security (this could be limited to your EC2 instance's IP)
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "flo-exam2-sg"
  }
}

# Create a VPC with a unique CIDR block and a Name tag
resource "aws_vpc" "main" {
  cidr_block = "172.15.0.0/16"
  enable_dns_support = true
  enable_dns_hostnames = true

  tags = {
    Name = "flo-exam-vpc"  # This is the name you want to assign to the VPC
  }
}

# Create subnets for the EC2 instance and RDS instance in different availability zones
resource "aws_subnet" "subnet_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "172.15.2.0/24"  # Adjust this as needed
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
}

resource "aws_subnet" "subnet_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "172.15.3.0/24"  # Adjust this as needed
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true
}

# Create a subnet for the EC2 instance
resource "aws_subnet" "main_subnet" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "172.15.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
}

# Create an internet gateway for internet access
resource "aws_internet_gateway" "main_igw" {
  vpc_id = aws_vpc.main.id
}

# Associate the subnet with the internet gateway
resource "aws_route_table" "main_route_table" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main_igw.id
  }
}

resource "aws_route_table_association" "main_route_association" {
  subnet_id      = aws_subnet.main_subnet.id
  route_table_id = aws_route_table.main_route_table.id
}

# Create an EC2 instance
resource "aws_instance" "target_node" {
  ami                    = "ami-0669774ba23136180"
  instance_type          = "t2.micro"
  subnet_id             = aws_subnet.main_subnet.id
  security_groups       = [aws_security_group.web_sg.id]
  associate_public_ip_address = true
  key_name              = "flo-east1"
  tags = {
    Name = "flo-target-node"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Create an Elastic IP and associate it with the EC2 instance
resource "aws_eip" "public_ip" {
  instance = aws_instance.target_node.id
}

resource "aws_key_pair" "deployer_key" {
  key_name   = "deployer-key"
  public_key = file("/home/flomihciu/devops/tfdocker/flo-east1.pub")
}

# Create a DB subnet group for RDS (PostgreSQL)
resource "aws_db_subnet_group" "main" {
  name        = "my-db-subnet-group"
  description = "Subnet group for RDS instances"
  subnet_ids  = [
    aws_subnet.subnet_a.id,  # Subnet in us-east-1a
    aws_subnet.subnet_b.id,  # Subnet in us-east-1b
  ]

  tags = {
    Name = "my-db-subnet-group"
  }
}

# Create an RDS PostgreSQL instance
resource "aws_db_instance" "my_postgres_db" {
  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "14.12"
  instance_class       = "db.t3.micro"
  db_subnet_group_name = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.web_sg.id]
  db_name              = "mydatabase"
  username             = "flo"
  password             = "password123"  # Use a secure method to handle passwords (e.g., Secrets Manager)
  multi_az             = false
  publicly_accessible  = true

  tags = {
    Name = "my-postgres-db"
  }
}

# Outputs
output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.target_node.public_ip
}

output "instance_private_ip" {
  description = "Private IP of the EC2 instance"
  value       = aws_instance.target_node.private_ip
}

output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.target_node.id
}

output "elastic_ip" {
  description = "Elastic IP assigned to the EC2 instance"
  value       = aws_eip.public_ip
}

output "db_instance_endpoint" {
  description = "Endpoint of the PostgreSQL RDS instance"
  value       = aws_db_instance.my_postgres_db.endpoint
}

output "db_instance_id" {
  description = "ID of the PostgreSQL RDS instance"
  value       = aws_db_instance.my_postgres_db.id
}
