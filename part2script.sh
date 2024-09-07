#!/bin/bash

path1_tr="../../start_texts/start_transcription.txt"
path2_tr="../../final_texts/final_transcription.txt"

path1_sc="../../start_texts/start_scenario.txt"
path2_sc="../../final_texts/final_scenario.txt"


python3 TR_converters/upgrade_transcription/main.py "$path1_tr" "$path2_tr"

python3 TR_converters/upgrade_scenario/main.py "$path1_sc" "$path2_sc"
