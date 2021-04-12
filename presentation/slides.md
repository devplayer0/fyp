---
title: Beyond functional autograding of ARM assembly language programs
theme: moon
separator: -----
verticalSeparator: ---
---

## Beyond functional autograding of ARM assembly language programs

_Final year project_

Jack O'Sullivan

osullj19@tcd.ie

Note:

- Slide presentation
- Demo of backend in terminal, then Submitty online system
- Results of student participation
- Feel free to ask questions at any stage!

-----

# Motivation and goals

---

## Motivation

- Automated grading is a powerful tool
- "Functional" or "black box" grading has limited value
- Correctness is not the only benchmark of a solution
- Student learning opportunities

Note:

Automated grading is very useful to instructors and students. Instructors and
TA's can save time when grading. Know this from experience marking assignments
on the module - particularly when correcting something more difficult to follow,
like assembly. Students can also benefit - immediate feedback on whether their
solution works.

"Functional" or "black box" systems only measure correctness - pass an input to
a program and check the output against a known-good result. How the program
arrives at this conclusion is unknown. To illustrate, the worst case is a
submission which simply prints a pre-determined correct result and in fact does
nothing at all! (Hidden test cases and manual cases are used to fix this)

While a solution to a problem should first produce the correct results, in real
world use the program should be well-written: performance and maintainability
are two important aspects, for example. If a program can sort an array correctly
but runs in O(n^3) time, it's not much use.

While the instant feedback of a functional autograding system is useful, a
purely success / failure result isn't a huge help to student learning. Providing
more detailed information on _how_ a student's work was graded the way it was
could be very helpful and encourage them to improve their work.

---

## Goals

- Focus on performance measurement
- Dynamic analysis of student code (simulator or real hardware)
- Produce a grade from performance metrics
- Generate performance feedback for instructors and students
- Integrate with Submitty

Note:

For the purposes of this project, the focus is on performance (over other
potential aspects such as maintainability).

Run students' code in a manner similar to the way it is already, through the use
of some kind of simulator / emulator (with a focus on accuracy and
instrumentation) or real hardware (in a way that can be automated with
relative ease).

With data collected from execution, figure out a way to place a student's
submission on a scale based on how well it performs.

<!-- TODO: published research? -->
Human-readable information generated from collected data such as graphs would be
useful (as mentioned before).

Submitty is the platform currently used in the Intro to Computing modules for
automated grading, so integration with this system is important to get the
project working in the real world.

-----

# Design

---

## How to measure performance?

- Metrics
- Hardware vs Software
- Assignment configuration
- Translate a metric into a performance "value"
- Informational results

---

## Metrics

- Cycle counts
- Tracing
 - Instructions types used
 - Memory accesses
 - ...

---

## Hardware vs Software

- Software: Simulation / emulation
 - Easy to deploy
 - Accuracy?
 - Performance?
- Hardware: A real microcontroller
 - Harder to deploy
 - Complexity and reliability
- Both: Instrumentation capabilities?

---

## Emulators and simulators

- xPack QEMU
 - QEMU fork
 - Emulates Cortex-M4 (no FPU)
 - Specific STM32 peripherals
- Unicorn
 - Another QEMU fork
 - Widely used in reverse engineering
 - Pure software with API
- gem5
 - Highly advanced modelling
 - Very modular
 - Contributions from silicon vendors

---

## Comparison

<table style="font-size: 60%;">
  <thead>
    <tr>
        <th>Tool</th>
        <th>Accuracy</th>
        <th>Performance</th>
        <th>Compatibility</th>
        <th>Instrumentation</th>
        <th>Difficulty</th>
    </tr>
  </thead>
  <tbody>
    <tr>
        <td>xPack QEMU</td>
        <td class="t-poor">Low</td>
        <td class="t-good">Medium</td>
        <td class="t-good">Medium</td>
        <td class="t-poor">Low</td>
        <td class="t-excellent">Low</td>
    </tr>
    <tr>
        <td>Unicorn</td>
        <td class="t-poor">Low</td>
        <td class="t-good">Medium</td>
        <td class="t-poor">Low</td>
        <td class="t-good">Medium</td>
        <td class="t-excellent">Low</td>
    </tr>
    <tr>
        <td>gem5</td>
        <td class="t-good">Medium / High*</td>
        <td class="t-poor">Low</td>
        <td class="t-poor">Low / Medium*</td>
        <td class="t-excellent">High</td>
        <td class="t-good">Medium / High*</td>
    </tr>
    <tr>
        <td>Hardware</td>
        <td class="t-excellent">High</td>
        <td class="t-excellent">High</td>
        <td class="t-excellent">High</td>
        <td class="t-excellent">High*</td>
        <td class="t-poor">High</td>
    </tr>
  </tbody>
</table>

---

## gem5

- Best overall simulator
- ARM components designed for Cortex-A* cores
- Develop a simplified, accurate configuration
 - "Minor" CPU model (in-order with branch prediction)
 - No caches, peripherals or DRAM
- Support loading of "vanilla" firmware
 - Not a user-mode ELF
 - Not a Linux kernel
- Generate parsable trace data

---

## gem5 architecture

- Everything is a `SimObject`, e.g. a CPU, memory module or peripheral
 - Each `SimObject` has a Python binding
 - Write a Python script to construct configurations from `SimObject`s
- `SimObjects` for this project:
  - A bare-metal workload
  - Custom tracer to produce machine-readable data
  - Hooks to load / dump memory for testing

---

## Hardware

- Accurate simulation is hard, STM32F4xx boards are cheap
- Open-source build tools (`libopencm3`)
 - "Universal" gem5 + hardware firmware
- Interacting with the debugging features
 - OpenOCD is the classic tool (e.g. provides `gdb` remote)
 - PyOCD is similar (in features) but entirely scriptable
- ARMv7-M Data Watchpoint and Trace unit (DWT) provides a cycle counter
- Tracing???

---

## Tracing???

- Embedded Trace Macrocell (ETM)
 - Precise, detailed and non-invasive
 - Standard part of ARM's "CoreSight Architecture"
- Usually requires €€€ hardware
 - Clock CPU down
 - Low-cost logic analyser
 - Complex protocol!
- Cortex-M4's ETM (aka ETM-M4) doesn't support cycle-accurate tracing 😥

---

## Assignment configuration

- Each assignment has specific requirements
- "Pipeline"-style configuration
 - Inspired by DevOps
 - YAML config file
 - "Steps" do a specific task, e.g. run simulator or calculate grade
 - Inline Python expressions (optional arbitrary Python steps)
- Flexible system
 - Can be used standalone
 - Integrate with Submitty autograding

---

## Translating metrics into a grade

- Most obvious: look at the cycle count
- "Bucketing": Grade based on a range
 - Nuance based on a "class of performance"
- Measure cycles as the input size grows
 - Guess complexity with curve fitting
 - Plot log-log and approximate $k$ in $O(n^k)$
 - Use $k$ instead of raw cycle count for bucket grading

---

## Informational results

- "Heatmap"
 - Use trace data to count individual instruction metrics
 - Highlight lines of the program
- Grade curve
 - Show buckets and $k$
- Plot input size vs cycle count
 - Points are measured data
 - Draw fitted function

-----

# Implementation

-----

# Results
