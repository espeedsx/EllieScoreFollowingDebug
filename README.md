# Score Following

Evaluation of various score following algorithms, particularly for
**Accomplice**.

---

## Installation

1. **Download and install Serpent**
   - From: [Serpent Installation (Windows)](https://www.cs.cmu.edu/~music/cmp/serpent/doc/installation-win.htm)

2. **Clone this project**

3. **Download the ASAP dataset**
   - Repository: [ASAP Dataset on GitHub](https://github.com/fosfrancesco/asap-dataset)
   - Ensure that the metadata file is located in the directory
     containing this repo. Relative to this README.md file, it should be:
     
     ```
     ../asap-dataset-master/metadata.csv
     ```

---

## Usage

### Run a Single Test from ASAP Repertoire

1. Update the following configurations in `run_bench.srp`:
   - Set the version of `score_follower`  
     *(v17: `score_follower_v17`, v18: `score_follower`)*
   - Set the **strategy**: `static` or `dynamic`

2. Execute: run_bench.srp STARTNO
   - where STARTNO is an integer ID of the test  
     *(ID = line number in `metadata.csv`)*

---

### Run a Suite of Tests from ASAP Repertoire

1. Update the following configurations in `run_bench.srp`:
   - Set the version of `score_follower`  
     *(v17: `score_follower_v17`, v18: `score_follower`)*
   - Set the **strategy**: `static` or `dynamic`

2. Execute: `serpent64 run_bench.srp STARTNO ENDNO`
   - where STARTNO is an integer ID of the first test and
     ENDNO is the ID of the last test.
     *(ID = line number in `metadata.csv`)*

---

### Run Your Own Test

1. Update the following configurations in `run_test.srp`:
- Set the version of `score_follower`  
  *(v17: `score_follower_v17`, v18: `score_follower`)*
- Set the **strategy**: `static` or `dynamic`

2. Copy both MIDI files to the `tests/midi` folder.

3. Execute: `serpent64 run_test.srp MIDI_SCORE MIDI_PERF`
   - where MIDI_SCORE is the file name of the score and
     MIDI_PERF is the file name of the performance. 


### Output Reporting
Attributes:
- note_count - number of performed notes
- matched_count - number of reported matches using the algorithm's
    model of confidence. These are not necessarily correct matches.
- matched-perc - percent of performed notes that are reported as
    matches

`tests/bench_result.csv` will contain a CSV file with:
    - no: number of the score (from
      `asap-dataset-master/metadata.csv`),
    - composer - from `metadata.csv`,
    - title - from `metadata.csv`,
    - note_count - number of notes in score
    - matched_count - number of confident matches
    - matched_pct - percent of performed notes matched,
    - midi_score - from `metadata.csv`,
    - midi_performance - from `metadata.csv 

---

### Serpent Version

The test bench was tested with **Serpent for Windows v418**.

---

### Score Follower Versions

- **`score_follower_v17_original_from_box.srp`**  
  Version 17, downloaded from Box.

- **`score_follower_v17.srp`**  
  Version 17, updated to run with the test bench.

- **`score_follower_original_from_sourceforge_r613.srp`**  
  Version 18, downloaded from SourceForge (r613).

- **`score_follower.srp`**  
  Version 18, updated to run with the test bench.

---

### Logging

Both `run_bench.srp` and `run_test.srp` support various logging levels.  
You can enable verbose logging by adjusting the log level settings within the scripts.

---

