#!/bin/bash
# Very simple script to run through a bunch of images
# Renames them with a same prefix while keeping their suffix (part of name after last underscore)
for file in *.png
do
	STR=`echo $file | sed 's/.*\_//'` # get part of filename after last underscore
	mv $file "prefix"$STR # rename
done
