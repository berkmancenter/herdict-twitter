#!/bin/bash
#
# Downloads the latest report log from Herdict and counts how frequently
# each domain occurs.

curl http://www.herdict.org/reports.csv.gz | gunzip |
  cut --delimiter=',' --field=4 |
  tr --delete '"' |
  awk --field-separator '/' '{ sub(/www\./, "", $1); print $1 }' |
  sort | uniq --ignore-case --count |
  sort --reverse --numeric-sort > ../../Data/Site_Block_Frequencies.txt

