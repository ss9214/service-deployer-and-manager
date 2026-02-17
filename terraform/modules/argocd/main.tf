variable "k8s_endpoint" {
  description = "Kubernetes API endpoint"
  type        = string
}

variable "k8s_ca_cert" {
  description = "Kubernetes cluster CA certificate"
  type        = string
  sensitive   = true
}

variable "k8s_token" {
  description = "Kubernetes cluster token"
  type        = string
  sensitive   = true
}

variable "platform_name" {
  description = "Platform name"
  type        = string
}

# Note: This is a simplified version
# In production, you'd use the Helm provider or kubectl provider

resource "null_resource" "argocd_install" {
  provisioner "local-exec" {
    command = <<-EOF
      # This would be executed after K3s is ready
      # In a real implementation, we'd use remote-exec or the Helm provider
      echo "ArgoCD installation would happen here"
      echo "kubectl create namespace argocd"
      echo "kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml"
    EOF
  }

  triggers = {
    k8s_endpoint = var.k8s_endpoint
  }
}

output "argocd_url" {
  description = "ArgoCD web UI URL"
  value       = "${replace(var.k8s_endpoint, "6443", "8080")}/argocd"
}

output "admin_password" {
  description = "ArgoCD initial admin password"
  value       = "Please retrieve from K8s secret: kubectl -n argocd get secret argocd-initial-admin-secret"
  sensitive   = true
}
