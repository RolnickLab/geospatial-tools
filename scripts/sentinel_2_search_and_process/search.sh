#!/usr/bin/env bash
#SBATCH --job-name=search_s2_products
#SBATCH --time=01:00:00
#SBATCH --mem=32Gb
#SBATCH --cpus-per-task=4

#module load miniconda/3
#conda activate geospatial-tools

CURRENT_DIR="$(dirname "$0")"
cd "${CURRENT_DIR}" || exit
source ../config.sh

python3 "${PROJECT_DIR}"/scripts/sentinel_2_search_and_process/product_search.py --help