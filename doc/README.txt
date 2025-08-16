Result without labels file annotating 3 trills:

midi_score = ../../asap-dataset-master/Bach/Fugue/bwv_846/midi_score.mid 
Large Gaps Between Matches 
--------------------------
5.8125 from unmatched pitch 71 at score time 25.5938 to 45 at 28.5
1.33542 from unmatched pitch 79 at score time 35.8323 to 77 at 36.5
4.5625 from unmatched pitch 76 at score time 36.5938 to 62 at 38.875
--------------------------
gap histogram data: [635, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0]
Gap in beats between next possible match beat and next actual match beat:
Labels at left are lower boundaries for bins.
      0.0       200       400       600       800       1000      1200   
       |         |         |         |         |         |         |
       |********************************
   1   | (1)
   2   | (0)
   3   | (0)
   4   | (1)
   5   | (1)
   6   | (0)
   7   | (0)
   8   | (0)
   9   | (0)
   10  | (0)
   11  | (0)



midi_score = ../../asap-dataset-master/Bach/Fugue/bwv_846/midi_score.mid 
Large Gaps Between Matches  (none)
gap histogram data: [698, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
Gap in beats between next possible match beat and next actual match beat:
Labels at left are lower boundaries for bins.
      0.0       200       400       600       800       1000      1200   
       |         |         |         |         |         |         |
       |***********************************
   1   | (0)
   2   | (0)
   3   | (0)
   4   | (0)
   5   | (0)
   6   | (0)
   7   | (0)
   8   | (0)
   9   | (0)
   10  | (0)
   11  | (0)

Matched 92.71% of notes.

Changing epsilon to 50 msec (or 25 msec) because the performance is so fast
that some sixteenths were grouped into chords improved alignment error and
matched more notes:

test result: test_no = 1, result.total_count = 754, result.matched_count = 711,
    result.matched_pct() = 94.2971

Timing errors are:
Large Errors In Estimated Score Time for Match
----------------------------------------------
score time 25.5 beat 50 performance time 63.6289 beat 50.1388
score time 25.5 beat 50 performance time 63.7266 beat 50.1986
score time 25.75 beat 50.5 performance time 63.819 beat 50.2553
score time 25.75 beat 50.5 performance time 63.9049 beat 50.3079
score time 36.5 beat 72 performance time 92.8333 beat 72.1548
score time 36.75 beat 72.5 performance time 93.0521 beat 72.273
----------------------------------------------

error histogram data: [0, 0, 0, 0, 0, 3, 7, 34, 58, 90, 66, 104, 114, 65, 79, 42, 31, 15, 3, 0, 0, 0, 0, 0]

Alignment Error Histogram: estimated position - correct position in millibeats:
Labels at left are lower boundaries for bins.
      0.0        20        40        60        80       100       120    
       |         |         |         |         |         |         |
       | (0)
 -4096 | (0)
 -2048 | (0)
 -1024 | (0)
  -512 | (0)
  -256 |**
  -128 |****
  -64  |*****************
  -32  |*****************************
  -16  |*********************************************
   -8  |*********************************
   -4  |****************************************************
   0   |*********************************************************
   4   |*********************************
   8   |****************************************
   16  |*********************
   32  |****************
   64  |********
  128  |**
  256  | (0)
  512  | (0)
  1024 | (0)
  2048 | (0)
  4096 | (0)

Stop reporting grace notes and trill notes since the Cevent time is not correct for
grace and trill notes: better. It seems that these are all distortions within beats
where the quarter is not subdivided accurately. The maximum error was about 0.15 beats
which was about 180 msec, and the maximum time error in the ritard at the end was
0.12 beats and 353 msec.

test result: test_no = 1, result.total_count = 754, result.matched_count = 704,
    result.matched_pct() = 93.3687

Large Errors In Estimated Score Time for Match
----------------------------------------------
score time 35.9375 beat 70.875 performance time 90.8958 beat 70.7241
----------------------------------------------

error histogram data: [0, 0, 0, 0, 0, 1, 7, 34, 58, 90, 66, 105, 114, 65, 79, 42, 31, 12, 0, 0, 0, 0, 0, 0]

Alignment Error Histogram: estimated position - correct position in millibeats:
Labels at left are lower boundaries for bins.
      0.0        20        40        60        80       100       120    
       |         |         |         |         |         |         |
       | (0)
 -4096 | (0)
 -2048 | (0)
 -1024 | (0)
  -512 | (0)
  -256 |*
  -128 |****
  -64  |*****************
  -32  |*****************************
  -16  |*********************************************
   -8  |*********************************
   -4  |*****************************************************
   0   |*********************************************************
   4   |*********************************
   8   |****************************************
   16  |*********************
   32  |****************
   64  |******
  128  | (0)
  256  | (0)
  512  | (0)
  1024 | (0)
  2048 | (0)
  4096 | (0)

-------------------------------------
