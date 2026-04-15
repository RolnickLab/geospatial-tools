---
name: infrastructure
description: Infrastructure Skill Instructions
---
# Infrastructure Skill Instructions

## Primary Directive
Your objective is to ensure that all research environments, compute jobs, and pipelines are reproducible, resilient, and explicitly defined as code.
**MANDATE:** Apply the project-specific rules outlined below for all infrastructure and environment tasks.

## Context
This project uses modern Python packaging and infrastructure-as-code principles.

## Standards
You MUST enforce the following project-specific infrastructure standards:

### 1. Environment Management

- **Explicit Definition:** Environments are defined centrally in `pyproject.toml` and locked using `uv` (`uv.lock`). ALWAYS use `uv` for dependency management tasks rather than raw `pip` or `conda` where possible.
- **Isolation:** ALWAYS run tasks within the appropriate `nox` session or `uv` virtual environment.

### 2. Infrastructure as Code (IaC)

- **Provisioning:** Prefer `Terraform` or `Pulumi` for defining cloud resources and infrastructure over manual provisioning or ad-hoc bash scripts.
- **Idempotency:** Setup, deployment, and data pipelines MUST be safe to run multiple times without causing errors or duplicate data.

### 3. Containerization (Docker)

- **Multi-Stage Builds:** When writing Dockerfiles, use multi-stage builds to keep final image sizes small and secure.
- **Least Privilege:** Containers MUST NOT run as the root user. Pinned, non-root base images are mandatory.

### 4. HPC & Automation

- **Explicit Resources:** If interacting with SLURM or cluster job scripts, ALWAYS request specific resources (`cpus-per-task`, memory, etc.).
    

## Forbidden Patterns

- ❌ **"ClickOps":** You MUST NOT recommend setting up environments or servers manually via a GUI.
- ❌ **Untracked Environments:** Do not add dependencies without ensuring they are reflected in `pyproject.toml` and `uv.lock`.
- ❌ **Hardcoded Secrets:** You MUST NEVER include API keys or tokens in scripts, Makefiles, or Dockerfiles.
    
