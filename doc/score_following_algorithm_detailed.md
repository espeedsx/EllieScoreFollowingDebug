
# Score Following Algorithm (Dannenberg, 1985)

## Context
Previous work in this area has concentrated on computer input devices, including the sequential drum, sonar sensors for conducting, pitch detection, and others. 
Some researchers considered the problem of following a melodic line in order to produce a transcription, but their algorithms often require knowledge of the future and cannot be realized in real-time.

Two related problems from outside music are:  
- **Diff algorithms** for file comparison (too slow for real-time use in music).  
- **Dynamic programming for speech recognition** (time-warping), which motivated the algorithm here.  

This paper describes an on-line algorithm suitable for **real-time score following and accompaniment**.

---

## The Model
A solo performance is treated as a stream of events (e.g., notes played, pitches sounded, valve positions).  
The score is an ordered list of expected events (not a conventional score, but the exact sequence of events expected in a correct performance).  

**Goal**: Find the “best” match between the two streams.  
- “Best” is defined as the **longest common subsequence** of the performance and the score.  
- Extra notes in performance → unmatched events.  
- Missing notes in performance → skipped score events.  

**Example**:  
```
performance: A G E D G B C
best match:  A G E   G B C
score:       A G E G A B C
```  

---

## The Algorithm
To compute the best match, construct an integer matrix:  
- Rows = score events.  
- Columns = performance events.  
- Each cell stores the length of the best match up to that point.  

**Pseudocode (Figure 3-1):**
```
forall i, bestlength[i, -1] <- 0;
forall j, bestlength[-1, j] <- 0;

for each new performance event p[c] do
begin
  for each score event s[r] do
  begin
    bestlength[r, c] <- max(bestlength[r - 1, c], bestlength[r, c - 1]);
    if p[c] matches s[r] then
      bestlength[r, c] <- max(bestlength[r, c],
                               1 + bestlength[r - 1, c - 1]);
  end
end
```

- Each new performance event extends the computation by one column.  
- The maximum values indicate the best alignment up to that point.  
- When a match increases the maximum, the algorithm reports that the performer is at the corresponding score position.  

---

## Efficiency Improvements
- **Space optimization**: Only keep the current and previous columns, not the entire matrix.  
- **Time optimization (windowing)**: Assume the performance is close to the score.  
  - Only compute values for a **window of score events** around the expected match.  
  - If no match is found, slide the window down by one row.  
  - Window size must tolerate expected error rates.  

---

## Example (Windowed Computation)
Using a window size of 3, the algorithm computes only around the likely current score location.  
This makes real-time tracking feasible on limited computers.  

---

## Heuristics
The raw algorithm can make mistakes, such as “jumping ahead” when a wrong event coincidentally matches a future score event.  
Three heuristics mitigate this:

1. **Limit skipping rate**: Restrict how quickly the score position can advance (≤ 2 rows per detected event).  
2. **Penalty for skipping**: Deduct points for skipped events by adjusting recurrence:  
   ```
   bestlength[r, c] <- max(bestlength[r - 1, c] - 1,
                           bestlength[r, c - 1]);
   ```  
3. **Earliest match preference**: If multiple matches tie for best score, choose the earliest score position.  

---

## Application to Accompaniment
The algorithm reports the soloist’s current location in the score.  
To synchronize accompaniment, a **virtual clock** is used:  

```
VirtualTime = (R - Rref) * S + Vref
```
- `R` = current real time.  
- `Rref` = last reset time.  
- `Vref` = virtual score time at last reset.  
- `S` = speed of virtual clock.  

Whenever a new match is reported, the virtual clock is reset to the matching score location.  
The speed `S` is slightly adjusted (increased if catching up, decreased if behind).  

This allows accompaniment to stay aligned with the soloist without rigid tempo assumptions.  

---

## Limitations
- Tempo following is mechanical (not musically expressive).  
- Only temporal matching: ignores dynamics, articulation, and expressive nuance.  
- Requires events to be totally ordered. Cannot handle unordered/simultaneous polyphonic events (e.g., chords).  
- Assumes relatively clean input; multiple sensors or microsecond-level simultaneous events are not well supported.  

---

## Conclusions
- The algorithm is tolerant of **wrong notes, missing notes, ornamentation, and slurs**.  
- It does not require steady tempo and does not rely on timing.  
- Works robustly for **monophonic input** (e.g., trumpet, single-line keyboard).  
- Provides a solid foundation for real-time computer accompaniment.  

