# Usage
## Crawler
Example command:
>./crawler.py -p 1000 -l 1000 -i seed.txt -o data.json -n 5

Arguments:

    Optional Arguments:
    -h    show help
    -n    number of threads

    Required Arguments:
    -i    input seed file
    -l    number of levels
    -o    output directory
    -p    number of pages

## Indexer
Fill out elasticsearch.txt with the following:
>username:password\
>deploymenturl

Run the following command from the same folder as data.json and elasticsearch.txt
>./indexer.sh

## Webpage
* Place index.php, elasticsearch.txt, interface.js, and interface.css in /var/www/html
* Input your query into the textbox
* press enter ONCE
* be patient (queries may take up to 30 seconds)
