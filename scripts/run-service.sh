#!/bin/bash

/usr/local/anaconda3/bin/python /home/abing/goldminer/SpidersConstituents.py > /home/abing/goldminer/log/constituents.log 2>&1
/usr/local/anaconda3/bin/python /home/abing/goldminer/Spiders.py > /home/abing/goldminer/log/spiders.log 2>&1
/usr/local/anaconda3/bin/python /home/abing/goldminer/Evaluations.py > /home/abing/goldminer/log/evaluations.log 2>&1
/usr/local/anaconda3/bin/python /home/abing/goldminer/Funds.py > /home/abing/goldminer/log/funds.log 2>&1
