# Provision a GKE Cluster

This repo is a companion repo to the [Provision a GKE Cluster tutorial](https://developer.hashicorp.com/terraform/tutorials/kubernetes/gke), containing Terraform configuration files to provision an GKE cluster on GCP.

This repo also creates a VPC and subnet for the GKE cluster. This is not
required but highly recommended to keep your GKE cluster isolated.

## GCP Infrastructure:

- Pull Terraform code

    ```
    cd gcp && bash pull.sh
    ```

- Add project/region to terraform.tfvars

- Provision resources

    ```
    cd learn-terraform-provision-gke-cluster && terraform init && terraform apply
    ```
    Don't forget to Type yes!

- [Add Kubectl Plug-in](https://cloud.google.com/blog/products/containers-kubernetes/kubectl-auth-changes-in-gke)

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
    kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v<< ADD VERSION NUMBER HERE (i.e 3.4.3)>>/install.yaml
    ```

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
## Adding Images to Artifact Registry

- Create Docker Repo in GCP
    ```
    gcloud artifacts repositories create DOCKER_REPO_NAME --repository-format=docker \
--location=us-central1 --description="Docker repository"
    ```

- Build and tag image
    ```
    docker build . -t us-central1-docker.pkg.dev/PROJECT/DOCKER_REPO_NAME/IMAGE_NAME:VERSION
    ```
- Push image to GCP
    ```
    docker push us-central1-docker.pkg.dev/PROJECT/DOCKER_REPO_NAME/IMAGE_NAME:VERSION
    ```

## Clean-up

- Destroy resources
    ```
    terraform destroy
    ```

## gcloud CLI

- Create K8s cluster

    ```
    gcloud beta container --project "$PROJECT_ID" clusters create "cluster-1" --zone "us-central1-c" --no-enable-basic-auth --cluster-version "1.23.12-gke.100" --release-channel "regular" --machine-type "e2-medium" --image-type "COS_CONTAINERD" --disk-type "pd-standard" --disk-size "100" --metadata disable-legacy-endpoints=true --scopes "https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" --max-pods-per-node "110" --num-nodes "3" --logging=SYSTEM,WORKLOAD --monitoring=SYSTEM --enable-ip-alias --network "projects/$PROJECT_ID/global/networks/default" --subnetwork "projects/$PROJECT_ID/regions/us-central1/subnetworks/default" --no-enable-intra-node-visibility --default-max-pods-per-node "110" --no-enable-master-authorized-networks --addons HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver --enable-autoupgrade --enable-autorepair --max-surge-upgrade 1 --max-unavailable-upgrade 0 --enable-shielded-nodes --node-locations "us-central1-c"
    ```