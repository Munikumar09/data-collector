## Installation
```
$ git clone https://github.com/Munikumar09/data-collector.git
$ conda create --name yt python=3.10
$ cd data-collector
$ poetry install
```

## Usage

Edit the `download_config.yaml` file based on your requirement.
Either create a text file with search queries or provide a single or list of search queries.
search query should be just topic name like `education`, `news`, `cricket`, etc.
run `python main.py`