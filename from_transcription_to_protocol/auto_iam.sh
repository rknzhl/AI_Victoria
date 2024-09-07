#!/bin/bash

#this script generates new IAM Token
yc iam create-token >> IAM_TOKEN.txt
