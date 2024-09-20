# Scripts

----
**Important note for SLURM scripts**

All Slurm scripts need to be run from the [scripts/](.) folder, as they use the 
[config.sh](config.sh.example) that also needs to be configured by each user.
----

This folder is dedicated to scripts, whether python, bash or sbatch.

Generally, scripts are more for standalone processes while figuring them out.

Once a script is more mature, it should be generalized and integrated into the package
itself.

## Scripts

* [resample_tiff_raster.py](resample_tiff_raster.py) : Script to resample a target tiff image, so it matches a source image's grid size and area. Resampling strategy is using a Nearest Neighbor algorythm to keep original values. Use the scripts CLI for more information : `python3 resample_tiff_raster.py --help` 
