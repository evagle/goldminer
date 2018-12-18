#!/bin/bash

goldminer_constituents_spiders > /home/abing/goldminer/log/constituents.log 2>&1
goldminer_spiders > /home/abing/goldminer/log/spiders.log 2>&1
goldminer_indicator_builder > /home/abing/goldminer/log/evaluations.log 2>&1
goldminer_funds > /home/abing/goldminer/log/funds.log 2>&1
