
from m5.objects import *



# Alpha 21264 Address ALU L0 and L1
# used as simple Int ALU and address calc
class Alpha21264_AddrALU(FUDesc):
    opList = [ OpDesc(opClass='IntAlu', opLat=1) ]
    count = 2

# Alpha 21264 Address INT UNIT
# used for
class Alpha21264_IntUnit(FUDesc):
    opList = [
                OpDesc(opClass='IntAlu',    opLat=1, pipelined=True),
                OpDesc(opClass='IntMult',   opLat=7, pipelined=True),
                OpDesc(opClass='IprAccess', opLat=3, pipelined=True)
               ]
    count = 2

# Alpha21264 dedicated floating point multiplier
class Alpha21264_FpMul(FUDesc):
    opList = [
               OpDesc(opClass='FloatMult', opLat=4)
               ]
    count = 1

# Alpha21264 complex floating point function unit
class Alpha21264_FpMisc(FUDesc):
    opList = [
               OpDesc(opClass='FloatAdd',   opLat   = 4),
               OpDesc(opClass='FloatCmp',   opLat   = 4),
               OpDesc(opClass='FloatCvt',   opLat   = 4),
               OpDesc(opClass='FloatDiv',   opLat   = 12, pipelined=False),
               OpDesc(opClass='FloatSqrt',  opLat   = 15, pipelined=False),
               OpDesc(opClass='FloatMisc',  opLat   = 4)
               ]
    count = 1


# Load/Store Units
class Alpha21264_Load(FUDesc):
    opList = [ OpDesc(opClass='MemRead',opLat=3),
               OpDesc(opClass='FloatMemRead',opLat=4) ]
    count = 1
class Alpha21264_Store(FUDesc):
    opList = [ OpDesc(opClass='MemWrite',opLat=3),
               OpDesc(opClass='FloatMemWrite',opLat=4) ]
    count = 1

# Functional Units for this CPU
class Alpha21264_FUP(FUPool):
    FUList = [
                Alpha21264_AddrALU(), Alpha21264_IntUnit(),
                Alpha21264_FpMul(), Alpha21264_FpMisc(),
                Alpha21264_Load(), Alpha21264_Store()
                ]


# Alpha21264 Tournament Branch Predictor
class Alpha21264_BP(TournamentBP):
    localPredictorSize      = 1024
    localCtrBits            = 3
    localHistoryTableSize   = 1024
    globalPredictorSize     = 4096
    globalCtrBits           = 2
    choicePredictorSize     = 4096
    choiceCtrBits           = 2



class Alpha21264_CPU(DerivO3CPU):

    LQEntries   = 32
    SQEntries   = 32
    LSQDepCheckShift = 0
    LFSTSize = 1024
    SSITSize = 1024

    decodeToFetchDelay  = 1
    renameToFetchDelay  = 1
    iewToFetchDelay     = 1
    commitToFetchDelay  = 1
    renameToDecodeDelay = 1
    iewToDecodeDelay    = 1
    commitToDecodeDelay = 1
    iewToRenameDelay    = 1
    commitToRenameDelay = 1
    commitToIEWDelay    = 1

    fetchWidth          = 4
    fetchBufferSize     = 32
    fetchToDecodeDelay  = 3

    # decode parameters
    decodeWidth         = 4
    decodeToRenameDelay = 2
    # rename parameters
    renameWidth         = 4
    renameToIEWDelay    = 1
    # issue parameters
    issueToExecuteDelay = 1
    dispatchWidth       = 6
    issueWidth          = 6

    fuPool              = Alpha21264_FUP()
    wbWidth             = 6

    iewToCommitDelay    = 1

    renameToROBDelay    = 1

    commitWidth         = 6
    squashWidth         = 6

    trapLatency         = 13
    backComSize         = 5
    forwardComSize      = 5

    # register gile setting
    numPhysIntRegs      = 160
    numPhysFloatRegs    = 72

    numIQEntries        = 35
    numROBEntries       = 80

    switched_out        = False


    branchPred          = Alpha21264_BP()



# L1 Instruction Cache
class Alpha21264_ICache(Cache):
    tag_latency         = 1
    data_latency        = 1
    response_latency    = 1
    mshrs               = 2
    tgts_per_mshr       = 8
    size                = '64kB'
    assoc               = 2
    is_read_only        = True
    # Writeback clean lines as well
    writeback_clean     = True


# L1 Data Cache
class Alpha21264_DCache(Cache):
    tag_latency         = 3
    data_latency        = 3
    response_latency    = 3
    mshrs               = 6
    tgts_per_mshr       = 8
    size                = '64kB'
    assoc               = 2
    write_buffers       = 16




# L2 Cache
# Alpha21264 official cache is an external cache,
# not on-chip cache! So some parameters may seems
# a little strange
class Alpha21264_L2Cache(Cache):
    # here, 18 = 12 cycle cache latency + 6 cycle
    # transfer latncy, because L2 is external by default
    tag_latency         = 18
    data_latency        = 18
    response_latency    = 18
    size                = '2MB'
    assoc               = 1
    mshrs               = 16
    tgts_per_mshr       = 8
    write_buffers       = 8
    prefetch_on_access = True
