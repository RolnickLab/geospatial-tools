#!/usr/bin/env bash
#SBATCH --job-name=search_s2_products
#SBATCH --time=01:00:00
#SBATCH --mem=32Gb
#SBATCH --cpus-per-task=4

module load miniconda/3
conda activate geospatial-tools

CURRENT_DIR="$(dirname "$0")"
cd "${CURRENT_DIR}" || exit 1
source ../config.sh

if [ "$1" == "" ]; then
  DEFAULT_ARGS=("--help")
else
  DEFAULT_ARGS=("${@:1}")
fi

python3 "${PROJECT_DIR}"/scripts/sentinel_2_search_and_process/product_search.py "${DEFAULT_ARGS[@]}"