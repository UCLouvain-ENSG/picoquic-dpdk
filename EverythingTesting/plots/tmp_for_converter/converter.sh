#!/bin/bash
for pdfile in *.pdf ; do
  convert -verbose -density 500 -resize '800' "${pdfile}" "${pdfile%.*}".png
done

