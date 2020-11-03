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

- [On automated grading of programming assignments in an academic institution](https://doi.org/10.1016/S0360-1315(03)00030-7)
  \- automated grading in 1999 (1 year after opening of School of Computing!)
- [Automated feedback generation for introductory programming assignments](https://doi.org/10.1145/2491956.2462195) -
  providing feedback and correcting errors by analysing code, also providing a DSL to notate common errors
- [MAGIC: Massive Automated Grading in the Cloud](https://www.semanticscholar.org/paper/MAGIC%3A-Massive-Automated-Grading-in-the-Cloud-Fox-Patterson/4e6a1657b6b3c73c248f852d2fb068572afad1ec?p2df)
  \- autograding with unit tests
- [Teaching and Learning Programming and Software Engineering via Interactive Gaming](https://doi.org/10.1109/ICSE.2013.6606662)
  \- attempts to gamify programming; similar to autograding with tests
- [Interface-based Programming Assignments and Automatic Grading of Java Programs](https://doi.org/10.1145/1268784.1268805)
  \- more unit test-based grading (only mentions "non-functional" aspects)
- [Program Analysis Tools in Automated Grading](https://github.com/Submitty/publications/raw/master/2018_SIGCSE_poster_dinella_et_al/Poster.pdf)
  \- mostly static analysis, but mentions use of tools such as Valgrind to detect memory leaks
- [Submitty: An Open Source, Highly-Configurable Platform for Grading of Programming Assignments](https://github.com/Submitty/Tutorial/raw/master/presentation/Submitty%20Demo%20SIGCSE%20March%2010%202017.pdf)
  \- Submitty presentation
- [EmbedInsight: Automated Grading of Embedded Systems Assignments](https://arxiv.org/abs/1703.04514)
  \- use of real hardware (still black box)
- [Testing Strategies for the Automated Grading of Student Programs](https://doi.org/10.1145/2839509.2844616)
  \- analysis of various autograding strategies
