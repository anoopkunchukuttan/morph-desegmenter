#!/bin/bash 

# parameters 
ref_doc="$1"
test_doc="$2"
output_dir="$3"
language="$4"

# read system configuration 
. /usr/local/bin/smt/moses_job_scripts/moses_env.conf

mkdir $output_dir

##### compute METEOR
cd $METEOR_HOME
java -Xmx512m -jar meteor-*.jar "$test_doc" $ref_doc -l $language > $output_dir/meteor.txt
#meteor_score=`tail -1 $output_dir/meteor.txt | cut -f 2 -d ':' | tr -d  [:space:]`

