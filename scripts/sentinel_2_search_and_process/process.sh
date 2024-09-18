#!/usr/bin/env bash
#SBATCH --job-name=process_s2_products
#SBATCH --time=02:00:00
#SBATCH --mem=32Gb
#SBATCH --cpus-per-task=4

module load miniconda/3
conda activate geospatial-tools

source config.sh

if [ "$1" == "" ]; then
  DEFAULT_ARGS=("--help")
else
  DEFAULT_ARGS=("${@:1}")
fi

python3 "${PROJECT_DIR}"/scripts/sentinel_2_search_and_process/download_and_process.py "${DEFAULT_ARGS[@]}"