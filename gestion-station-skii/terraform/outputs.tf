output "vpc_id" {
  description = "ID du VPC créé"
  value       = aws_vpc.my_vpc.id
}

output "public_subnet_ids" {
  description = "IDs des sous-réseaux publics"
  value       = aws_subnet.public_subnets[*].id
}

output "private_subnet_ids" {
  description = "IDs des sous-réseaux privés"
  value       = aws_subnet.private_subnets[*].id
}

output "cluster_endpoint" {
  description = "Endpoint du cluster EKS"
  value       = aws_eks_cluster.my_cluster.endpoint
}

output "cluster_security_group_id" {
  description = "Security Group ID du cluster EKS"
  value       = aws_security_group.eks_cluster_sg.id
}
