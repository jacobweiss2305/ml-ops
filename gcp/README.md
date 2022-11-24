# GCP Workloads

The ethos of this project is to run distrubted ML on cloud native technologies. 

This folder focuses on deploying in GCP.

Experiment Workflow:
1. Data scientist creates experiments in notebooks.
    - `src/experiments/notebooks`
2. Data scientist uses MLflow to pick the best model
    - See `src/experiments/README.md`
3. Move to production

Production Workflow:
1. Data scientist and ML Engineer code review (translate .ipynb to .py)
    - Replace Pandas with Modin
    - Trim packaging
2. ML engineer packages code into containers.
3. ML engineer builds and pushs containers to Artifact Registry
    ```
    make version=1.0 push-version
    ```
4. ML engineer submits a workload and scheduler to GKE
    ```
    argo submit -n argo workflow.yaml
    ```

- Note: Steps 3 and 4 will be automated using Gitub actions and Cloud Trigger

## Setting up Experiment Workflow
- See `src/experiments/README.md`

## Setting up Production Workflow

### 1. Create K8s cluster

#### Using Gcloud CLI (preferred)
    ```
    gcloud beta container --project "$PROJECT_ID" clusters create "cluster-1" --zone "us-central1-c" --no-enable-basic-auth --cluster-version "1.23.12-gke.100" --release-channel "regular" --machine-type "e2-medium" --image-type "COS_CONTAINERD" --disk-type "pd-standard" --disk-size "100" --metadata disable-legacy-endpoints=true --scopes "https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" --max-pods-per-node "110" --num-nodes "3" --logging=SYSTEM,WORKLOAD --monitoring=SYSTEM --enable-ip-alias --network "projects/$PROJECT_ID/global/networks/default" --subnetwork "projects/$PROJECT_ID/regions/us-central1/subnetworks/default" --no-enable-intra-node-visibility --default-max-pods-per-node "110" --no-enable-master-authorized-networks --addons HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver --enable-autoupgrade --enable-autorepair --max-surge-upgrade 1 --max-unavailable-upgrade 0 --enable-shielded-nodes --node-locations "us-central1-c"
    ```

#### Using Terraform:

    ```
    cd gcp && git clone git@github.com:hashicorp/learn-terraform-provision-gke-cluster.git
    ```

- Add project/region to learn-terraform-provision-gke-cluster/terraform.tfvars

- Provision resources

    ```
    cd learn-terraform-provision-gke-cluster && terraform init && terraform apply
    ```
    Don't forget to Type yes!

### 2. GKE Setup

- [Kubectl Installation Local](https://kubernetes.io/docs/reference/kubectl/)

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

- Authenticate

    ```
    kubectl apply -f https://raw.githubusercontent.com/hashicorp/learn-terraform-provision-gke-cluster/main/kubernetes-dashboard-admin.rbac.yaml
    ```
- You can only use the token to access the Control Plane Server. Copy/Paste the Token in the UI.

    ```
    kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep service-controller-token | awk '{print $1}')
    ```

### 4. Setup Argo

Argo is used for scheduling our container workflows either as a one time job or on a reoccuring time period (cron scheduler).

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
### 5. Add images to Artifact Registry

In order to submit a workload using our custom images, we need to push our local container builds to Artifact Registry.

- Create Docker Repo in Artifact Registry (make sure API is enabled)
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

- These commands are automated in Makefile

    ```
    make version=1.0 push-version
    ```