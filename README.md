# vdx  


Diff, Flatten, Slice.<br>
(delta-encode, linearize, ordinal-segment). <br>
A simple way to batch documents together, flatten the report to scrub fluff, and then slice into parts of a whole, which will lower overhead for your AI assistant.  <br>
Also helps with file size upload restrictions.

***
Optimized Text Data for Your AI Assistant
=========================================

Stop dumping massive unorganized data onto your AI context budget.<br>
Your AI receives a compact structured report instead of raw file contents.<br>

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
| "I forgot where I was, what I was doing." | **Mode 1** (Diff) |
| "I want to know why/when something was done." | **Mode 1** (Diff) |
| "I have an 8gb 3060ti, and need every advantage I can take." | **Mode 1** (Diff) |
| "I have noisy files (comments/blanks) and want clean text." | **Mode 2** (Flatten) |
| "I have files I want to put in storage." | **Mode 2** (Flatten) |
| "My single file is too big for the AI context window." | **Mode 3** (Slice) |
| "I only have access to my a 128 MB usb drive." | **Mode 3** (Slice) |
| "I need to clean signal reports under a certain size." | **Mode 1 → 2 → 3** |
| "I have a large Home Assistant log, and my AI is on a Raspberry Pi." | **Mode 1 → 2 → 3** |
| "I need to undo slices I created already." | **Mode 4** ( Reconstruction) |

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
- This Mode includes Mode 2.<br>

Choose individual files, or whole directories, no specific order necessary.<br>
- Automatically organizes you files chronologically, comparing them in order.<br>
- Options to choose entire directories and nested files added.<br>
Tracks when line additions, deletions, modifications, and exact block movements/renames occur.<br>
- Shows where you were, where you are, and where you were headed.<br>
Exports structured reports (index.tsv, dense.json, readable.md).<br>
- Index file provides featherweight meta-data.<br>
- Dense file provides the raw data.<br>
- Readable file is for user review.<br>
Go to your AI Assistant of choice<br>
- Upload index for high signal, small footprint.<br>
- Upload index and dense for added insight and tuned inference.<br>
- Query.<br>

Flatten Batch (Mode 2)
----------------------
- This Mode is included in Mode 1.<br>

Select multiple files and flatten them into a single clean text stream.<br>
- Options to choose entire directories and nested files added.<br>
Strips unnecessary comments and collapses blank lines.<br>
Produces a 2-file report for your AI, and a single, clean readable for you.<br>
- Use for uploading an efficient scrubbed doc, quickly.<br>
Put them in storage.<br>
- Can be Diff'd the same at a later date.<br>

Large Text Slicer (Mode 3)
--------------------------

Take massive text documents, logs, or source files and cleanly segment them into slices for easier processing or manual handling.<br>
- If either Mode 1 or 2 produce larger files, slice them down.<br>
Comes with its own ledger to aid the AI and/or manual locating of data.<br>
- MD5 and SHA256 used for improved recovery.<br>
If needed, slices can be reversed back into the original.<br>

Reconstruction (Mode 4)
-----------------------

Undo sliced files to put back together<br>
- If the original whole file is gone, put back slices from Mode 3.<br>
- MD5 and SHA256 improve recovery confidence.<br>


Zero-Overhead Dispatcher (run_vdx.bat)
------------------------------------
Acts as a pure, featherweight dispatcher.<br>
Only requires having python, and a resource budget.<br>
Styled with ANSI colors and clear visual status indicators.<br>
Put the portable script on that usb drive, and keep it mobile.<br>
Keep a copy in Home Assistant for convenience without strain.<br>


Example Workflows:
==================
- Workflow A: Difference, Inference & Trajectory (Mode 1 only)
- Workflow B: Noise Reduction (Mode 2 only)
- Workflow C: Context Window Management (Mode 3 only)
- Workflow D: Inference & Analysis, Scoped (Mode 1 → 2 → 3)
- Workflow E: Scrub and Slice (Mode 2 and 3)
- Workflow F: Ooops (Mode 4)

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
- Choose number of slices (must not exceed total line count).
- Feed your AI assistant pre-sliced flattened deltas with the index created in Mode [1]
- Lowers AI overhead, makes data easier to see, get better answers.



Usage Quick Start 
=================

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
VDX menu
========
```
  ======================================================
  ======================================================
                     -- vdx --
                 Diff, Flatten, Slice
  ======================================================
  ======================================================

            Recent Reports:
            • flat_scan_20261011_121413
            • split_filename_20261028_121406
            • diff_scan_20261009_140540

  ++++++++++++++++++++++++++++++++++++++++++++++++++++++

  [1] Diff & Comparison Mode (Compare target files against ground truth)
  [2] Flatten Mode           (Reduce noise in 1 or more files)
  [3] Slice Mode             (Slice a text file into smaller files)
  [4] Reconstruct Mode       (Rebuild sliced files from past jobs)

  >>  Select mode [1 - 4]:

============================================================
```
Diff Menu [1]
=============
```
============================================================
 CURRENT DIRECTORY : C:\VDX Video Demo\vdx development files\duplicate older
 FILE/DIR MODE     : DIRECTORY +RECURSIVE # Shows Selection and Recursive modes
 SELECTIONS        : []
============================================================

 Directories: # Directories up top
  [1] newer old vers
  [2] older_v
-----------------------------

 Files (Text Docs): # Files down low
  (No compatible text/artifact files)
============================================================

  [R]  Recursive Mode ...                    (ON) # Shows Recursive mode
  [F]  File/Dir Mode ...               (File <-> Directory)
  [B]  Back ...                        (^ Move directory ^)
  [D]  Done ...                         (Move to next step)
  [Q]  Quit ...                        (Exit to Runner/CLI)
============================================================
 >> Input Option or Select Docs [DIRECTORY mode]: 1 # Shows Selection mode

  [LAYER SELECTION LOCK]
  Target Folder : newer old vers/ 
  Total Assets  : 15 tracking files available
  Visual Anchor : Oldest found is Script Comparitor AI Inspector-last.py (2026-10-20 16:57)

  >> Track full folder containing Script Comparitor AI Inspector-last.py? [Y/n]:
  # Confirms 1 file in directory for ID/verification
```

Manual Execution (Python)
=========================

If you prefer running the scripts directly via command line:

Anchor Edition: python vdx.py<br>
Portable Edition: python vdx-p.py<br>

Output Architecture
-------------------

vdx.py <br>
-outputs generated report packages to: %USERPROFILE%\.ssdx\vdx_reports\ <br>

vdx-p.py <br>
-keeps everything local, outputting report packages directly to: ./vdx_reports/ <br>


## Credits
- [https://github.com/lonerTools/vdx](https://github.com/lonerTools/vdx)
- [s.KiNG](https://github.com/seancking215-hub) - author

## License
Apache-2.0
