# MLOps Infrastructure: Containerization & Orchestration

This document describes the MLOps components implemented for the **FAERS Drug Adverse Event Prediction** project. The objective is to improve reproducibility, portability, and deployment readiness through containerization and orchestration technologies.

---

## Overview

The machine learning pipeline was packaged and prepared for deployment using:

* Docker for containerization

* Kubernetes (Minikube) for orchestration

* GitHub Actions for Continuous Integration (CI)

These components ensure that the project can be executed consistently across different environments.

---

## 1\. Docker Containerization

The complete workflow, including data preprocessing, graph construction, feature engineering, model training, and evaluation, is containerized using Docker.

Containerization provides:

* Reproducible execution environments

* Dependency isolation

* Simplified deployment

* Platform-independent execution

### Dockerfile

**FROM** python:3.12-slim

**WORKDIR** /app

**COPY** requirements.txt .

**RUN** pip install \--no-cache-dir \-r requirements.txt

**COPY** . .

**CMD** \["python", "pipeline.py"\]

### Build Docker Image

docker build \-t drug-ae-pipeline .

### Run Container

docker run \--name drug-pipeline-container drug-ae-pipeline

---

## 2\. Kubernetes Orchestration

To demonstrate orchestration capabilities, the Docker container was deployed to a local Kubernetes cluster using Minikube.

Since the training workflow is a finite batch-processing task, a Kubernetes Job resource was used rather than a Deployment.

### Kubernetes Job Manifest

File: k8s-job.yaml

apiVersion**:** batch/v1  
kind**:** Job  
metadata**:**  
  name**:** drug-pipeline-job

spec**:**  
  template**:**  
    spec**:**  
      containers**:**  
      **\-** name**:** drug-pipeline-container  
        image**:** drug-ae-pipeline  
        imagePullPolicy**:** Never

      restartPolicy**:** Never

  backoffLimit**:** 0

### Start Minikube

minikube start

### Configure Docker Environment

eval $(minikube docker-env)

### Deploy Job

kubectl apply \-f k8s-job.yaml

### Verify Execution

kubectl get jobs  
kubectl get pods

Expected output:

NAME                COMPLETIONS   DURATION   AGE  
drug-pipeline-job   1/1           XXs        XXm

A completed job indicates that the pipeline executed successfully and terminated normally.

---

## 3\. Continuous Integration

Continuous Integration is implemented using GitHub Actions.

The CI workflow automatically:

* Creates a Python environment

* Installs project dependencies

* Verifies package installation

* Ensures the repository remains buildable

Workflow file:

.github/workflows/ci.yml

This allows automated validation whenever code is pushed to the repository.

---

## 4\. Project Architecture

FAERS Data  
     │  
     ▼  
Data Preprocessing  
     │  
     ▼  
Feature Engineering  
     │  
     ▼  
Drug Interaction Network  
     │  
     ▼  
Graph Risk Scoring  
     │  
     ▼  
Random Forest Model  
     │  
     ▼  
Evaluation & Reports  
     │  
     ▼  
Docker Container  
     │  
     ▼  
Kubernetes Job

---

## 5\. Screenshots & Verification

### Kubernetes Execution

The screenshot below demonstrates successful execution of the training pipeline within the Kubernetes cluster.

reports/figures/k8s\_dashboard.png

A status of **Completed** confirms that the training workflow finished successfully.

### Docker Environment

The project was also verified inside a Docker container, ensuring compatibility of all major dependencies including:

* Scikit-Learn

* NetworkX

* SQLAlchemy

* Pandas

* NumPy

---

## Reproducibility

The combination of Docker, Kubernetes, and GitHub Actions provides:

* Reproducible model training

* Environment consistency

* Automated validation

* Deployment readiness

These practices follow common MLOps standards used in production machine learning systems.