<h1>
vdx
</h1>
Aggregate, delta-encode, linearize, ordinal-segment. <br>
A simple way to batch documents together, flatten the report to scrub fluff, and then slice into parts of a whole, which will lower overhead for your AI assistant.  <br>
Also helps with file size upload restrictions.

***
VDX - Optimized Text Data for Your AI Assistant
=======================================================

Stop data dumping massive unorganized data onto your AI.

Flatten, Compress, Diff, Version, Summarize, and Split.<br>
Use on any 1 or multiple text based documents. <br>
Produce a 2 file report (dense/index) you can give to your AI assistant,<br> 
providing instant sight into whatever the documents relate to. <br>
Projects, Coding, Finance, Medical, and just about anything you can think of. 

__Run, Drag, Drop, Ask.__

Repository Structure
====================
```
|-- vdx.py          # Anchor Edition: Standard script that outputs reports to user profile (~/.ssdx/)
|-- vdx-p.py        # Portable Edition: Self-contained script that outputs reports directly to ./vdx_reports/
|-- run_vdx.bat     # Windows Launcher: Platform path-safe interactive menu wrapper
|-- run_vdx.sh      # MacOS\Linux Launcher: Platform path-safe interactive menu wrapper
```

__Whether 1 or all, you choose what's needed__

Example Flow- for many files
===========================

- __Diff mode [1]__
- Navigate to a directory with many text based files.
- Choosing the oldest file first helps, but is not required.
- Select all files relevant to your batch.
- Output diff report, back out.
- __Flat mode [2]__
- Navigate to the diff output directory.
- Select the dense diff report generated from [1].
- Output flattened diff, back out.
- __Split mode [3]__
- Navigate to the flattened diff.
- Selected the dense flat diff.
- Choose the amount to split them into.
- Feed you AI assistant pre-sliced flattened diffs with the index created in mode [1]
- Lowers AI overhead, makes data easier to see, get better answers.


Key Features
============

Differential Comparison (Mode 1)
--------------------------------

Compare multiple target files against a single reference base file.<br>
Tracks line additions, deletions, modifications, and exact block movements/renames.<br>
Exports structured reports (index.tsv, dense.json, readable.md).<br>

Flat Batch Compression (Mode 2)
-------------------------------

Select and compress multiple files simultaneously.<br>
Strips unnecessary comments and collapses blank lines to create pristine text streams optimized for LLM ingest.<br>

Large Text Splitter (Mode 3)
----------------------------
Take massive text documents, logs, or source files and cleanly segment them into $N$ equal chunks for easier processing or manual handling.<br>

Zero-Overhead Launcher (run_vdx.bat)
------------------------------------

Acts as a pure, lightweight "Captain/Ship" router.<br>
Delegating pathing and directory creation entirely to the underlying Python scripts.<br>
Styled with ANSI colors and clear visual status indicators.<br>



UsageQuick Start (Windows)
==========================

Double-click run_vdx.bat, run_vdx.sh or launch it from your command line terminal. You will be greeted by the interactive runner menu:

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

Global Edition: python vdx.py
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
