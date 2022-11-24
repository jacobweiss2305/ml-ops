# Experiment tracking

This project uses MLflow to keep track of experiments.

## Overview

The deployment uses managed *Cloud SQL* database, *Cloud Storage* bucket for artifact storage,
*Secret Manager* for obtaining secrets at run time, *Container Registry* for docker
image storage and *Cloud Run* for managed, serverless runtime environment.

## 7-Steps to deployment:

1. Install gcloud cli and docker

2. Create a service account with Owner access
    - Secrets Manager > Create Service Account > Supply name > Owner Access Levels
    - After service account is made download the Key-pair as .json
    - Store it here:
        - `/ml-ops/gcp/src/experiments/mlflow-for-gcp/secrets`
    - Optional but recommended
        - `gcloud auth activate-service-account –key-file=<your_credentials_file_path>`

3. Create a *PostgreSQL* managed *Cloud SQL* instance.

    - Create SQL Instance > Choose PostgreSQL > Provide Instance Name and Password > Make sure Public IP is open to the internet (users will still need to auth in) > Finalize and create Instance

    - Setup SSL and enforce it.
        -  Go to SQL instance details -> Connections -> Click ‘Allow only SSL connections’
        - Go to SQL instance details -> Users -> Add User Account
        - Set PostgreSQL authentication, username, and password
        - Click ‘ADD’

    - Download and store certificates
        - Go to SQL instance details -> Connections -> Click ‘CREATE A CLIENT CERTIFICATE’ and download the files client-cert.pem, client-key.pem and server-ca.pem

        - Store it here:
            - `/ml-ops/gcp/src/experiments/mlflow-for-gcp/secrets`

    - Enable *Cloud SQL Admin API* and create a new database with a new user (you don't want `mlflow` to have ownership of your whole database).
    Alternatively you can execute the following SQL statements in the database:
    ```sql
    create database mlflow;
    create user mlflow with encrypted password 'some-password';
    grant all privileges on database mlflow to mlflow;
    ```
4. Create a storage bucket
    - Choose ‘Storage’ from the left-hand GCP panel
    - Click ‘Create Bucket’
    - Set name and preferred location; you can leave the rest of the parameters as ‘Default’ (if you need to adjust their settings, there are thorough guidelines to help you do that)

5. Secret Manager
    - On the left GCP panel, click ‘Security’ -> Select ‘Secret Manager’
    - Enable Secret Manager
    - Create Secret:
        - mlflow_artifact_url: this is the address of the Storage Bucket where you’ll store MLflow artifacts
            - When creating Secret Manager, you have to set the Secret Value
            - If you set the secret name as mlflow, then the default secret value should be gs://mlflow
            - Note: you can also check this in Storage -> Bucket details -> Configuration (link for gsutil)
        - mlflow_database_url: SQLAlchemy-format Cloud SQL connection string (over internal GCP interfaces, not through IP), sample value `postgresql+pg8000://<dbuser>:<dbpass>@/<dbname>?unix_sock=/cloudsql/<project-id>:<location>:<cloud-instance-name>/.s.PGSQL.5432`
            - The Cloud SQLinstance name can be copied from Cloud SQL instance overview page
        - mlflow_tracking_username: the basic HTTP auth username for MLflow (your choice)
        - mlflow_tracking_password: your choice

6. Container registery
    - `export GCP_PROJECT=project_id`
    - `cd src/experiments/mlfow-for-gcp`
    - `make docker-auth`
    - `make build && make tag && make push`

7. Cloud run
    - Create a new ‘Cloud Run’ deployment using the image you just pushed to the Container Registry. Click Create Service.
    - Deploy one revision from an existing image (Enter image path from GCR)
    - Under Container, Connections, Security:
        - Select “Allow unauthenticated invocations” to enable incoming web traffic (MLflow will be protected by HTTP basic auth at a later step)
        - Give the machine 1GB of RAM (use the service account you created earlier; you can decrease the maximum number of instances)
        - Add Environment Variable (Under Container section)
            - GCP_PROJECT = <project_id>
        - Add SQL connection (Under Connections section)
        - Add service account (Under security section)

## Set up Jupyterlab:
- Make sure `kubectl` and `helm` are installed.
- 

## How to track experiments:

- Configure the following environment variables:

    * `MLFLOW_TRACKING_URI=https://<your cloud run deployment URL.a.run.app>`
    * `MLFLOW_TRACKING_USERNAME=<mlflow access username>`
    * `MLFLOW_TRACKING_PASSWORD=<mlflow access password>`
    * `MLFLOW_EXPERIMENT_NAME=my_little_pony` - the name of your experiment (needs to be created beforehand - through web UI or `mlflow` CLI).
    * `GOOGLE_APPLICATION_CREDENTIALS=/home/<user>/<absolute path>/credentials.json` - the path to the service account credentials JSON file.

- Add mlflow logging to your notebook or use their auto_log feature.

- Execute your experiment (*.ipynb or *.py)

## Additional resources:

- [Guide to deploying MLflow on GCP](https://console.cloud.google.com/run/create?project=data-science-362714)
- [Zero to JupyterHub with K8s](https://z2jh.jupyter.org/en/stable/index.html)
