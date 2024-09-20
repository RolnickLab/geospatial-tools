#!/usr/bin/env bash
#SBATCH --job-name=search_s2_products
#SBATCH --time=01:30:00
#SBATCH --mem=32Gb
#SBATCH --cpus-per-task=4

module load miniconda/3
conda activate geospatial-tools

source config.sh

DEFAULT_ARGS=("${@:1}")

python3 "${PROJECT_DIR}"/scripts/sentinel_2_search_and_process/product_search.py "${DEFAULT_ARGS[@]}"