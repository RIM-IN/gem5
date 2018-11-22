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
from create_system import create_alpha_21364

parser = optparse.OptionParser()
parser.add_option("--prog",   type="string", default="", \
      help="program binary file name")
parser.add_option("--argv",   type="string", default="", \
      help="command line arguments, argv[0] excluded")
parser.add_option("--stdi",   type="string", default="", \
      help="redirected stdin")
parser.add_option("--stdo",   type="string", default="", \
      help="redirected stdout")
parser.add_option("--tick",   type="string", default="", \
      help="max simulation ticks, null = infinity")
parser.add_option("--freq",   type="string", default="", \
      help="system frequency, null = default")
parser.add_option("--core",   type="string", \
      default="AtomicSimple", \
      help="CPU Type, AtomicSimpleCPU, TimingSimpleCPU or DerivO3CPU")
parser.add_option("--l2as",   type="string", default="", \
      help="L2 Cache sssociativity, null = default")
parser.add_option("--l2lt",   type="string", default="", \
      help="L2 Cache latency, null = default")
parser.add_option("--l1dl",   type="string", default="", \
      help="L1 D-Cache latency, null = default")
parser.add_option("--l1il",   type="string", default="", \
      help="L1 I-Cache latency, null = default")

(options, pos_args) = parser.parse_args()



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



system = create_alpha_21364(options.core ,process)





# -------------------------
# override default settings
# -------------------------

tick_limit_flag   = False
tick_limit_num    = 100000* 1000
if (options.tick != ""):
      tick_limit_flag = True
      tick_limit_num = int(options.tick)

if (options.freq != ""):
      system.clk_domain.clock = str(options.freq)

if (options.l2as != ""):
      system.l2cache.assoc = int(options.l2as)

if (options.l2lt != ""):
      system.l2cache.tag_latency = int(options.l2lt)
      system.l2cache.data_latency = int(options.l2lt)
      system.l2cache.response_latency = int(options.l2lt)

if (options.l1dl != ""):
      system.cpu[0].dcache.tag_latency = int(options.l1dl)
      system.cpu[0].dcache.data_latency = int(options.l1dl)
      system.cpu[0].dcache.response_latency = int(options.l1dl)

if (options.l1il != ""):
      system.cpu[0].icache.tag_latency = int(options.l1il)
      system.cpu[0].icache.data_latency = int(options.l1il)
      system.cpu[0].icache.response_latency = int(options.l1il)

print("\n\n")
print("echo".center(50, "-"))
print(" CPU Type = {}".format(type(system.cpu)))
print(" I Cache Size = {} Byte".format(system.cpu.icache.size))
print(" D Cache Size = {} Byte".format(system.cpu.dcache.size))
print(50*"-")
print("\n\n")







root = Root(full_system = False, system = system)

m5.instantiate()

print("Beginning simulation!")


if (tick_limit_flag):
      exit_event = m5.simulate(tick_limit_num)
else:
      exit_event = m5.simulate()

print('Exiting @ tick {} because {}'
      .format(m5.curTick(), exit_event.getCause()))