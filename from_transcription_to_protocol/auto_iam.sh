#!/bin/bash

#this script generates new IAM Token
rm IAM_TOKEN.txt
yc iam create-token >> IAM_TOKEN.txt
