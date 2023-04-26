#!/bin/bash

# Set input variable
API_KEY=$1

sleep 10

###########################
## Create data directory ##
###########################
echo -e "Creating directories" >> flow.log

mkdir -p raw_data \
  clean_data

sleep 10

################
## Fetch Data ##
################

echo -e "Running esearch and efetch" >> flow.log

start=`date +%s`

if [[ "${API_KEY}" == "NULL" ]]; then
  # Use parallel to fetch 3 at a time
  parallel -a agents_list.txt -j3 "echo {}; timeout 1h \
    bash -c 'esearch -db biosample -query {} | \
    efetch -format runinfo > raw_data/{}.tsv'" \
    1> esearch.out 2> esearch.err
else
  # Set API KEY as env var
  # How to get one: https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
  export NCBI_API_KEY="${API_KEY}"

  # Use parallel to fetch 8 at a time
  parallel -a agents_list.txt -j8 "echo {}; timeout 1h \
    bash -c 'esearch -db biosample -query {} | \
    efetch -format runinfo > raw_data/{}.tsv'" \
    1> esearch.out 2> esearch.err
fi

# Replace spaces with underscores
for i in raw_data/*' '*; do
  mv "$i" `echo $i | sed -e 's/ /_/g'`
done

end=`date +%s`
runtime=$((${end} - ${start}))
echo -e "Time to fetch biosamples: ${runtime}" >> flow.log

sleep 10