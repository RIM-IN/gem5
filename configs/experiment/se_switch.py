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

from ruby import Ruby

from common import Options
from common import Simulation
from common import CacheConfig
from common import CpuConfig
from common import MemConfig
from common.Caches import *
from common.cpu2000 import *


from create_system import create_alpha_21364

parser = optparse.OptionParser()
Options.addCommonOptions(parser)
Options.addSEOptions(parser)

parser.add_option("--prog",   type="string", default="", \
      help="program binary file name")
parser.add_option("--argv",   type="string", default="", \
      help="command line arguments, argv[0] excluded")
parser.add_option("--stdi",   type="string", default="", \
      help="redirected stdin")
parser.add_option("--stdo",   type="string", default="", \
      help="redirected stdout")
# parser.add_option("--tick",   type="string", default="", \
#       help="max simulation ticks, null = infinity")
# parser.add_option("--freq",   type="string", default="", \
#       help="system frequency, null = default")
# parser.add_option("--core",   type="string", \
#       default="AtomicSimple", \
#       help="CPU Type, AtomicSimpleCPU, TimingSimpleCPU or DerivO3CPU")
parser.add_option("--l2as",   type="string", default="", \
      help="L2 Cache sssociativity, null = default")
parser.add_option("--l2lt",   type="string", default="", \
      help="L2 Cache latency, null = default")
parser.add_option("--l2sz",   type="string", default="", \
      help="L2 Cache Size,    null = default")
parser.add_option("--l1dl",   type="string", default="", \
      help="L1 D-Cache latency, null = default")
parser.add_option("--l1ds",   type="string", default="", \
      help="L1 D-Cache size,   null = default")
parser.add_option("--l1il",   type="string", default="", \
      help="L1 I-Cache latency, null = default")
parser.add_option("--l1is",   type="string", default="", \
      help="L1 I-Cache size,  null = default")

(options, pos_args) = parser.parse_args()





(CPUClass, test_mem_mode, FutureClass) = Simulation.setCPUClass(options)
CPUClass.numThreads = 1

print("--------------------echo----------------------")
print("CPU Class = {}".format(CPUClass))
print("Future CPU Class = {}".format(FutureClass))
print("----------------------------------------------")


# Check -- do not allow SMT with multiple CPUs
if options.smt and options.num_cpus > 1:
    fatal("You cannot use SMT with multiple CPUs!")

np = options.num_cpus
system = System(cpu = [CPUClass(cpu_id=i) for i in xrange(np)],
                mem_mode = test_mem_mode,
                mem_ranges = [AddrRange(options.mem_size)],
                cache_line_size = options.cacheline_size)



# Create a top-level voltage domain
system.voltage_domain = VoltageDomain(voltage = options.sys_voltage)

# Create a source clock for the system and set the clock period
system.clk_domain = SrcClockDomain(clock =  options.sys_clock,
                                   voltage_domain = system.voltage_domain)

# Create a CPU voltage domain
system.cpu_voltage_domain = VoltageDomain()

# Create a separate clock domain for the CPUs
system.cpu_clk_domain = SrcClockDomain(clock = options.cpu_clock,
                                       voltage_domain =
                                       system.cpu_voltage_domain)

# If elastic tracing is enabled, then configure the cpu and attach the elastic
# trace probe
if options.elastic_trace_en:
    CpuConfig.config_etrace(CPUClass, system.cpu, options)

# All cpus belong to a common cpu_clk_domain, therefore running at a common
# frequency.
for cpu in system.cpu:
    cpu.clk_domain = system.cpu_clk_domain

if CpuConfig.is_kvm_cpu(CPUClass) or CpuConfig.is_kvm_cpu(FutureClass):
    if buildEnv['TARGET_ISA'] == 'x86':
        system.kvm_vm = KvmVM()
        for process in multiprocesses:
            process.useArchPT = True
            process.kvmInSE = True
    else:
        fatal("KvmCPU can only be used in SE mode with x86")

# Sanity check
if options.simpoint_profile:
    if not CpuConfig.is_atomic_cpu(CPUClass):
        fatal("SimPoint/BPProbe should be done with an atomic cpu")
    if np > 1:
        fatal("SimPoint generation not supported with more than one CPUs")








# -----------------------



process = Process()
process.cmd = [options.prog] + options.argv.split(" ")
if (options.stdi != ""):
      process.input = options.stdi
if (options.stdo != ""):
      process.output = options.stdo

print("\n\n")
print("echo".center(50, "-"))
print(" ".join(process.cmd))
if ("" != process.input):
      print(" < " + process.input)
if ("" != process.output):
      print(" > " + process.output)
print(50*"-")
print("\n\n")


system.cpu[0].workload = process
system.cpu[0].createThreads()


# -----------------------







MemClass = Simulation.setMemClass(options)
system.membus = SystemXBar()
system.system_port = system.membus.slave
CacheConfig.config_cache(options, system)
MemConfig.config_mem(options, system)



























# -------------------------
# override default settings
# -------------------------

# tick_limit_flag   = False
# tick_limit_num    = 100000* 1000
# if (options.tick != ""):
#       tick_limit_flag = True
#       tick_limit_num = int(options.tick)

# if (options.freq != ""):
#       system.clk_domain.clock = str(options.freq)

if (options.l2as != ""):
      system.l2.assoc = int(options.l2as)

if (options.l2lt != ""):
      system.l2.tag_latency = int(options.l2lt)
      system.l2.data_latency = int(options.l2lt)
      system.l2.response_latency = int(options.l2lt)

if (options.l1dl != ""):
      system.cpu[0].dcache.tag_latency = int(options.l1dl)
      system.cpu[0].dcache.data_latency = int(options.l1dl)
      system.cpu[0].dcache.response_latency = int(options.l1dl)

if (options.l1ds != ""):
      system.cpu[0].dcache.size = str(options.l1ds)

if (options.l1il != ""):
      system.cpu[0].icache.tag_latency = int(options.l1il)
      system.cpu[0].icache.data_latency = int(options.l1il)
      system.cpu[0].icache.response_latency = int(options.l1il)

if (options.l1is != ""):
      system.cpu[0].icache.size = str(options.l1is)




# ------ print system config ---------------

print("\n\n")
print("echo".center(50, "-"))

if (hasattr(system.cpu[0], "dcache")):
      print("D Cache Params:")
      print("lat : {}".format(system.cpu[0].dcache.tag_latency))
      print("size : {}".format(system.cpu[0].dcache.size))
      print("assoc : {}".format(system.cpu[0].dcache.assoc))

if (hasattr(system.cpu[0], "icache")):
      print("D Cache Params:")
      print("lat : {}".format(system.cpu[0].icache.tag_latency))
      print("size : {}".format(system.cpu[0].icache.size))
      print("assoc : {}".format(system.cpu[0].icache.assoc))


if (hasattr(system, "l2")):
      print("L2 Cache Params:")
      print("lat : {}".format(system.l2.tag_latency))
      print("size : {}".format(system.l2.size))
      print("assoc : {}".format(system.l2.assoc))

if (hasattr(system.cpu[0], "clk_domain")):
      print("CPU Clock:")
      print((system.cpu[0].clk_domain.clock))


print(50*"-")
print("\n\n")


# -------------------------------------------






# root = Root(full_system = False, system = system)

# m5.instantiate()



# print("Beginning simulation!")


# if (tick_limit_flag):
#       exit_event = m5.simulate(tick_limit_num)
# else:
#       exit_event = m5.simulate()

# print('Exiting @ tick {} because {}'
#       .format(m5.curTick(), exit_event.getCause()))




# MemConfig.config_mem(options, system)


root = Root(full_system = False, system = system)
Simulation.run(options, root, system, FutureClass)
