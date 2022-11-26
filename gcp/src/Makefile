# Makefile
SHELL = /bin/bash

#Help
.PHONY: help
help:
	@echo "Commands:"
	@echo "push-version version=1.X                  : push images to GCP."
	@echo "mlflow-init                               : initializes mlflow repo."
	@echo "jup-kill ns=namespace                     : kill jupyterhub container (requires ns=namespace)."
	@echo "jup-start ns=namespace version=1.X        : spin up jupyterhub (requires version=version_number)."
	@echo "jup-rebuild ns=namespace version=1.X      : kill and rebuild (requires ns=namespace version=version_number)."

# AWS
.PHONY:
push-version:
	docker build preprocess/. -t us-central1-docker.pkg.dev/data-science-362714/data-science/phone-accuracy-preprocess:$(version) && \
	docker build train/. -t us-central1-docker.pkg.dev/data-science-362714/data-science/phone-accuracy-train:$(version) && \
	docker build serve/. -t us-central1-docker.pkg.dev/data-science-362714/data-science/phone-accuracy-serve:$(version) && \
	docker build monitor/. -t us-central1-docker.pkg.dev/data-science-362714/data-science/phone-accuracy-monitor:$(version) && \
	docker push us-central1-docker.pkg.dev/data-science-362714/data-science/phone-accuracy-preprocess:$(version) && \
	docker push us-central1-docker.pkg.dev/data-science-362714/data-science/phone-accuracy-train:$(version) && \
	docker push us-central1-docker.pkg.dev/data-science-362714/data-science/phone-accuracy-serve:$(version) && \
	docker push us-central1-docker.pkg.dev/data-science-362714/data-science/phone-accuracy-monitor:$(version)

.PHONY:
mlflow-init:
	cd experiments && git clone https://github.com/dlabsai/mlflow-for-gcp.git

.PHONY:
kill-ns:
	kubectl delete namespace $(ns)

.PHONY:
start-jlab:
	kubectl create namespace jlab --dry-run=client -o yaml | kubectl apply -f - && \
	kubectl apply -f experiments/jupyter/deployment.yaml && \
	sleep 5 && \
	kubectl get pods -n jlab

.PHONY:
open-jlab:
	kubectl port-forward $(pod-name) 8888:8888 -n jlab

.PHONY:
exit-jlab:
	kubectl delete namespaces jlab