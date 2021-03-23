#!/bin/bash

HOME="$(pwd)/.."

path="$HOME/scripts"
PYTHON="python"

$PYTHON $path/goldminer_constituents_spiders > $HOME/log/constituents.log 2>&1
$PYTHON $path/goldminer_spiders > $HOME/log/spiders.log 2>&1
$PYTHON $path/goldminer_indicator_builder > $HOME/log/evaluations.log 2>&1
$PYTHON $path/goldminer_funds > $HOME/log/funds.log 2>&1
