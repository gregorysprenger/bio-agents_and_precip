#!/bin/bash

sleep 10

###########################
## Create data directory ##
###########################
echo -e "Creating directories" >> flow.log

mkdir -p raw_data \
  clean_data

sleep 10

echo -e "Running esearch and efetch" >> flow.log

start=`date +%s`

# Use parallel to fetch 3 at a time
parallel -a agents_list.txt -j3 'echo {}; timeout 2h \
  esearch -db biosample -query {} | \
  efetch -format runinfo > raw_data/{}.tsv' 1> esearch.log

# Replace spaces with underscores
for i in raw_data/*' '*; do
  mv "$i" `echo $i | sed -e 's/ /_/g'`
done

end=`date +%s`
runtime=$((${end} - ${start}))
echo -e "Time to fetch biosamples: ${runtime}" >> flow.log

sleep 10