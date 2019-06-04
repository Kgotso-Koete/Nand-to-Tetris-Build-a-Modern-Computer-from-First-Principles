Contents:
--------

LFSR32Rand.jack     LFSR-based random number generator.

Main.jack           Test program for LFSR32Rand -- presents side by side test
                    patterns drawn with LCGRand and LFSR32Rand.
LCGRand.jack        "Objectized" version of LCGRandom.jack.  (Used by Main, not
                    required by LFSR32Rand.)


LFSR32Rand uses a Linear Feedback Shift Register to implement a random number
generator with a cycle length of 2^32-1 (4.29e+9).

LFSR32Rand solves several problems that can occur when using LCG-based random
number generators like LCGRandom.

 1) Because Hack only supports 16-bit signed multiplication, the LCG has a
    cycle length of at most 32767 values before it repeats.
 2) LCGs have poor randomness in the lower bits of the generated numbers.
 3) LCGs can have noticeable patterns (autocorrelation) between returned values.
 4) The LCG's unscaled values are unique; there are no duplicate values in the
    series returned by rand().  True random values have randomly occurring
    duplicates.  (Search for "birthday problem" to learn about this.)


Test program notes:
------------------

The "mormal-ish" distribution is the sum of three uniformly distributed random
integers in the range 0-85 (3d86).

The number displayed at the end of the test is the number of black pixels at 
the end of the test.

Interesting tests to look at:

Uniform distribution, 16K, set pixels -- Beginning to see LCG patterning.
Uniform distribution, 32K, set pixels -- Strong patterning, overly dense.
Uniform distribution, 64K, XOR pixels -- Pixels turned off during 2nd LCG cycle.
Normal distribution, 16K, set pixels -- Diagonal patterning, low center density.
Random walk, 32K, set pixels -- LCG draws an interesting creature.
Random walk, 64K, XOR pixels -- The creature gets drawn and erased.

(See Nand2Tetris forum
    http://nand2tetris-questions-and-answers-forum.32033.n3.nabble.com/Pseudo-Random-Number-Generator-tp4026059p4029903.html
for information about why the LCG generates the creature.)


Expected Value Table:
--------------------

n(K)          set pixel               XOR pixel
         uniform      3d86       uniform      3d86
  1      1016.05     1002.95     1008.18      982.64
  2      2016.35     1965.24     1985.34     1888.10
  4      3970.65     3776.14     3850.40     3497.60
  8      7700.74     6995.09     7248.35     6078.50
 16     14496.61    12156.86    12893.35     9585.08
 32     25786.56    19170.01    20713.51    13458.44
 64     41426.84    26916.78    28333.47    17109.61
128     56666.80    34219.17    32167.87    20318.87
256     64335.70    40637.71    32757.01    23034.44
512     65514.02    46068.88    32768.00    25269.91
