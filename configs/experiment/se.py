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
      help="system frequency, unit GHz, null = default")
parser.add_option("--core",   type="string", \
      default="AtomicSimpleCPU", \
      help="CPU Type, AtomicSimpleCPU, TimingSimpleCPU or DerivO3CPU")
parser.add_option("--l2as",   type="string", default="", \
      help="L2 Cache sssociativity, null = default")
parser.add_option("--l2lt",   type="string", default="", \
      help="L2 Cache latency, null = default")

(options, pos_args) = parser.parse_args()



process = Process()
process.cmd = [options.prog] + options.argv.split(" ")
process.input = options.stdi
process.output = options.stdo

print("echo".center(50, "-"))
print(" ".join(process.cmd))
if ("" != process.input):
      print(" < " + process.input)
if ("" != process.output):
      print(" < " + process.output)
print(50*"-")


system = create_alpha_21364(options.core ,process)












root = Root(full_system = False, system = system)

m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()
print('Exiting @ tick {} because {}'
      .format(m5.curTick(), exit_event.getCause()))