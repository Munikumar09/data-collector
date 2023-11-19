## Installation
```
$ git clone https://github.com/Munikumar09/data-collector.git
$ conda create --name yt python=3.9
$ cd data-collector
$ poetry install
```

## Usage

```
python main.py --search_queries <text file path that contains search topics or search query topic> --is_file --device <cpu or cuda> --max_pages <number of pages to fetch data> --language hindi
```
search query should be just topic name like `education`, `news`, `cricket`, etc.