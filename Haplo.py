#! /usr/bin/env python

"""Module for estimating haplotypes.

"""
import sys, string, os, re
from Arlequin import ArlequinBatch
from Utils import getStreamType

class Haplo:
    """*Abstract* base class for haplotype parsing/output.

    Currently a stub class (unimplemented).
    """
    pass

class HaploArlequin(Haplo):
    """Haplotype estimation implemented via Arlequin
    
    Outputs Arlequin format data files and runtime info, also runs and
    parses the resulting Arlequin data so it can be made available
    programatically to rest of Python framework.

    Delegates all calls Arlequin to an internally instantiated
    ArlequinBatch Python object called 'batch'.  """
    
    def __init__(self,
                 arpFilename,
                 idCol,
                 prefixCols,
                 suffixCols,
                 windowSize,
                 mapOrder = None,
                 untypedAllele = '0',
                 arlequinPrefix = "arl_run",
                 debug=0):

        """Constructor for HaploArlequin object.

        Expects:

        - arpFilename: Arlequin filename (must have '.arp' file
          extension)
        
        - idCol: column in input file that contains the individual id.
        
        - prefixCols: number of columns to ignore before allele data
          starts
        
        - suffixCols: number of columns to ignore after allele data
          stops
        
        - windowSize: size of sliding window

        - mapOrder: list order of columns if different to column order in file
          (defaults to order in file)

        - untypedAllele:  (defaults to '0')
        
        - arlequinPrefix: prefix for all Arlequin run-time files
        (defaults to 'arl_run').

        - debug: (defaults to 0)
        
        """

        self.arpFilename = arpFilename
        self.arsFilename = 'arl_run.ars'
        self.idCol = idCol
        self.prefixCols = prefixCols
        self.suffixCols = suffixCols
        self.windowSize = windowSize
        self.arlequinPrefix = arlequinPrefix
        self.mapOrder = mapOrder
        self.untypedAllele = untypedAllele
        self.debug = debug
        
        # arsFilename is default because we generate it
        self.batch = ArlequinBatch(arpFilename = self.arpFilename,
                              arsFilename = self.arsFilename,
                              idCol = self.idCol,
                              prefixCols = self.prefixCols,
                              suffixCols = self.suffixCols,
                              windowSize = self.windowSize,
                              mapOrder = self.mapOrder,
                              debug = self.debug)

    def outputArlequin(self, data):
        """Outputs the specified .arp sample file.
        """
        self.batch.outputArlequin(data)

    def _outputArlRunArs(self, arsFilename):
        """Outputs the run-time Arlequin setting file.

        """
        file = open(arsFilename, 'w')
        file.write("""[Setting for Calculations]
TaskNumber=8
DeletionWeight=1.0
TransitionWeight=1.0
TranversionWeight=1.0
UseOriginalHaplotypicInformation=0
EliminateRedondHaplodefs=1
AllowedLevelOfMissingData=0.0
GameticPhaseIsKnown=0
HardyWeinbergTestType=0
MakeHWExactTest=0
MarkovChainStepsHW=100000
MarkovChainDememorisationStepsHW=1000
PrecisionOnPValueHW=0.0
SignificanceLevelHW=2
TypeOfTestHW=0
LinkageDisequilibriumTestType=0
MakeExactTestLD=0
MarkovChainStepsLD=100000
MarkovChainDememorisationStepsLD=1000
PrecisionOnPValueLD=0.01
SignificanceLevelLD=0.05
PrintFlagHistogramLD=0
InitialCondEMLD=10
ComputeDvalues=0
ComputeStandardDiversityIndices=0
DistanceMethod=0
GammaAValue=0.0
ComputeTheta=0
MismatchDistanceMethod=0
MismatchGammaAValue=0.0
PrintPopDistMat=0
InitialConditionsEM=50
MaximumNumOfIterationsEM=5000
RecessiveAllelesEM=0
CompactHaplotypeDataBaseEM=0
NumBootstrapReplicatesEM=0
NumInitCondBootstrapEM=10
ComputeAllSubHaplotypesEM=0
ComputeAllHaplotypesEM=1
ComputeAllAllelesEM=0
EpsilonValue=1.0e-7
FrequencyThreshold=1.0e-5
ComputeConventionalFST=0
IncludeIndividualLevel=0
ComputeDistanceMatrixAMOVA=0
DistanceMethodAMOVA=0
GammaAValueAMOVA=0.0
PrintDistanceMatrix=0
TestSignificancePairewiseFST=0
NumPermutationsFST=100
ComputePairwiseFST=0
TestSignificanceAMOVA=0
NumPermutationsAMOVA=1000
NumPermutPopDiff=10000
NumDememoPopDiff=1000
PrecProbPopDiff=0.0
PrintHistoPopDiff=1
SignLevelPopDiff=0.05
EwensWattersonHomozygosityTest=0
NumIterationsNeutralityTests=1000
NumSimulFuTest=1000
NumPermMantel=1000
NumBootExpDem=100
LocByLocAMOVA=0
PrintFstVals=0
PrintConcestryCoeff=0
PrintSlatkinsDist=0
PrintMissIntermatchs=0
UnequalPopSizeDiv=0
PrintMinSpannNetworkPop=0
PrintMinSpannNetworkGlob=0
KeepNullDistrib=0""")
        file.close()

    def runArlequin(self):
        """Run the Arlequin haplotyping program.

        Generates the expected '.txt' set-up files for Arlequin, then
        forks a copy of 'arlecore.exe', which must be on 'PATH' to
        actually generate the haplotype estimates from the generated
        '.arp' file.
        """
        # generate the `standard' run file
        self.batch._outputArlRunTxt(self.arlequinPrefix + ".txt", self.arpFilename)
        # generate a customized settings file for haplotype estimation
        self._outputArlRunArs(self.arlequinPrefix + ".ars")
        
        # spawn external Arlequin process
        self.batch.runArlequin()
        
    def genHaplotypes(self):
        """Gets the haplotype estimates back from Arlequin.

        Parses the Arlequin output nonsense to retrieve the haplotype
        estimated data.  Returns a list of the sliding `windows' which
        consists of tuples.

        Each tuple consists of a:

        - dictionary entry (the haplotype-frequency) key-value pairs.

        - population name (original '.arp' file prefix)

        - sample count (number of samples for that window)

        - ordered list of loci considered
        """
        outFile = self.batch.arlResPrefix + ".res" + os.sep + self.batch.arlResPrefix + ".htm"
        dataFound = 0
        headerFound = 0

        haplotypes = []
        
        patt1 = re.compile("== Sample :[\t ]*(\S+) pop with (\d+) individuals from loci \[([^]]+)\]")
        patt2 = re.compile("    #   Haplotype     Freq.      s.d.")
        patt3 = re.compile("^\s+\d+\s+UNKNOWN(.*)")
        windowRange = range(1, self.windowSize)
        
        for line in open(outFile, 'r').readlines():
            matchobj = re.search(patt1, line)
            if matchobj:
                headerFound = 1
                popName = matchobj.group(1)
                sampleCount = matchobj.group(2)
                liststr = matchobj.group(3)
                # convert into list of loci
                lociList = map(int, string.split(liststr, ','))
                freqs = {}
                
            if dataFound:
                if line != os.linesep:
                    if self.debug:
                        print string.rstrip(line)
                    matchobj = re.search(patt3, line)
                    if matchobj:
                        cols = string.split(matchobj.group(1))
                        haplotype = cols[2]
                        for i in windowRange:
                            haplotype = haplotype + "_" + cols[2+i]
                        freq = float(cols[0])*float(sampleCount)
                        freqs[haplotype] = freq
                    else:
                        sys.exit("Error: unknown output in arlequin line: %s" % line)
                else:
                    headerFound = 0
                    dataFound = 0
                    haplotypes.append((freqs, popName, sampleCount, lociList))
            if re.match(patt2, line):
                dataFound = 1

        return haplotypes

class Emhaplofreq(Haplo):
    """Haplotype estimation implemented via emhaplofreq.

    This is essentially a wrapper to a Python extension built on top
    of the 'emhaplofreq' command-line program.

    Will refuse to estimate haplotypes longer than that defined by
    'emhaplofreq'.
    
    """
    def __init__(self, locusData, debug=0):

        # import the Python-to-C module wrapper
        # lazy importation of module only upon instantiation of class
        # to save startup costs of invoking dynamic library loader
        import _Emhaplofreq

        # assign module to an instance variable so it is available to
        # other methods in class
        self._Emhaplofreq = _Emhaplofreq
        
        self.matrix = locusData
        
        rows, cols = self.matrix.shape
        self.totalNumIndiv = rows
        self.totalLociCount = cols / 2
        
        self.debug = debug

        # initialize flag
        self.maxLociExceeded = 0

        # create an in-memory file instance for the C program to write
        # to; this remains in effect until a call to 'serializeTo()'.
        
        import cStringIO
        self.fp = cStringIO.StringIO()

    def estHaplotypes(self, locusKeys=None,
                      permutationFlag=0, haploSuppressFlag=0):
        
        """Estimate haplotypes for listed groups in 'locusKeys'.

        Format of 'locusKeys' is a string consisting of:

        - comma (',') separated haplotypes blocks for which to estimate
          haplotypes

        - within each `block', each locus is separated by colons (':')

        e.g. '*DQA1:*DPB1,*DRB1:*DQB1', means to est. haplotypes for
         'DQA1' and 'DPB1' loci followed by est. of haplotypes for
         'DRB1' and 'DQB1' loci.
        """

        # if no locus list passed, assume calculation of entire data
        # set
        if locusKeys == None:
            # create key for entire matrix
            locusKeys = ':'.join(self.matrix.colList)

        for group in string.split(locusKeys, ','):
            
            # get the actual number of loci being estimated
            lociCount = len(string.split(group,':'))

            if self.debug:
                print "number of loci for haplotype est:", lociCount

                print lociCount, self._Emhaplofreq.MAX_LOCI

            if lociCount <= self._Emhaplofreq.MAX_LOCI:

                # filter-out all individual untyped at any position
                subMatrix = self.matrix.filterOut(group, '****')

                # calculate the new number of individuals emhaplofreq is
                # being run on
                groupNumIndiv = len(subMatrix)

                if self.debug:
                    print "debug: key for matrix:", group
                    print "debug: subMatrix:", subMatrix
                    print "debug: dump matrix in form for command-line input"
                    for line in range(0, len(subMatrix)):
                        theline = subMatrix[line]
                        print "dummyid",
                        for allele in range(0, len(theline)):
                            print theline[allele][:-1], " ",
                        print
                    
                self.fp.write(os.linesep)

                # if nothing left after filtering, simply continue
                if groupNumIndiv == 0:
                    self.fp.write("<group mode=\"no-data\" loci=\"%s\"/>%s" % (group, os.linesep))
                    continue
                
                if permutationFlag:
                    self.fp.write("<group mode=\"LD\" loci=\"%s\">%s" % (group, os.linesep))
                else:
                    self.fp.write("<group mode=\"haplo\" loci=\"%s\">%s" % (group, os.linesep))
                self.fp.write(os.linesep)

                self.fp.write("<individcount role=\"before-filtering\">%d</individcount>" % groupNumIndiv)
                self.fp.write(os.linesep)
                
                self.fp.write("<individcount role=\"after-filtering\">%d</individcount>" % self.totalNumIndiv)
                self.fp.write(os.linesep)
                
                # pass this submatrix to the SWIG-ed C function
                self._Emhaplofreq.main_proc(self.fp, subMatrix,
                                        lociCount, groupNumIndiv,
                                        permutationFlag, haploSuppressFlag)

                self.fp.write("</group>")

                if self.debug:
                    # in debug mode, print the in-memory file to sys.stdout
                    lines = string.split(self.fp.getvalue(), os.linesep)
                    for i in lines:
                        print "debug:", i

            else:
                self.fp.write("Couldn't estimate haplotypes for %s, num loci: %d exceeded max loci: %d" % (group, lociCount, self._Emhaplofreq.MAX_LOCI))
                self.fp.write(os.linesep)


    def estAllPairwise(self):
        """Estimate LD (linkage disequilibrium) in all pairwise loci.

        Estimate the LD for each pairwise set of loci.  
        """
        loci = self.matrix.colList
        li = []
        for i in loci:
            lociCopy = loci[:]
            indexRemoved = loci.index(i)
            del lociCopy[indexRemoved]
            for j in lociCopy:
                if ((i+':'+j) in li) or ((j+':'+i) in li):
                    pass
                else:
                    li.append(i+':'+j)

        if self.debug:
            print li, len(li)

        for pair in li:
            self.estHaplotypes(pair, permutationFlag=1,
                               haploSuppressFlag=1)
            
##             filename = string.join(string.split(pair,'*'),'')
##             # create stream to write to
##             stream = open(filename+'.haplo', 'w')

##             # create the in-memory file instance for the C program to write to
##             import cStringIO
##             self.fp = cStringIO.StringIO()

##             print "estimating haplos for", pair
##             self.estHaplotypes(pair)

##             self.serializeTo(stream)
            

    def serializeTo(self, stream):

        type = getStreamType(stream)

        if type == 'xml':
            # until we "XML-ify" simply pass output from emhaplofreq
            # to XML file as a CDATA (character data) section
            stream.opentag('emhaplofreq')
            stream.writeln()
            stream.write(self.fp.getvalue())
            #self.fp.close()
            stream.closetag('emhaplofreq')
            stream.writeln()
        
        else:
            # write complete contents of file pointer to text output
            # stream
            stream.write(self.fp.getvalue())
            #self.fp.close()

        
