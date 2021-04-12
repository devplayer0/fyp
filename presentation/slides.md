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

Note:

Look at the planned features included the final "product".

---

## How to measure performance?

- Metrics
- Hardware vs Software
- Assignment configuration
- Translate a metric into a performance "value"
- Informational results

Note:

A few key items to think about when designing the overall system.

- Metrics: What sort of data can be generated?
- Hardware vs Software: Two obvious overall ways of measuring performance
- Assignment configuration: How to set up the system to grade an assignment
- Metric to performance value: How to translate data to a grade?
- Informational results: Non-grade output from data

---

## Metrics

- Cycle counts
- Tracing
 - Where does a program spend its time?
 - Instructions types used
 - Memory accesses
 - ...

Note:

The easiest metric to create is a count of how many CPU cycles it took to run a
program. This value gives an absolute number of how well a student's solution
performed.

Tracing is the idea of keeping track what the CPU is actually doing at a very
fine-grained level (from sampling the program counter to generating information
for every instruction executed). A lot of results might be produced from such
detailed information, such as determining which parts a program uses most of its
CPU cycles on. It would also be easy to track specific types of instructions
(including their register values), memory access and many others.

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

Note:

Just a quick comparison of those two main measurement methods.

When talking about software, specifically I mean some kind of simulator or
emulator. The easiest benefit to identify is probably ease of deployment - a
good emulator can usually run anywhere, from a laptop to a server. When
considering candidates for this project, the accuracy of a given emulator is
key - we want to precisely measure a short hand-written assembly program's
performance. The speed of the emulator itself is another factor that will
actually become quite important later.

Real hardware presents an immediate challenge: how to set up one or more
development boards? There's a practical question of how to physically configure
such a deployment. The complexity raised by having to manage flashing and
debugging of a real microcontroller is also an issue. Extra precautions should
ideally be made to ensure code running in real hardware is safe.

For the purposes of this project, the degree to which execution can be
instrumented is very important.

---

## Emulators and simulators

- xPack QEMU
 - QEMU fork
 - Emulates Cortex-M4 (no FPU)
 - Specific STM32 peripherals
 - Used for Intro to Computing
- Unicorn
 - Another QEMU fork
 - Pure software with API
 - Widely used in reverse engineering
- gem5
 - Highly advanced modelling
 - Very modular
 - Contributions from silicon vendors

Note:

There were three emulators / simulators considered for this project.

xPack QEMU ARM is a fork of the popular open-source emulator QEMU. Provided by
the xPack project (which provides a toolchain management suite for embedded
software), it is specifically designed to emulate Cortex-M3/M4 boards (the
Cortex-M4 being a Cortex-M3 with optional floating point and DSP extensions,
xPack QEMU doesn't support floating point).
For example, when writing to an STM32F4xx GPIO peripheral in emulated code,
xPack QEMU can draw a virtual development board with an LED which is lit based
on the state of the GPIO pin wired to the LED in real hardware. This emulator is
currently used in Intro to Computing!

Unicorn is the self-described "Ultimate CPU emulator", designed to emulate many
CPU's and provide an easily accessible API. It is again a fork of QEMU, but is
designed solely to execute raw instructions (no peripherals supported). Unicorn
is widely used in reverse engineering and other infosec tools (given it has
bindings in 10+ languages).

gem5 is an advanced simulator designed specifically for computer architecture
research, and thus provides very advanced modelling of system components. Its
design is modular and quite extensible, and has contributions from large
silicon vendors (including ARM), while remaining fully open-source.

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
        <td class="t-good">Medium / High*</td>
        <td class="t-poor">High</td>
    </tr>
  </tbody>
</table>

Note:

A comparison of the most important aspects of each emulator / simulator (from
this project's perspective).

Both xPack QEMU and Unicorn are based on QEMU and are therefore quite similar.
Since QEMU is designed to be a high-performance emulator for cross-platform
execution of programs, it has poor accuracy. Since QEMU xPack emulates specific
Cortex-M4 hardware (and even specific STM32F4xx hardware), it has quite good
compatibility (minus floating point hardware).

QEMU is not designed with extensibility in mind (and has a quite nasty
codebase). Plain QEMU (i.e. xPack) has little to no opportunities for
instrumentation. Unicorn provides a clean API for per-instruction
instrumentation, but individual CPU cycles are a non-starter.

Both QEMU-based options are easy to use, with QEMU in general being
well-supported, xPack QEMU being already proven for Intro to Computing and
Unicorn being widely used in infosec tooling.

gem5 comes with a number of asterisks, mainly due to its modularity. gem5 has
successfully modelled very complex cores, but is not set up for Cortex-M* cores
out of the box (so work is needed to improve accuracy from "good" to
"excellent"). Due to its focus on accuracy, gem5 is very slow. Again due to not
supporting Cortex-M* out of the box, compatibility with code designed for
Cortex-M* MCU's is poor (especially for peripherals), but can be improved. gem5
provides many opportunities to instrument code and gather statistics (since this
is essentially what it was designed for). Finally, it has a significant learning
curve over the other options (with poor documentation and much less general
use). Improving accuracy and compatibility might involve increasing amounts of
modifications to gem5's internals!

Real hardware obviously has perfect accuracy, compatibility and high performance
(STM32F407 can clock up to 168MHz). ARM also provides a number of debugging
tools which (at least in theory) provide a large number of opportunities for
instrumentation and gathering metrics. Setting up and managing real hardware to
perform all of this is a challenge, however.

---

## gem5

- Best overall simulator
- ARM components designed for Cortex-A* cores
- Develop a simplified, accurate configuration
 - "Minor" CPU model (in-order with branch prediction)
 - No caches, DRAM or peripherals
- Support loading of "vanilla" firmware
 - Not a user-mode ELF
 - Not a Linux kernel
- Generate parsable trace data

Note:

gem5 was chosen as the approach to design a simulator-based system for this
project, being the only option from those explored with any kind of
cycle-accurate emulation (along with high extensibility).

As previously mentioned however, gem5 is not set up to simulate a Cortex-M*
core. In fact, contributors have put a lot of work into developing a highly
accurate ARMv8 Cortex-A* simulation, including out-of-order execution, caches,
DRAM and even graphics.

For this project, a simplified configuration is needed (most likely using the
"Minor" CPU model, which is in-order only but includes branch prediction,
similar to a real Cortex-M4). The configuration won't have any caches or DRAM
and likely won't feature any peripherals.

Ideally the setup would be able to load a raw firmware image (similar to what
would be flashed to the ROM on a real STM32F4xx). gem5 normally operates in
either syscall emulation (user-mode ELF) or full system (with Linux `Image`)
mode.

Finally, machine-readable trace data would be required (gem5 can generate traces
but it's a messy text format designed for human inspection).

---

## gem5 architecture

- Everything is a `SimObject`, e.g. a CPU, memory module or peripheral
 - Each `SimObject` has a Python binding
 - Write a Python script to construct configurations from `SimObject`s
- `SimObjects` for this project:
  - A bare-metal workload
  - Custom tracer to produce machine-readable data
  - Hooks to load / dump memory for testing

Note:

In gem5's modular design, all components in a system are so-called `SimObject`s.
These are written in C++ and communicate with each other over "ports". These
`SimObject`s then have a Python binding. A Python script drives the layout or
configuration of all components in a simulated system, instantiating the
`SimObject`s and wiring up ports.

This project will require a few specific `SimObject`s (along with a custom
Python configuration script of course). Since compatibility with a bare-metal
firmware is desirable, a custom `SimObject` will handle loading this (along with
setting up the basic starting system state). A custom tracer implementation
will generate a more machine-readable trace data representation. Finally, it'll
be necessary to load test data into memory at runtime (and dump the results)
when evaluation is finished.

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

Note:

As it will turn out later, getting gem5 to accurately simulate a Cortex-M* core
is quite difficult. With STM32F4xx boards being quite cheap, it's worth also
trying a hardware-based approach.

Many open-source tools exist for running code on Cortex-M*-based boards,
`libopencm3` is a lightweight library which doesn't provide hardware
abstraction, but definitions and simple routines to access to all of the ARM,
Cortex-M4 and STM32Fxx peripherals, along with tooling to build and flash
firmware images. With this, it would be ideal to generate a "universal"
firmware that can run without modification in both gem5 and in hardware.

In order to make use of the core's debugging features, a software debugging
component is needed. OpenOCD (the Open On-Chip Debugger) is the classic
open-source tool for this purpose (e.g. providing a GDB stub). PyOCD is a
Python-based alternative with a similar feature set, but with much improved
scripting capabilities (very helpful for automation).

The ARMv7-M architecture standardises the Data Watchpoint and Trace unit (aka
DWT) - this provides a software-controllable cycle counter (along with some
other instrumentation features). What about tracing?

---

## Tracing???

- Embedded Trace Macrocell (ETM)
 - Precise, detailed and non-invasive
 - Standard part of ARM's "CoreSight Architecture"
- Usually requires €€€ hardware
 - Makes sense for multi-GHz cores
 - Clock CPU down?
 - Low-cost logic analyser
 - Complex protocol!
- Cortex-M4's ETM (aka ETM-M4) doesn't support cycle-accurate tracing 😥

Note:

ARM specifies the Embedded Trace Macrocell (or ETM) for highly detailed
execution (and also data) tracing of ARM cores. The Cortex-M4's implementation
of the ETM is based on ARM's universal "CoreSight Architecture".

Generally, it's set up to require very expensive hardware (in multiple hundreds
to thousands), along with proprietary software. The need for these makes sense
when considering the volume of tracing data that could be produced by a
multi-GHz Cortex-A* core, but what about a simple Cortex-M MCU? The core could
be clocked way down to a speed that a cheap knockoff logic analyser could work
with. Unfortunately, the wire protocol is quite complex.

The final nail is the fact that cycle-accurate tracing is an optional feature
that the Cortex-M4's ETM (the ETM-M4) doesn't support.

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
 - Something else?

Note:

Once all of the evaluation pieces are in place, how to actually do automated
grading? Each assignment might have its own needs...

DevOps is an ever-popular idea, what about a "pipeline"? An assignment's entire
autograding configuration could be specified in one (or more) YAML files (YAML
being a human-friendly config language). Each element of the YAML document could
describe a single "step" in the pipeline, such as running code in a simulator or
calculating a grade from previously-gathered data. Allow for inline Python
expressions and arbitrary Python snippets.

By providing a very flexible system, it could be used in many ways. For
development, a "standalone" pipeline could be useful. Later, a
Submitty-compatible configuration would be needed for actual automated grading.
In future it should be possible to work with any other system.

---

## Translating metrics into a grade

- Most obvious: look at the cycle count
 - An "absolute" value
- "Bucketing": grade based on ranges
 - Map with a function to a grade
 - Nuance based on a "class of performance"
- Measure cycles as the input size grows
 - A number of "runs"
 - Guess complexity with curve fitting
 - Plot log-log and approximate $k$ in $O(n^k)$
 - Use $k$ instead of raw cycle count for bucket grading

Note:

So how to use gathered data to generate a grade? The simplest method is just to
use a cycle count, which can be easily obtained from either the software or
hardware methods. This is only an "absolute" number, however.

Taking the cycle count metric a small step further, a given result could be
placed in a number of buckets, and then mapped over a function to produce a
final grade. The function might be different per-bucket (to grade differently
based on the "class" of performance).

For a more advanced measurement, the cycle count could be measured as the size
of the input grows (i.e. a number of evaluations of a program) would be needed.
This is where the performance of the system becomes important! With a number of
data points, the input size could be plotted against cycle count. Curve fitting
can then be used to estimate the time complexity of a program. Using a log-log
plot would allow for `k` in `O(n^k)` to be estimated (the slope of such a
graph). `k` could then become the value used for the input to the bucketing
method described above.

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

Note:

What additional information could be generated and presented to students /
instructors?

A "heatmap" of the program might be useful. Trace data could be used to count
how many times an instruction was executed (and how many CPU cycles those
executions took). This could then be placed adjacent to each line of the
original assembly source, with a colour gradient based on the fraction of the
programs total cycles were spent on a given line.

A "grade" curve could show all of the grading buckets, their corresponding
functions along with the calculated `k` vs the resulting grade.

Finally, each of the executions could be plotted as points (input size against
cycle count), with the fitted big-O function drawn underneath.

-----

# Implementation

---

## gem5 additions

---

## Pipeline system

---

## Hardware target

-----

# Results
