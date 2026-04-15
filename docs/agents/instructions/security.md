---
name: security
description: Security Skill Instructions
---
# Security Skill Instructions

## Primary Directive
Your primary objective is to identify vulnerabilities, enforce defense-in-depth, and ensure absolute data privacy.
**MANDATE:** Apply the project-specific rules outlined below for all tasks involving security, authentication, or data privacy.

## Context
Geospatial research often involves massive downloads from third-party catalogs (STAC, Copernicus) requiring authentication tokens. Exposing these tokens compromises the lab's infrastructure limits.

## Standards
You MUST actively enforce the following project-specific security standards:

### 1. Secret Management

- **Token Protection:** Copernicus, Planetary Computer, and AWS tokens MUST NEVER be hardcoded. They must be loaded via `.env` files, environment variables, or centralized configuration (`configs/geospatial_tools_ini.yaml`).
- **File Exclusions:** Ensure `configs/geospatial_tools_ini.yaml` and `.env` remain in `.gitignore`. Only commit `.example` versions.

### 2. Data Safety

- **Path Traversal:** When dynamically generating file paths based on STAC item IDs or user input, use `pathlib.Path.resolve()` to ensure paths do not traverse outside the intended output directory (`../`).
- **Deserialization:** Do not use `pickle` or `numpy.load(allow_pickle=True)` for data acquired from external STAC catalogs.
    

## Forbidden Patterns

- ❌ **Committing Secrets:** You MUST NEVER allow code containing hardcoded credentials or API tokens to be committed.
- ❌ **Disabling SSL Verification:** You MUST NEVER permit `verify=False` in `requests` or `aiohttp` calls to STAC catalogs or data endpoints.
- ❌ **Raw SQL:** Always use ORMs or parameterized queries to prevent SQL injection. You MUST NEVER construct raw SQL strings with user input.
    
