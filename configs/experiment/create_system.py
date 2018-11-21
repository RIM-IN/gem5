# Alpha 21364 SE Mode
# Configuration File
from __future__ import print_function

import sys, os, optparse
import m5
from m5.objects import *
from m5.defines import buildEnv
from m5.objects import *
from m5.util import addToPath, fatal, warn
addToPath('../')
from common import Caches
from common.cores.alpha import alpha_21364



def create_alpha_21364(cpu_type, process):

    system = System()
    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = '1.25GHz'
    system.clk_domain.voltage_domain = VoltageDomain()

    # set system memory
    if (cpu_type == "AtomicSimpleCPU"):
        system.mem_mode = "atomic"
    else:
        system.mem_mode = 'timing'

    system.mem_ranges = [AddrRange('1024MB')]
    system.membus = SystemXBar()


    if (cpu_type == "DerivO3CPU"):
        system.cpu = alpha_21364.Alpha21364_CPU()
    elif (cpu_type == "TimingSimpleCPU"):
        system.cpu = TimingSimpleCPU()
    else:
        system.cpu = AtomicSimpleCPU()


    system.cpu.icache = alpha_21364.Alpha21364_ICache()
    system.cpu.dcache = alpha_21364.Alpha21364_DCache()

    # connect the CPU and L1 caches
    system.cpu.icache.cpu_side = system.cpu.icache_port
    system.cpu.dcache.cpu_side = system.cpu.dcache_port

    system.l2bus = L2XBar()
    system.cpu.icache.mem_side = system.l2bus.slave
    system.cpu.dcache.mem_side = system.l2bus.slave

    system.l2cache = alpha_21364.Alpha21364_L2Cache()

    system.l2cache.cpu_side = system.l2bus.master
    system.l2cache.mem_side = system.membus.slave


    system.cpu.createInterruptController()

    system.system_port = system.membus.slave



    system.mem_ctrl = DDR3_1600_8x8()
    system.mem_ctrl.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.master


    system.cpu.workload = process
    system.cpu.createThreads()


    return system
