# HH Job Parser

HH Job Parser is a Python script that parse resumes by search request links

## Dependencies
- requests
- beautifulsoup4

## Usage
To get resumes urls use `job_parser.py`. Just fill `jobs` list at the begining of the file. The result is a `.txt` file
in `resume_lists` dir, named `JobName_urls.txt`

To parse this urls use `parse_urls.py` with following params:
- -i path_to_urls_file
- -o output dir for parsed resumes
- -j job name
The result is banch of `.json` files in `output_dir/job_name/` dir

Example

`$ python parse_urls.py -i ./resume_lists/Бортпроводник_urls.txt -o ./res -j Бортпроводник`


### Have fun