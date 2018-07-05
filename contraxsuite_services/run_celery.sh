#!/bin/bash

pushd ../../
source ve/bin/activate
popd

celery multi restart worker -A apps -B -Q serial --concurrency=1 -Ofair -l DEBUG -n beat@%h

celery multi restart worker1 -A apps -Q default,high_priority --concurrency=1 -Ofair -n default_priority@%h


