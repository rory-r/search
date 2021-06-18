#!/bin/sh
file=`cat ./elasticsearch.txt`
pos=`expr index "$file" $'\n'`
userpwd=${file:0:$pos}
deployment=${file:$pos}
curl -X PUT -u $userpwd $deployment"?pretty" -H 'Content-Type: application/json' -d '{
  "settings": {
    "analysis": {
      "analyzer": {
        "htmlStripAnalyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase"],
          "char_filter": [ "html_strip" ]
        }
      }
    }
  },"mappings": {
      "properties": {
        "html": {
          "type": "text",
          "analyzer": "htmlStripAnalyzer"
        }
      }
  }
}'
curl -X POST -u $userpwd $deployment"/_bulk" -H "Content-Type: application/x-ndjson" --data-binary @data.json