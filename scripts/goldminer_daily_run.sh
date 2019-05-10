#!/bin/bash

path="/home/abing/goldminer/scripts"
PYTHON="/usr/local/anaconda3/bin/python"

$PYTHON $path/goldminer_constituents_spiders > /home/abing/goldminer/log/constituents.log 2>&1
$PYTHON $path/goldminer_spiders > /home/abing/goldminer/log/spiders.log 2>&1
$PYTHON $path/goldminer_indicator_builder > /home/abing/goldminer/log/evaluations.log 2>&1
$PYTHON $path/goldminer_funds > /home/abing/goldminer/log/funds.log 2>&1
