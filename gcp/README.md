# Provision a GKE Cluster

This repo is a companion repo to the [Provision a GKE Cluster tutorial](https://developer.hashicorp.com/terraform/tutorials/kubernetes/gke), containing Terraform configuration files to provision an GKE cluster on GCP.

This repo also creates a VPC and subnet for the GKE cluster. This is not
required but highly recommended to keep your GKE cluster isolated.

## GCP Infrastructure:
- Add project/region to terraform.tfvars

- Pull Terraform code

    ```
    cd gcp && bash pull.sh
    ```

- Provision resources

    ```
    cd learn-terraform-provision-gke-cluster && terraform init && terraform apply
    ```

- Kubectl Plug-in

    ```
    gcloud components install gke-gcloud-auth-plugin
    ```

- Configure kubectl

    ```
    gcloud container clusters get-credentials $(terraform output -raw kubernetes_cluster_name) --region $(terraform output -raw region)
    ```

- Deploy

    ```
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0-beta8/aio/deploy/recommended.yaml
    ```

- K8s Dashboard

    ```
    kubectl proxy
    ```

- In a web browser

    ```
    http://127.0.0.1:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
    ```

- Authenticate (should be a one time thing)

    ```
    kubectl apply -f https://raw.githubusercontent.com/hashicorp/learn-terraform-provision-gke-cluster/main/kubernetes-dashboard-admin.rbac.yaml
    ```
- Code to get your token for K8s UI DB

    ```
    kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep service-controller-token | awk '{print $1}')
    ```

## Argo Provision

- Install Argo Workflows

    ```
    kubectl create namespace argo
    ```

- Ensure namespace was created (optional, but it should say argo)

    ```
    kubectl get namespace
    ```

- Install argo on K8s
    - Grab [latest release](https://github.com/argoproj/argo-workflows/releases) and edit the url below

    ```
    kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v<< ADD VERSION NUMBER HERE (i.e 3.4.3)>>/install.yaml ```

- Patch argo-server auth

    ```
    kubectl patch deployment \
    argo-server \
    --namespace argo \
    --type='json' \
    -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/args", "value": [
    "server",
    "--auth-mode=server"
    ]}]'
    ```

- Port-forward the UI

    ```
    kubectl -n argo port-forward deployment/argo-server 2746:2746
    ```

- Accept TLS Certification [https://localhost:2746](https://localhost:2746)

- [Install Argo Workflow CLI on local machine](https://github.com/argoproj/argo-workflows/releases)

    - Test Install

        ```
        argo version
        ```

- Submit a workload

    - Sample workload
        ```
        argo submit -n argo --watch https://raw.githubusercontent.com/argoproj/argo-workflows/master/examples/hello-world.yaml
        ```

    - List workloads
        ```
        argo list -n argo
        ```
    - Details of a workload
        ```
        argo get -n argo @latest
        ```

## Clean-up
- Destroy resources
    ```
    terraform destroy
    ```