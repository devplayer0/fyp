#!/bin/sh
set -e

pandoc --number-sections report.md -o report.pdf
