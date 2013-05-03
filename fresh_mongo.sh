#!/bin/bash

rm -rf ./mongo.db
mkdir ./mongo.db
mongod --dbpath=./mongo.db --rest
