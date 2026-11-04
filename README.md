<h1>
vdx
</h1>
Diff, Flatten, Slice.<br>
(delta-encode, linearize, ordinal-segment). <br>
A simple way to batch documents together, flatten the report to scrub fluff, and then slice into parts of a whole, which will lower overhead for your AI assistant.  <br>
Also helps with file size upload restrictions.

***
Optimized Text Data for Your AI Assistant
=========================================

Stop dumping massive unorganized data onto your AI workflow.

Diff, Flatten, Slice. Your AI does the rest.<br>
Use with any 1 or multiple text-based documents. <br>
Produce a 2-file report (dense/index) for your AI, and a readable diff for you.<br> 
Insight into any topic within the documents. <br>
Projects, Coding, Finance, Medical, and just about anything you can think of. 

__Run, Drag, Drop, Ask.__

## Quick Decision Matrix

| Your Goal | Use Mode |
| :--- | :--- |
| "I have many files with changes/edits." | **Mode 1** (Diff) |
| "I have noisy files (comments/blanks) and want clean text." | **Mode 2** (Flatten) |
| "My single file is too big for the AI context window." | **Mode 3** (Slice) |
| "I need to clean up deltas, then slice them." | **Mode 1 → 2 → 3** |

Repository Structure
====================
```
|-- vdx.py          # Anchor Edition: Standard script that outputs reports to user profile (~/.ssdx/vdx_reports/)
|-- vdx-p.py        # Portable Edition: Self-contained script that outputs reports directly to ./vdx_reports/
|-- run_vdx.bat     # Windows Launcher: Platform path-safe interactive menu wrapper
|-- run_vdx.sh      # MacOS\Linux Launcher: Platform path-safe interactive menu wrapper
```

__Whether 1 or all, you choose what's needed__


Key Features
============

Differential Comparison (Mode 1)
--------------------------------

Choose a 'ground truth' or 'original' file as the base to measure changes against.<br>
- This adds a time dimension to the delta<br>
Tracks line additions, deletions, modifications, and exact block movements/renames.<br>
Exports structured reports (index.tsv, dense.json, readable.md).<br>

Flatten Batch (Mode 2)
----------------------

Select and flatten multiple files simultaneously.<br>
Strips unnecessary comments and collapses blank lines to create clean text streams optimized for LLM ingest.<br>

Large Text Slicer (Mode 3)
----------------------------
Take massive text documents, logs, or source files and cleanly segment them into N equal chunks for easier processing or manual handling.<br>

Zero-Overhead Dispatcher (run_vdx.bat)
------------------------------------
Acts as a pure, lightweight dispatcher.<br>
Delegating path resolution and directory creation entirely to the underlying Python scripts.<br>
Styled with ANSI colors and clear visual status indicators.<br>


Example Workflows:
==================
- Workflow A: Diff Identification (Mode 1 only)
- Workflow B: Noise Reduction (Mode 2 only)
- Workflow C: Context Window Management (Mode 3 only)
- Workflow D: Full Analysis Pipeline (Mode 1 → 2 → 3)

Example Workflow D:
===================

- __Diff mode [1]__
- Navigate to a directory with many text-based files.
- Choosing the oldest file first helps, but is not required.
- Select all files relevant to your batch.
- Output the delta report for AI, the diff report for you.
- __Flat mode [2]__
- Navigate to the delta output directory.
- Select the dense delta report generated from [1].
- Output the flattened delta for AI, the diff for you.
- __Slice mode [3]__
- Navigate to the flat delta.
- Select the dense flat delta.
- Choose the number of slices (# slices ≤ # lines).
- Feed your AI assistant pre-sliced flattened deltas with the index created in Mode [1]
- Lowers AI overhead, makes data easier to see, get better answers.



Usage Quick Start (Windows)
===========================

Double-click run_vdx.bat, run_vdx.sh, or launch from your terminal. You will be greeted by the interactive runner menu:

```
=====================================================================
                        VDX REPORT RUNNER
=====================================================================

  [1] Run vdx.py      (Saves to: C:\Users\YourName\.ssdx\vdx_reports)
  [2] Run vdx-p.py       (Saves to: C:\path\to\script\vdx_reports)
  [3] Exit
=====================================================================
```


Manual Execution (Python)
=========================

If you prefer running the scripts directly via command line:

Anchor Edition: python vdx.py
Portable Edition: python vdx-p.py

Output Architecture
-------------------

vdx.py <br>
-outputs generated report packages to: %USERPROFILE%\.ssdx\vdx_reports\

vdx-p.py <br>
-keeps everything local, outputting report packages directly to: ./vdx_reports/


## Credits
- [s.KiNG](https://github.com/seancking215-hub) - author

## License
Apache-2.0
