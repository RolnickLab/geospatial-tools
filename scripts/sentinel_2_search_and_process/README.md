# Sentinel 2 Search and Process Scripts

Scripts to run in order:

* [product_search.py](product_search.py) : Execute the search for products for a given region of interest
* [download_and_process.py](download_and_process.py) : Process the products found in previous scripts

Both scripts can be used with the `--help` option to have more information.

```bash
python product_search.py --help
```

```bash
python download_and_process.py --help
```

## Slurm scripts

The above scripts have their Slurm equivalent:

* [search.py](search.sh) : Execute the search for products for a given region of interest
* [process.py](process.sh) : Process the products found in previous scripts
