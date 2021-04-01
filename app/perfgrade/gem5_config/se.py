import argparse

# import the m5 (gem5) library created when gem5 is built
import m5
# import all of the SimObjects
from m5.objects import *

from common import CM4

parser = argparse.ArgumentParser()
parser.add_argument('program', help='Program to run')
parser.add_argument('--wait-gdb', action='store_true', help='Wait for GDB')

args = parser.parse_args()

# create the system we are going to simulate
system = System()

# Set the clock fequency of the system (and all of its children)
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '100MHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Set up the system
system.mem_mode = 'timing'               # Use timing accesses
system.mem_ranges = [AddrRange('512MB')] # Create an address range

# Create a simple CPU
system.cpu = CM4()

# Create a memory bus, a system crossbar, in this case
system.membus = SystemXBar()

# Hook the CPU ports up to the membus
system.cpu.icache_port = system.membus.slave
system.cpu.dcache_port = system.membus.slave

# create the interrupt controller for the CPU and connect to the membus
system.cpu.createInterruptController()

# Create a DDR3 memory controller and connect it to the membus
#system.mem_ctrl = MemCtrl()
#system.mem_ctrl.dram = DDR3_1600_8x8()
#system.mem_ctrl.dram.range = system.mem_ranges[0]
#system.mem_ctrl.port = system.membus.master
system.mem_ctrl = SimpleMemory(latency='30ns')
system.mem_ctrl.port = system.membus.master

# Connect the system up to the membus
system.system_port = system.membus.slave

# get ISA for the binary to run.
isa = str(m5.defines.buildEnv['TARGET_ISA']).lower()

# Create a process for a simple "Hello World" application
process = Process()
# Set the command
# cmd is a list which begins with the executable (like argv)
process.cmd = [args.program]
# Set the cpu to use the process as its workload and create thread contexts
system.cpu.workload = process
system.cpu.wait_for_remote_gdb = args.wait_gdb
system.cpu.createThreads()

system.cpu.tracer = PerfgradeTracer()

# set up the root SimObject and start the simulation
root = Root(full_system = False, system = system)
# instantiate all of the objects we've created above
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()
print('Exiting @ tick %i because %s' % (m5.curTick(), exit_event.getCause()))
