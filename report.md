---
template: eisvogel.tex
papersize: a4
#geometry: margin=2cm
title: Beyond functional autograding of ARM assembly language programs
author:
  - |
    [Jack O'Sullivan](osullj19@tcd.ie) (#17331147)
title-extra: |
  ```{=latex}
  \textsf{Supervisor: Dr. Jonathan Dukes}
  ```
titlepage: true
---

# Abstract

Automated grading of programming assignments is a desirable option to have in
the face of growing class sizes. Considering the nature of the assignments,
marking seems like an obvious target for automation. Platforms like the
open-source Submitty have been developed to fulfill this idea.

However, the
focus when grading is almost always on functional or "black box" testing. In
this model, the student's code is given a set of inputs, and the produced
outputs are tested against a corresponding pre-determined set of correct ones.
This is usually as simple as passing a list of items as command line arguments
or strings on standard input and parsing the results from standard output.
Usually an additional set of "hidden test cases" (inputs which the student can
never obtain direct access to) is used to prevent hardcoding of answers.

Aside from preventing the use of hardcoded outputs (and possibly measuring how
long it took for a student's code to execute, usually to detect infinite loops),
the quality of a submission is never tested. While this is less important for
some types of assignments (implementation of some algorithm in a high-level
language), marks for topics like high-performance assembly programming are often
given for specific instructions and optimisations used.

In order to more appropriately grade assignments in such topics, more
in-depth analysis is required. This project seeks to explore the potential of
runtime performance measurement techniques in grading ARM assembly programs. In
particular, this includes extracting accurate information from running code such
as processor cycles used and presenting this to students.

Hardware such as the Cortex-M series of microcontrollers usually provide
dedicated debugging facilities which allow access to this information. While
accurate, use of such hardware is not as convenient as testing execution of code
in an emulator running on an off-the-shelf x86_64 machine. This project
therefore also seeks to explore the feasibility of obtaining accurate metrics
from an emulator, comparing this to similar data from dedicated hardware.

\newpage

# Introduction

\newpage

# Background

\newpage

# Design

\newpage

# Implementation

\newpage

# Evaluation

\newpage

# Conclusions

\newpage

# References
