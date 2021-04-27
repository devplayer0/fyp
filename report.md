---
template: eisvogel.tex
numbersections: true
papersize: a4

title: Beyond functional autograding of ARM assembly language programs
subtitle: |
  Final Year Project (CSU44099)
author:
  - |
    [Jack O'Sullivan (osullj19@tcd.ie)](osullj19@tcd.ie)
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
upon the implementation of a solution to a single relatively specific problem, they
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

In order to appropriately grade assignments in such topics, more
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
Submitty, the online grading platform already used in the module. It's worth
noting that the Introduction to Computing modules focus on writing programs to
run on an ARM-based microcontroller. At time of writing, this is specifically an
STMicroelectronics STM32F4xx-based board (featuring an ARM Cortex-M4 core).
This project will target the same platform.

\newpage

# Background

## Prior work

## Hardware

ARM processors are pervasive in mobile devices and increasingly so in
microcontrollers, displacing 8-bit products. Newer designs in the Cortex-M
series feature increasingly
complex cores with more features than the older ARM7 and ARM9.

STMicroelectronics produce a series of microcontrollers (and accompanying
low-cost development boards) making use of Cortex-M cores called "STM32". The
STM32F4xx series is based upon a Cortex-M4, which in turn is effectively a
Cortex-M3 with floating point and DSP (Digital Signal Processor)
instructions [@cortex_m4]. These cores
implement the ARMv7-M architecture, which use only the Thumb-1 and Thumb-2
instruction sets, and not the older ARM set used my processors like the ARM7
[@armv7m].

![STM32F4 Discovery board used in this project\label{fig:stm32f4_discovery}](img/stm32f4_discovery.jpg)

The STM32F4 Discovery board is the target board for Introduction to Computing
(and is therefore also the target for this project). Figure
\ref{fig:stm32f4_discovery} shows the board featuring an STM32F407VG
microcontroller and an integrated ST-LINK/V2 debugger [@stm32f4_discovery]. The
ST-LINK is a standard debugging component provided by ST that implements ARM's
Serial Wire Debug (SWD) protocol. This requires only 2 pins - SWDIO and SWCLK,
providing bidirectional communication and a clock signal respetively [@arm_swd].

The STM32F407VG provides a wide range of peripherals - the reference manual
describing them is over 1700 pages long [@stm32f407]. Use of peripherals is
relatively limited in Introduction to Computing, with only the standard ARM
SysTick timer and GPIO's (General Purpose I/O) being used.
The SysTick timer is a counter that decrements at a configurable real-time
interval and can generate interrupts [@armv7m].

## Emulators and simulators

Emulators and simulators are useful tools that can be used, in whole or part, to
replace a piece of real hardware.
In general, an *emulator*
attempts to achieve full functionality of a real system, usually maximising
performance by designing the system with the host in mind. A *simulator* aims
to accurately model the internals of a system and is generally less of a
replacement for real hardware. Some tools combine both, using accurate
simulation only for the most critical sections of evaluation [@marss].

A number of both emulators and simulators were considered for the "software" method
of evaluating programs for this project. It wasn't immeditately clear which
would best fulfill the needs of the project, as they each have benefits and
drawbacks.

### xPack QEMU

QEMU (the Quick EMUlator) describes itself as "a generic and open source
machine emulator and virtualizer" [@qemu]. It's purpose is generally to emulate
full systems, including peripherals such as hard drives and network interfaces.
Typically, hardware accelerated virtualisation technology is used to achieve
near-native performance (e.g. KVM on Linux). QEMU also offers the ability to
emulate software compiled for other CPU's with user-mode syscall translation.
It's very flexible, but is mostly focused on achieving maximum
performance, with the website's tagline as
"QEMU: the FAST! processor emulator" [@qemu].

The xPack project provides "tools to manage, configure and build complex,
package based, multi-target projects" [@xpack]. xPack's primary goal is to
provide a dependency management tool for embedded projects (primarily
toolchains, with a particular focus on ARM).

![xPack QEMU STM32F4 Discovery board emulation\label{fig:xpack_qemu_gui}](img/xpack_qemu_gui.jpg)

A subproject of xPack is their
fork of QEMU, referred to as "The xPack QEMU Arm". This fork of QEMU seeks to
address the lack of support for microcontroller cores in QEMU (which generally
emulates high-performance application cores only). Specifically, the fork aims
to support Cortex-M3 and M4 boards (including peripherals). The STM32F4 Discovery
development board (featuring an STM32F407 chip), used in Introduction to
Computing, is one of the supported boards. Emulation is quite
detailed, and a graphical representation of the board with LED's that react
to changing GPIO state is provided (see Figure \ref{fig:xpack_qemu_gui}).

Aside from better Cortex-M peripheral support, xPack QEMU doesn't really
provide any features over upstream QEMU (instrumentation, improved accuracy
etc). xPack's QEMU is currently used in Introduction to Computing (particularly
for its GUI mode, allowing for GPIO demonstrations without needing real
hardware).

### Unicorn

Unicorn describes itself as a "CPU emulator framework" [@unicorn]. Based on
QEMU, Unicorn seeks to provide a framework for emulating and instrumentating
code across many architectures. A key difference between Unicorn and xPack QEMU
(or even upstream QEMU) is its narrower focus: no peripherals are supported at
all. Unicorn only emulates raw machine code.

Being developed with security research in mind (and initially presented at Black
Hat!), Unicorn exposes an easy to use API allowing for powerful instrumentation.
This is a notable extension over QEMU, which provides no such access. The
emulated CPU can be programmatically hooked (with bindings in a multitude of
popular programming languages) to control execution and inspect
registers and memory on a per-instruction basis [@unicorn]. It's not possible
to record accurate timing information or break down execution to a level beyond
a single instruction however (an inherent limitation when using QEMU as a base).

![Unicorn is widely used in security research\label{fig:unicorn_showcase}](img/unicorn_showcase.png)

Since Unicorn has seen a lot of use in information security research (see figure
\ref{fig:unicorn_showcase}), it is relatively well documented and easy to use
(although there is little to no official documentation beyond examples given
in the original Black Hat talk).

### gem5

gem5 is vastly different to both xPack QEMU and Unicorn. With its primary goal
of "\[being\] a community tool focused on architectural modeling" [@gem5],
gem5's design and features are unrelated to those of QEMU and the forks
described previously. gem5's headline feature is really its flexibility and
modularity (it's the first goal listed in the project's original paper), which
originally comes from M5 (a previous simulator folded into gem5).

![Visualisation of a sample gem5 config (for an ARM Versatile Express platform)\label{fig:gem5_config_complex}](img/gem5_config_complex.jpg)

The simulator's flexibility primarily stems from its tight, object-oriented
integration with Python. All components in gem5 are `SimObject`s. These contain
two pieces: a C++ implementation and a Python binding. While the C++
part implements the behaviour of the component (e.g. a memory controller) for
high performance, the Python part defines the parameters for the component
[@gem5]. An overall Python-based configuration script instantiates all of the
`SimObject`s and wires them up. "Ports" are generally used to connect
communication between components such as memories. A visualisation of such a
configuration script (generated by gem5 itself) can be seen in figure
\ref{fig:gem5_config_complex}.

Using this modular design, it's possible to create a nearly endlessly
customisable system layout based on the requirements of a particular
application. gem5 can simulate a number of different CPU ISA's and memory
systems with various models. For CPU's, it's possible to simulate certain
segments of code in a simple "atomic" mode (for performance) and critical
segments using a complex pipelined and out-of-order execution model named "O3"
(for detailed analysis). Memory can also be modelled as simple SRAM-style
hardware with a fixed latency, or complex DRAM.

gem5 also supports two primary execution modes, similar to QEMU. In full system
mode ("FS"), gem5 emulates a full bare-metal system, with interrupts and
peripheral support (sophisticated enough to boot a full Linux kernel). Syscall
emulation mode ("SE") emulates syscalls for executing user-mode programs.

Adding and making use of new features (as `SimObject`s) is easy with gem5's
SCons-based build system and Python-based configuration scripts.

\newpage

# Design

There are a number of components required to produce a functioning automated
grading system for measuring performance of ARM assembly language programs.
Collectively, these are referred to as "**_Perfgrade_**". This section describes
the high-level design of the system.

## Considerations

Before a final overall system can be realised, there are a number of factors to
consider when designing _Perfgrade_.

### Metrics

Metrics are the types of raw data that can be collected in order to later
generate useful information. It's important to keep in mind the types of
metrics that can or need be collected - what metrics can be collected from a
particular system and which are required to generate specific results.

When measuring performance, the simplest metric to
consider is a measure of execution time. The most basic form of such a metric is
to run a timer or "stopwatch" while a program is running. A more precise and
reliable method will be required to measure time for the types of short assembly
programs graded by the system.

Aside from measuring execution time, this project will likely make use of another
somewhat broad "metric" in _tracing_. Tracing a program involves logging in
detail each execution of small blocks in a program, often as small as a single
instruction [@profiling_tracing]. This provides a lot of data that could
potentially be used to measure performance.

### Execution and measurement methods

There are two overall methods for executing programs and
recording some of the metrics described above
(within the context of this project): Hardware and software. **Hardware** refers
to the evaluation of a program on a real STM32F4xx-based microcontroller.
**Software** means evaluation of a program in some kind of emulator or simulator
that itself runs on a standard PC or server.

Which "method" is best for this project is not entirely clear, as both carry
their own advantages and disadvantages.

Software:

- is generally easy to set up and deploy, from a laptop to a server environment
- can usually be extended (e.g. to improve accuracy or measurement capabilities)
- may be lacking in accuracy (popular emulators don't often implement the
  concept of CPU cycles)
- can be slow (especially if high accuracy is required)

Hardware:

- is perfectly accurate
- requires additional physical components for deployment (less flexible)
- may require complex software infrastructure to manage
- isn't extensible
- may be difficult or impossible to measure metrics in detail

### Assignment configuration

Due to the nature of the assignments being graded, consideration needs to be
taken for how to set up each assignment in the system. Not every problem can be
graded with the same parameters: there will be specific test cases and
potentially different sections of a program that should be measured. A flexible
configuration system is therefore required to fulfill these requirements.

Since the system needs to integrate with Submitty, assignment configuration
will need the ability to generate the output required to publish results in
the appropriate format. In addition, the system would ideally be flexible
enough to support another grading platform in future, if needed.

### Grading results

Once execution and collection of metrics through the assignment configuration
system is completed, there should be two outputs: the performance grade and
additional "informational results". That is, how well the submission performed
represented as a score and other (arbitrary) information that doesn't directly
contribute to the score value.

The most important aspect of this is how to calculate the performance grade or
score. Given the types of metrics that might be collected, how can a number on
a scale be generated? A cycle count gives a sort of "absolute" measure of how
well a program performs, but this will need to be placed on a relative scale.
It's also worth considering that the relationship between a cycle count and the
scale may not be simple. An algorithm that runs in $O(n^2)$ time may not be
that much worse than program running on $O(n)$ in the case of a particular
assignment.

Any additional outputs that don't factor in to the performance grade need only
be considered based on their usefulness to both instructors or students. Graphs
or diagrams might help to show why a submission received a particular grade.

## High-level components

![Main system components\label{fig:high_level}](img/high_level.jpg)

Figure \ref{fig:high_level} shows the primary components in the Perfgrade
system, along with high-level interactions.

### Submitty

This is the primary driver of the system, along with the only way students can
interact with Perfgrade. Typically for Introduction to Computing, a student will
log in to the interface with their college credentials, select an assignment and
upload a single ARM assembly language source file as their submission. At this
point Submitty hands the source over to Perfgrade, which handles producing the
grades and other outputs shown to the student.

### Perfgrade system

The main "glue" in this project, facilitating assignment configuration. As shown
in the diagram, the student's submission is taken as an input, which is passed
to other components. Outputs from these are used to produce the results required
by Submitty. Note the distinct steps which are individually used in Submitty.

Additionally, it can be seen in the diagram that the system makes use of both
a simulator ("software") and hardware. Both of these options are _almost_
interchangeable in terms of functionality (as will be discussed later).

### Assembler / Linker

A build process making use of an open-source toolchain (where a submission is
assembled and linked to some additional code) to produce a working
firmware for evaluation of a student's program.

### Simulator

The "software" option for evaluation is used to check correctness of a
submission, loading test cases and writing out the results. It's also used in
part to evaluate performance.

### Hardware

A real STM32F4xx-based board is used to evaluate performance of the solution.

## Evaluation environment choice

\definecolor{excellent}{RGB}{100,143,255}
\definecolor{good}{RGB}{254,97,0}
\definecolor{poor}{RGB}{220,38,127}

**Tool** | **Accuracy** | **Performance** | **Compatibility** | **Instrumentation** | **Difficulty**
 ---:|:--- |:--- |:--- |:--- |:---
xPack QEMU | \textcolor{poor}{Low} | \textcolor{good}{Medium} | \textcolor{good}{Medium} | \textcolor{poor}{Low} | \textcolor{excellent}{Low}
Unicorn | \textcolor{poor}{Low} | \textcolor{good}{Medium} | \textcolor{poor}{Low} | \textcolor{good}{Medium} | \textcolor{excellent}{Low}
gem5 | \textcolor{good}{Medium / High*} | \textcolor{poor}{Low} | \textcolor{poor}{Low / Medium*} | \textcolor{excellent}{High} | \textcolor{good}{Medium / High*}
Hardware | \textcolor{excellent}{High} | \textcolor{excellent}{High} | \textcolor{excellent}{High} | \textcolor{good}{Medium / High*} | \textcolor{poor}{High}

The table above shows a comparison of each of the simulators considered for
this project, along with real hardware. As discussed in the background section,
both xPack QEMU and Unicorn are based on QEMU, so they are quite similar.

#### Accuracy

Neither of the QEMU-based emulators are very accurate, given that QEMU is
designed for high performance. In fact, QEMU uses dynamic instruction
translation to maximise speed, which makes the emulation nothing like the real
processor being emulated [@qemu_tcg]. gem5 is much more accurate out of the box,
since it is designed to model complex ARM application cores (Cortex-A series).
It is given a more ambiguous rating since there aren't any configurations for
Cortex-M cores provided, but this should be possible to improve with some work.

#### Performance

Both xPack QEMU and Unicorn therefore have
reasonable performance, although not approaching real ARM hardware of course.
gem5 is a slower since it tries to accurately model complex architectures (when
configured to do so at least).

#### Compatibility

Unicorn has very poor compatibility with firmware built to run on an STM32F407,
given that it is designed to only execute pure instructions. xPack QEMU
is better in this regard, since it aims to emulate real microcontrollers and
boards. gem5's compatbility out of the box is also relatively poor, again due to
the lack of pre-made configurations for Cortex-M platforms (along with a lack of
associated peripheral implementations). With further work, compatibility could
be greatly improved.

#### Instrumentation

QEMU provides no support for instrumentation at all, and this extends to xPack's
fork. Unicorn provides a simple to use API, but it doesn't allow for analysis
beyond granularity of a single instruction. gem5 is set up to collect a lot of
statistics throughout execution (since that's effectively what it was designed
for). It also has the ability to generate very detailed trace data and can be
easily extended to add further instrumentation. ARM defines a number of
standardised debugging tools, which can (in theory) provide a lot of
opportunities for analysis. Their use depends on the implementation being present on
a specific microcontroller however, and can in some cases require additional
expensive hardware.

#### Difficulty

Both QEMU-based emulators are very easy to use, with QEMU and Unicorn being
widely used in the open-source community. gem5 is far less common (and has very
limited documentation). The amount of work required to bring gem5's accuracy
and compatibility closer to real hardware could also be substantial. Setting up
some of the more advanced debugging facilities on a real STM32F407 is also
quite complex.

Overall, *gem5 is really the only choice for a software option*, since neither
xPack QEMU or Unicorn provide any sort of cycle accurate modelling. This is
important for the purposes of the project, since the programs being analysed are
short, hand-written assembly programs. As real STM32F4-based hardware has
inherently perfect accuracy and compatibility, high performance and the
potential for a lot of instrumentation, it is worth exploring this avenue in
addition to gem5.

## Metrics

Given the final choice of evaluation environments, the limits on the types of
metrics that can be collected are set. There are two primary types:
**Execution time** and **Tracing**.

### Execution time

A measurement as crude as a stopwatch can be used to directly compare the
performance of one program
to another. If a program takes longer to execute than another, it stands to
reason that it performs worse.
Using some kind of timer to measure execution time doesn't make a lot of sense
in the context of small, hand-written assembly programs. This is often referred
to as "real time" or "wall-clock time" [@wall_time].

CPU cycle counts would be a more precise measure of execution time, as the
(generally) smallest unit of time a programmer can directly control. Although
CPU features such as pipelining mean that execution of a single instruction does
not directly correspond to a fixed number of CPU cycles, the there's a close
association. The opportunity for variance or errors to arise when measuring
performance using wall time would also increase through the use of operating
systems and preemptive multitasking. When another task or process needs to
execute, real time would continue to count up while the code being measured is
not even running.

### Tracing

In its simplest form, a trace might
contain a sequential list of memory addresses, each being the value of the
program counter every time the CPU executed an instruction. With the original
program, it would be possible to reconstruct the exact path the processor took.

Additional data might be included for each instruction traced, such as the value
of registers involved in the instruction (the "operands"), or the addresses and
values of memory accessed (so-called "data tracing"). In rare cases, code
executed might even by dynamically generated, so it may be necessary to include
the value of the instruction itself in the trace.

Considering the speed of modern processors (and even microcontrollers, including
the STM32F4xx-based chip used in this project), tracing can often generate a
significant amount of data. As such, a simplified statisical method is often
employed when profiling programs. In an example setup, a profiling tool might
sample the value of the processor's program counter at an interval. This results
in a much smaller volume of data, but won't affect accuracy too much in the case
of a long-running execution of a program at high speed.
Profiling is a more broad term for recording
and dynamically analysing execution of blocks of code [@profiling_tracing].

For the purposes of this project, detailed tracing of individual instructions
makes the most sense, given that the programs being evaluated are hand-written
in assembly and relatively short.

## Assignment configuration

In order to accommodate for the specific needs of each assignment, a flexible
configuration system is needed (as previously discussed). Since assignments
will likely consist of a set of common steps with slightly differing setups,
a design incorporating composable "blocks" was decided upon. A
"block" might execute some code in simulator, calculate a grade or generate
Submitty-compatible output. These could be arranged in many configurations, each
with specific options such as the value of test data to use.

There are a number of possible design patterns that could fulfill this idea. One
might be to follow gem5's Python configuration philosophy - write a script
which instantiates and wires up the whole system. However, since assignments
will likely follow a similar set up and pattern of performing one action and
following it up with another that uses the results of the previous, this is
probably unnecessary and might lead to a lot of boilerplate code being needed
for each assignment.

![Blender's node editor for materials\label{fig:blender_nodes}](img/blender_nodes.png)

One model that might be possible is to provide a "node editor". Figure
\ref{fig:blender_nodes} shows an example of this user interface design from
Blender, the free and open-source 3D graphics package [@blender_nodes]. Here,
it's possible to connect a series of "nodes", each of which has a number of
adjustable settings. The combination of different nodes' outputs to other nodes'
inputs can produce vastly different resulting materials ("Material Output" is
the final output node). The visual interface also makes it easier for users
unfamiliar with scripting or programming.

While this pattern might work well for a graphics application, the benefits of
the user-friendly design might not be worth the extra work required to implement
a fully featured graphical interface, especially since the user of the
assignment configuration system will be an instructor for a computer science
course.

DevOps is a popular set of software development practices that can be summarised
as the combination of DEVelopment and OPerations [@devops]. Although flexible
and sometimes loosely defined, there are often Continuous Integration and
Continuous Deployment stages (together referred to CI/CD). Here, changes to
software are automatically built and tested (CI) before being automatically
deployed (CD).

The manner in which software is built and tested varies
significantly, but the inputs and outputs are usually similar. Code to be
tested exists in a version control system (VCS), such as Git. A CI/CD tool pulls
this code and uses some kind of build tool to produce a result that can be
evaluated (e.g. a binary executable). Following this, a test suite might be used
to ensure the software behaves correctly. If the tests pass, a deployment tool
can then be used to make the changes available to a wide audience, such as a web
application.

``` {.yaml label="lst:github-actions" caption="GitHub Actions pipeline example"}
name: Build and deploy presentation

on:
  push:
    branches: [master]
    paths: ['presentation/**']

jobs:
  build_deploy:
    runs-on: ubuntu-20.04
    steps:
      - uses: actions/checkout@v2

      - name: Install reveal-md
        run: sudo yarn global add reveal-md

      - name: Build presentation
        run: |
          cd presentation/
          reveal-md slides.md --css style.css --assets-dir assets --static _site --static-dirs backgrounds

      - name: Deploy to GitHub Pages
        uses: JamesIves/github-pages-deploy-action@4.1.1
        with:
          branch: gh-pages
          folder: presentation/_site
```

Listing \ref{lst:github-actions} is an example of a CI/CD pipeline, written
for GitHub Actions. The purpose of this pipeline (or "workflow" as it is
referred to on the GitHub Actions platform) is to "build" and deploy a
the Reveal.js-based presentation for this project to GitHub Pages. Reveal.js is
"an open source HTML presentation framework", allowing for the creation of
slide presentations written in HTML [@revealjs]. GitHub Pages is "a static site
hosting service that takes HTML, CSS, and JavaScript files straight from a
repository on GitHub, optionally runs the files through a build process, and
publishes a website." [@github_pages].

In the given workflow, the conditions that must be met for the run to be
triggered are laid out (on Git push to the `master` branch and when files under
the `presentation` directory are modified). After this, a number of "steps" in
the workflow process are defined. The details of exactly what each step does is
unimportant, but each one performs some task (via a shell script or an external
GitHub action created by another GitHub user) that modifies the environment,
whether that means installing dependencies or deploying changes to a remote
system. The full extent of the syntax for GitHub Actions is defined in the
official documentation [@github_actions]. Note that the workflow is written in
YAML (YAML Ain't Markup Language), a self-described "human friendly data
serialization standard for all programming languages" [@yaml]. Often used as a
configuration file format, YAML can be translated into popular data exchange
formats such as JSON, but is easier to write by hand.

It could be argued the problem solved by CI/CD systems is analagous
to configuration of assignments to be automatically graded. There are a number
of steps to be taken, each of which may take a number of inputs and produce
outputs (working in a temporary environment). An example step in the context of
an automatically graded assignment might be the compilation of a student's
submission or calculation of a grade. Commonly used steps could be implemented
in the platform (with configurable options) to reduce boilerplate. For increased
flexibility, embedded scripting capabilities could be provided.

The "pipeline" approach was decided upon for the implementation of the
assignment configuration in _Perfgrade_, for its balance of flexibility and
relative ease of use for instructors.

## Grade calculation

## Informational results

\newpage

# Implementation

## gem5 evaluation

Evaluating student submissions with the gem5 simulator was the initial approach
attempted for this project.

## Hardware evaluation

### Tracing

Hardware tracing was attempted for this project, although this avenue ultimately
proved impractical.

## Unified firmware

## Perfgrade platform

Perfgrade is the implementation of the aforementioned "glue" in this project,
providing a pipeline-based system to configure automated assignment evaluation
and grading. The system is written in Python, for ease of development and to
allow for easy scripting capabilities within pipeline definitions.

The source for the application is in the `app/` subdirectory, with the structure
following that of a standard Python library. `app/perfgrade/` contains the code
for all of the classes described in this section.

### Pipeline configuration format

``` {.yaml label="lst:perfgrade-simple" caption="Simple Perfgrade pipeline example"}
steps:
  - id: build
    type: build
    description: Build test code
    input:
      opencm3: /opt/libopencm3
      uut: arraymove.s
      harness: arraymove_harness.s
      defines:
        ARR_SPACE: !expr 1024 * 4

  - type: copy
    description: Copy build results
    input:
      - src: !expr build.elf
        dst: perfgrade.elf
      - src: !expr build.rom
        dst: perfgrade.bin
```

Listing \ref{lst:perfgrade-simple} is an example of a Perfgrade
configuration file, demonstrating the basic structure of a pipeline definition.
The outermost object contains only one key: `steps`. This is an array of step
definitions. Each step has a number of attributes:

- `id`: An optional shorthand identifier for the step, which allows its
  outputs to be referenced in future steps (as `<id>.<output_prop>`).
- `type`: The type of step being defined. A number of pre-defined step types are
  implemented in the Python application to perform a wide range of tasks.
- `description`: An optional human-readable description of the step (shown in
  logs)
- `input`: Type-specific input for the step. This usually contains options and
  references the outputs from previous steps to set up how a step will run.

An additional element seen in Listing \ref{lst:perfgrade-simple} is `!expr`,
which comes after the YAML key but before its value. A lesser-known feature,
tags indicate the underlying type of a value (it is always implied but can be
specified for any node) [@yaml_spec]. The `expr` tag is picked up by Perfgrade
and indicates that the value corresponding to the given key should be
evaluated as a Python expression. For example, `src: !expr build.elf` in listing
\ref{lst:perfgrade-simple} means that the value of `src` will be dynamically
evaluated to be the `elf` output from the `build` step. `!expr` tags can be used
for any input value (including nested ones), as well as the `description`.

### Step implementation

Since the Perfgrade platform is written in Python, a language object-oriented
features, each of the step `type`s is implemented as a class inheriting from a
base `Step`. This class defines a number of methods and defines some common
behaviour, with the `run()` method needing to be implemented by all subclasses
to provide an actual action to be taken.

Notably, `Step` provides `_eval_input()`, which is an internal method that
traverses the `input` tree and evaluates any `!expr`-tagged values as
expressions before `run()` is called to execute the step. The `output` instance
property should be set by the end of `run()` to provide outputs for other steps
to use. Instance property `input` can be accessed by `run()` to read the
processed input tree (with `!expr` values evaluated).

``` {.python label="lst:perfgrade-copy" caption="Perfgrade `Copy` step definition"}
class Copy(Step):
    description = 'Copy files'

    def run(self, ctx: Mapping):
        input_ = self.input
        if not isinstance(self.input, list):
            input_ = [self.input]

        for i in input_:
            if os.path.isdir(i['src']):
                shutil.copytree(i['src'], i['dst'])
            else:
                shutil.copy(i['src'], i['dst'])
```

Listing \ref{lst:perfgrade-copy} shows the complete implementation of the `copy`
step type, a simple step which allows one or more files to be copied (using the
standard library `shutil` functions). Although this step does not provide any
outputs, it references elements of the input array, each of which should have a
`src` file/directory and a `dst` file/directory. The class-level property
`description` provides a default value, used in log output if none is provided
in the configuration file. Listing \ref{lst:perfgrade-simple} shows an example
use of the `copy` step.

``` {.python label="lst:perfgrade-passthrough" caption="Perfgrade `Passthrough` step definition"}
class Passthrough(Step):
    description = 'Pass evaluated input through to output'

    def run(self, ctx: Mapping):
        self.output = self.input
```

Listing \ref{lst:perfgrade-passthrough} shows an even further simplified step
definition. At first glance, this appears to do nothing. However, recall that
`self.input` refers to the processed input tree, with all expressions evaluated.
This provides a convenient way to define via YAML a set of values to be
referenced in later steps, with the added capability to add Python expressions
at any level in the tree.


### Available step types

#### `exec`

This step type takes a Python program as input, and simply evaluates it. This is
effectively a long-form version of an inline expression. While an expression
has limits and must evaluate to a value, the `exec` step uses the Python
standard `exec()` builtin to run code as if it were a complete script. This step
type is akin to the `run:` value in a GitHub Actions step.

_Inputs:_

The input value is a string, which is parsed as a Python script. Use of the
YAML literal block indicator is recommended [@yaml_multiline].

_Outputs:_

None (`self.output` can be set by the script to provide an output)

_Example:_

```yaml
id: test
type: exec
input: |
  from zipfile import ZipFile

  self.output = []
  with ZipFile('spam.zip') as myzip:
      with myzip.open('eggs.txt') as myfile:
          for line in myfile:
              self.output.append(line)
```

#### `passthrough`

As previously described, this step effectively does "nothing", passing its input
(_with evaluation of nested expressions_) as the output.

_Inputs:_

An arbitrary YAML tree.

_Outputs:_

The evaluated input.

_Example:_

```yaml
id: values
type: passthrough
input:
  stuff:
    foo: bar
    qwe: 123
  a:
    b: !expr 5 * 4
```

#### `copy`

Copies files / directories.

_Inputs:_

An array of objects with `src` and `dst` values. A single object (without being
wrapped in an array) can also be provided.

_Outputs:_

None.

_Example:_

```yaml
type: copy
input:
  - src: /etc/hosts
    dst: /tmp/hosts
  - src: /usr/share/man
    dst: /tmp/man
```

#### `build`

Builds a universal firmware (see the dedicated section for further details).

_Inputs:_

- `opencm3`: Path to pre-built `libopencm3` tree
- `uut`: Path to the "unit under test" assembly source file
- `harness`: Path to an optional test harness (`.c` for C or `.s`/`.S` for
   assembly)
- `defines`: Optional array of preprocessor defines (key is the name of the
   define)
- `rom`: Whether or not to produce a raw firmware from the final ELF (defaults
   to `True`)

_Outputs:_

- `dir`: Path to the temporary build directory
- `uut`: Path of the copied uut (relative to the temporary build directory)
- `elf`: Absolute path to the final ELF
- `rom`: Absolute path to the final raw firmware (if requested)

**Note:** The resulting ELF and optional ROM are stored in a temporary
directory which will be deleted upon Perfgrade's exit. Consider using a `copy`
step if they are required after a pipeline has finished executing.

_Example:_

```
id: build
type: build
input:
  opencm3: /opt/libopencm3
  uut: arraymove.s
  harness: arraymove_harness.s
  defines:
    ARR_SPACE: !expr 1024 * 4
```

#### `symtab`

#### `evaluate`

#### `load_traces`

#### `augment_traces`

#### `cycle_count`

#### `heatmap`

#### `curve_guess`

#### `bucket_grade`

#### `diff`

#### `pipeline`

#### `mapped`

#### `include`

### Setup

Perfgrade can be installed in a manner similar to any other Python package, but
requires some additional work to use evaluation features (both `gem5` and
`hardware`). A Docker image is also provided (with these additional dependencies
pre-installed).

...

## Submitty integration

\newpage

# Evaluation

\newpage

# Results and conclusions

\newpage

# References
