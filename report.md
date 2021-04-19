---
template: eisvogel.tex
papersize: a4
title: Beyond functional autograding of ARM assembly language programs
subtitle: |
  Final Year Project (CSU44099)
author:
  - |
    [Jack O'Sullivan](osullj19@tcd.ie) (#17331147)
title-extra: |
  ```{=latex}
  \textsf{Supervisor: Dr. Jonathan Dukes}
  ```
titlepage: true
csl: harvard.csl
bibliography: references.bib
link-citations: true
---

# Introduction

## Motivation

Automated grading of programming assignments is a desirable option to have,
allowing instructors and teaching assistants to save a significant amount of
time. Since programming assignments are often based
upon the implementation of a solution to a single fairly specific problem, they
seem like a fairly obvious candidate for automation.

The focus when performing automated
grading is almost always on functional or "black box" testing. In
this model, a student's code is given a set of inputs, and the produced outputs
are tested against a corresponding pre-determined set of correct ones [@online_judge].
This is usually as simple as passing a list of items as command line arguments
or strings on standard input and parsing the results from standard output.
Often, an additional set of "hidden test cases" (inputs which the student can
never obtain direct access to) is used to prevent hardcoding of answers [@online_judge].

Aside from checking for hardcoded outputs, the quality of a submission is
rarely tested. While this is less important for
some types of assignments (perhaps implementation of an algorithm in a high-level
language), marks for topics like high-performance assembly programming are
often given for specific instructions and optimisations used.

In order to more appropriately grade assignments in such topics, more
in-depth analysis is required. Usually this comes in the form of a manual marking
step. Here (in the case of an assembly language assignment), a grader might
review a student's submission and identify
specific issues, such as the use of extraneous CPU instructions or poor overall
program structure.

The mechanism through which this analysis might be automated is much less
obvious, but any reduction in the requirement for manual grading would be very
beneficial.

In addition to the benefits for instructors, students can also take advantage of
an automated grading system. With manual grading, there is a significant delay
between submission and receiving feedback for an assignment. Since
an automated system can perform its grading in a matter of minutes or seconds,
students can learn more efficiently. They might be able to improve a single
assignment before final submission or simply be prepared for future assignments
more quickly.

\newpage

## Goals

This project seeks to develop an automated grading system which focuses
specifically on measuring performance (at runtime) of ARM assembly language
programs. As previously mentioned, there are a number of potential aspects for
improving automation around programming assignment grading. By choosing a
specific type of assignment and domain for improvement, a more in-depth system
can be realised.

Since the type of assignments being analysed will be relatively short,
hand-written ARM assembly language programs, it makes sense to look at
performance. This is primarily due to the fact that assembly language programs
are usually written with high-performance in mind. Additionally, other aspects
of a program's
grading (aside from correctness) such as maintainability are somewhat more
difficult to anaylse, given that assembly programs have very little structure.
Dynamic or runtime performance analysis is also used over static analysis for
the same reason.

The final product will be designed to facilitate grading assignments in the
modules "Introduction to Computing" (parts I and II), taught to first year
computer science students. This will include testing against specific
assignments given in the modules. The system will also need to integrate with
Submitty, the online grading platform already used in the module.

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
