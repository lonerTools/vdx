#!/usr/bin/env python3
"""
vdx - tool to optimize text for AI assistant. Now with text split & reconstruction!
Assumes nothing, depends on nothing, leaves nothing behind. 
It does what it does, you do what you do.

Copyright (c) 2026 [s.KiNG]
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0

Official Repository: https://github.com/lonerTools/vdx
"""
__author__ = "s.KiNG"
__licence__ = "Apache-2.0"

import os
import sys
import json
import hashlib
import difflib
import re
from datetime import datetime, timezone
from pathlib import Path
import argparse

# -- Global .vdx Zero-Footprint Configuration --

if os.name == 'nt':
    os.system('')  # Triggers Windows console to interpret ANSI codes

CONFIG_DIR = Path(__file__).parent
CONFIG_DIR.mkdir(exist_ok=True, parents=True)
OUTPUT_DIR = CONFIG_DIR / "vdx_reports"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

RST = "\033[0m"
BLD = "\033[1m"
RED = "\033[91m"
MAG = "\033[95m"
GRN = "\033[32m"
CYN = "\033[36m"
BLU = "\033[94m"
GRY = "\033[38;5;242m" 
CLS = "\033[H\033[J"

# Protocol Tethering Constants
PROTOCOL_HEADER_TSV = "# PROTOCOL: MAP-DESTINATION\tUSE_TSV_AS_MAP\tFIND_PTR\n"
PROTOCOL_META_JSON = {
    "protocol": "MAP-DESTINATION-v1.0",
    "rule": "AI-ONLY: Search TSV map first. Extract JSON_PTR (e.g., e[idx]), then fetch target JSON node only. Zero human comfort padding."
}

# -- JSON & JSONL Variant Parser --

def load_json_variant(file_path: Path):
    """
    Parses JSON, JSONL, NDJSON, and JSONC (with inline comments/trailing commas).
    Returns (data, variant_type).
    """
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Strip single-line comments for JSONC compatibility
    clean_content = re.sub(r'^\s*//.*$', '', content, flags=re.MULTILINE)

    # 1. Standard JSON attempt
    try:
        return json.loads(clean_content), "json"
    except json.JSONDecodeError:
        pass

    # 2. JSONL / NDJSON attempt (line-delimited JSON objects)
    jsonl_items = []
    is_jsonl = True
    for line in clean_content.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            jsonl_items.append(json.loads(line))
        except json.JSONDecodeError:
            is_jsonl = False
            break
            
    if is_jsonl and jsonl_items:
        return jsonl_items, "jsonl"

    # 3. Concatenated JSON objects
    decoder = json.JSONDecoder()
    pos = 0
    concat_items = []
    str_len = len(clean_content)
    while pos < str_len:
        while pos < str_len and clean_content[pos].isspace():
            pos += 1
        if pos >= str_len:
            break
        try:
            obj, end_pos = decoder.raw_decode(clean_content, pos)
            concat_items.append(obj)
            pos = end_pos
        except json.JSONDecodeError:
            concat_items = []
            break

    if concat_items:
        return concat_items, "json_concat"

    raise ValueError(f"Unable to parse '{file_path.name}' as any valid JSON/JSONL variant.")

# -- Universal Text & Structural Normalization --

def universal_normalize(src: str, path: str, strip_comments: bool = True, collapse_blank_lines: bool = True) -> str:
    """
    Universally normalizes any text document, script, or configuration file.
    Handles code comments selectively and cleans whitespace.
    """
    lines = src.splitlines()
    cleaned_lines = []
    
    is_code = path.endswith(('.py', '.sh', '.pl', '.rb', '.js', '.ts', '.c', '.cpp', '.java'))
    last_was_blank = False
    
    for line in lines:
        stripped = line.strip()
        if strip_comments and is_code and stripped.startswith(('#', '//')) and not stripped.startswith('#!'):
            continue
            
        if not stripped:
            if collapse_blank_lines:
                if not last_was_blank:
                    cleaned_lines.append("")
                    last_was_blank = True
            else:
                cleaned_lines.append("")
            continue
            
        last_was_blank = False
        cleaned_lines.append(line.rstrip())
            
    return '\n'.join(cleaned_lines).strip()

# -- Diff Engine --

def hash_block(block: str) -> str:
    return hashlib.md5(block.encode()).hexdigest()

def find_moves(deleted_blocks, inserted_blocks):
    pure_moves = []
    moved_with_changes = []
    remaining_deleted = list(deleted_blocks)
    remaining_inserted = list(inserted_blocks)

    for d in list(remaining_deleted):
        for i in list(remaining_inserted):
            if hash_block(d['code']) == hash_block(i['code']):
                pure_moves.append({
                    "from_line": d['line'],
                    "to_line": i['line'],
                    "lines": len(d['code'].splitlines()),
                    "content_hash": hash_block(d['code'])
                })
                remaining_deleted.remove(d)
                remaining_inserted.remove(i)
                break

    for d in list(remaining_deleted):
        best_ratio = 0
        best_i = None
        for i in remaining_inserted:
            sm = difflib.SequenceMatcher(None, d['code'], i['code'])
            ratio = sm.ratio()
            if ratio > 0.75 and ratio > best_ratio:
                best_ratio = ratio
                best_i = i
        if best_i is not None:
            moved_with_changes.append({
                "from_line": d['line'],
                "to_line": best_i['line'],
                "similarity": round(best_ratio, 3),
                "before_snippet": d['code'][:100],
                "after_snippet": best_i['code'][:100]
            })
            remaining_deleted.remove(d)
            remaining_inserted.remove(best_i)

    return pure_moves, moved_with_changes, remaining_deleted, remaining_inserted

def compute_diff(base_src: str, target_src: str):
    base_lines = base_src.splitlines()
    target_lines = target_src.splitlines()

    sm = difflib.SequenceMatcher(None, base_lines, target_lines)
    deleted_blocks = []
    inserted_blocks = []
    modified_pairs = []

    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'delete':
            deleted_blocks.append({
                'line': i1 + 1,
                'code': '\n'.join(base_lines[i1:i2]),
                'lines': i2 - i1
            })
        elif op == 'insert':
            inserted_blocks.append({
                'line': j1 + 1,
                'code': '\n'.join(target_lines[j1:j2]),
                'lines': j2 - j1
            })
        elif op == 'replace':
            modified_pairs.append({
                'line': i1 + 1,
                'before': '\n'.join(base_lines[i1:i2]),
                'after': '\n'.join(target_lines[j1:j2])
            })

    pure_moves, moved_with_changes, remaining_deleted, remaining_inserted = \
        find_moves(deleted_blocks, inserted_blocks)

    return {
        'pure_moves': pure_moves,
        'moved_with_changes': moved_with_changes,
        'added': remaining_inserted,
        'deleted': remaining_deleted,
        'modified': modified_pairs
    }

# -- Report Writers --

def write_batch_report(comparisons, outdir, tsv_only=False):
    os.makedirs(outdir, exist_ok=True)
    
    # The Index structure remains flat and strict
    idx_lines = [
        PROTOCOL_HEADER_TSV.strip(), 
        "target_file\tbase_file\tadded_blocks\tmodified_changes\tdeleted_blocks\tnet_lines\tdensity_delta\ttime_gap\tjson_ptr"
    ]
    
    meta_block = dict(PROTOCOL_META_JSON)
    meta_block["ts"] = datetime.now(timezone.utc).isoformat()
    batch_dense = {"_meta": meta_block, "comparisons": []}
    
    md = ["# VDX Multi-File Chronological Delta Report", f"**Timestamp:** {datetime.now().isoformat()}\n"]

    for comp in comparisons:
        base_name = comp['base']
        target_name = comp['target']
        diff = comp['diff']
        time_gap = comp.get('time_gap', 'N/A')
        density_delta = comp.get('density_delta', '+0.000')
        
        total_added = sum(a['lines'] for a in diff['added'])
        total_deleted = sum(d['lines'] for d in diff['deleted'])
        net = total_added - total_deleted
        
        counts = {
            'added': len(diff['added']),
            'modified': len(diff['modified']),
            'deleted': len(diff['deleted']),
            'moved': len(diff['pure_moves'])
        }
        
        json_ptr = ""

        if not tsv_only:
            json_ptr = f"/comparisons/{len(batch_dense['comparisons'])}"
            batch_dense["comparisons"].append({
                "base": base_name,
                "target": target_name,
                "metrics": counts,
                "diff": diff,
            })

            md.append(
                f"## Delta: `{base_name}` ➔ `{target_name}` *({time_gap})*"
            )
            md.append(
                f"- **Net Lines:** {net:+d} "
                f"(+{total_added} / -{total_deleted}) | "
                f"**Density Shift:** {density_delta}"
            )
            md.append(
                f"- **Added Blocks:** {counts['added']} | "
                f"**Modified:** {counts['modified']} | "
                f"**Deleted:** {counts['deleted']}\n"
            )

        idx_lines.append(
            f"{target_name}\t{base_name}\t"
            f"{counts['added']}\t{counts['modified']}\t"
            f"{counts['deleted']}\t{net:+d}\t"
            f"{density_delta}\t{time_gap}\t{json_ptr}"
        )

    # Save out the maps matching user parameters
    with open(outdir / "index.tsv", "w", encoding='utf-8') as f:
        f.write('\n'.join(idx_lines) + '\n')
        
    if not tsv_only:
        with open(outdir / "dense.json", "w", encoding="utf-8") as f:
            json.dump(batch_dense, f, indent=2)

        dense_hash = hashlib.sha256(
            (outdir / "dense.json").read_bytes()
        ).hexdigest()
        idx_lines.insert(1, f"# DENSE_SHA256\t{dense_hash}")

        with open(outdir / "readable.md", "w", encoding="utf-8") as f:
            f.write('\n'.join(md))

    with open(outdir / "index.tsv", "w", encoding="utf-8") as f:
        f.write('\n'.join(idx_lines) + '\n')

    return outdir

def write_flat_batch_report(file_records, outdir):
    os.makedirs(outdir, exist_ok=True)

    json_ptr = f"/files/{len(flat_dense['files'])}"

    idx_lines = [
        PROTOCOL_HEADER_TSV.strip(),
        "file_name\torigin_layer\traw_lines\tclean_lines\t"
        "timestamp\tjson_ptr"
    ]

    meta_block = dict(PROTOCOL_META_JSON)
    meta_block["ts"] = datetime.now(timezone.utc).isoformat()


    md = [
        "# VDX Flat Batch AI Ingest Report",
        f"**Timestamp:** {datetime.now().isoformat()}\n",
        "## Structural Layer Breakdown",
        "This package contains noise-reduced structural text assets grouped by origin layers:\n"
    ]

    # Group files by their parent directories for cleaner macro context mapping
    grouped_by_layer = {}
    for rec in file_records:
        layer = rec.get("origin_layer", "Root")
        if layer not in grouped_by_layer:
            grouped_by_layer[layer] = []
        grouped_by_layer[layer].append(rec)

    for layer, records in sorted(grouped_by_layer.items()):
        md.append(f"###  Layer Archive: `{layer}`")
        
        for rec in records:
            fname = rec['name']
            src = rec['src']
            clean = rec['clean']
            raw_count = len(src.splitlines())
            clean_count = len(clean.splitlines())

            idx_lines.append(f"{fname}\t{layer}\t{raw_count}\t{clean_count}\t{datetime.now().isoformat()}\t{json_ptr}")

            flat_dense["files"].append({
                "file": fname,
                "origin_layer": layer,
                "raw_lines": raw_count,
                "clean_lines": clean_count,
                "content": clean
            })

            md.append(f"####  File: `{fname}` ({clean_count} clean lines / {raw_count} raw lines)")
            md.append("```python" if fname.endswith('.py') else "```text")
            md.append(clean)
            md.append("```\n")

    with open(outdir / "dense.json", "w", encoding="utf-8") as f:
        json.dump(flat_dense, f, indent=2)

    dense_hash = hashlib.sha256(
        (outdir / "dense.json").read_bytes()
    ).hexdigest()
    idx_lines.insert(1, f"# DENSE_SHA256\t{dense_hash}")

    with open(outdir / "index.tsv", "w", encoding="utf-8") as f:
        f.write('\n'.join(idx_lines) + '\n')

    with open(outdir / "readable.md", "w", encoding="utf-8") as f:
        f.write('\n'.join(md))

    return outdir


def interactive_file_selector(start_path: Path, single_select: bool = False):
    current = start_path.resolve()
    selected_files = []
    valid_extensions = ('.py', '.sh', '.json', '.jsonl', '.ndjson', '.jsonc', '.tsv', '.txt', '.md', '.csv', '.log', '.env', '.yaml', '.yml', '.ini', '.toml')
    
    layer_mode = "file" 
    recursive_mode = False

    while True:
        print(f"{CLS}", end="")
        print(f"\n" + f"{RED}={RST}" * 60)
        print(f"{RED}={RST}" * 60)
        print(f" CURRENT DIRECTORY :{CYN} {current}{RST}")
        print(f" FILE/DIR MODE     : {BLD}{layer_mode.upper()} " + (f"{GRN}+RECURSIVE{RST}" if recursive_mode and layer_mode == "directory" else ""))
        
        # Safe string conversion for mixed bucket types (Paths vs Tracker Dicts)
        bucket_display = []
        for item in selected_files:
            if isinstance(item, dict):
                bucket_display.append(item["name"])
            else:
                bucket_display.append(item.name)
        print(f" SELECTIONS        : {bucket_display}")
        print(f"{BLU}={RST}" * 60)

        try:
            entries = sorted(os.scandir(current), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            print(f"  {RED}{BLD}[!]{RST} Permission denied for this directory.")
            current = current.parent
            continue

        dirs = [e for e in entries if e.is_dir() and not e.name.startswith('.')]
        files = [e for e in entries if e.is_file() and e.name.endswith(valid_extensions)]


        print(f"\n {CYN}Directories:{RST}")
        if not dirs:
            print("  (No subdirectories)")
        for idx, d in enumerate(dirs, 1):
            # Check if this directory descriptor is already inside the tracker bucket
            d_path = Path(d.path).resolve()
            dir_marker = ""
            for item in selected_files:
                if isinstance(item, dict) and item.get("dir_path") == d_path:
                    dir_marker = f"{GRN}{BLD} [SELECTED]{RST} "
            print(f"  [{idx}] {d.name}{dir_marker}")

        offset = len(dirs)
        print(f"{BLU}-----------------------------")
        print(f"\n {MAG}Files (Text Docs):{RST}")
        if not files:
            print("  (No compatible text/artifact files)")
        for idx, f in enumerate(files, offset + 1):
            f_path = Path(f.path).resolve()
            marker = f"{GRN}{BLD} [SELECTED]{RST}" if f_path in selected_files else ""
            print(f"  [{idx}]  {f.name}{marker}")
        print(f"{BLU}={RST}" * 60)
        print("")

        if layer_mode == "directory":
            print(f"  [{CYN}R{RST}]  Recursive Mode ...                    (" + (f"{GRN}ON{RST}" if recursive_mode else f"{RED}OFF{RST}") + ")")
        print(f"  [{CYN}F{RST}]  File/Dir Mode ...               (File <-> Directory)")
        print(f"  [{BLU}B{RST}]  Back ...                        (^ Move directory ^)")
        print(f"  [{GRN}D{RST}]  Done ...                         (Move to next step)")
        print(f"  [{RED}Q{RST}]  Quit ...                        (Exit to Runner/CLI)")
        print(f"{BLU}={RST}" * 60)
        prompt_text = f" >> Input Option or Select Docs [{layer_mode.upper()} mode]: "
        choice = input(prompt_text).strip().lower()

        if choice == 'q':
            print(f"{CLS}")
            print(f"\n Exiting... ")
            print(f"\n\n\n           ... {RED}Stay sharp{RST} .. {GRY}Not dull{RST} ...\n\n")
            sys.exit(0)
        elif choice == 'b':
            current = current.parent
        elif choice == 'f':
            layer_mode = "directory" if layer_mode == "file" else "file"
        elif choice == 'r' and layer_mode == "directory":
            recursive_mode = not recursive_mode
        elif choice == 'd':
            if len(selected_files) == 0:
                print(f"  {RED}[!]{RST} Please select at least 1 file to proceed.")
                input("  Press [ENTER] to continue...")
                continue
            
            # Unpack and flatten any tracking descriptors before turning things over to main loops
            final_files = []
            for item in selected_files:
                if isinstance(item, dict) and "dir_path" in item:
                    d_path = item["dir_path"]
                    if item["recursive"]:
                        for ext in valid_extensions:
                            final_files.extend(d_path.rglob(f"*{ext}"))
                    else:
                        final_files.extend([p for p in d_path.iterdir() if p.is_file() and p.suffix in valid_extensions])
                else:
                    final_files.append(item)
            
            # Clean and deduplicate chronological timeline paths
            final_files = sorted(list(set(final_files)), key=os.path.getmtime)
            return current, final_files
        else:
            try:
                num = int(choice)
                if 1 <= num <= len(dirs):
                    target_dir_entry = dirs[num - 1]
                    target_dir_path = Path(target_dir_entry.path).resolve()
                    
                    if layer_mode == "file":
                        # Standard navigation behavior
                        current = target_dir_path
                    else:
                        # Intercept folder selection immediately
                        sub_files = []
                        if recursive_mode:
                            for ext in valid_extensions:
                                sub_files.extend(target_dir_path.rglob(f"*{ext}"))
                        else:
                            sub_files = [p for p in target_dir_path.iterdir() if p.is_file() and p.suffix in valid_extensions]
                        
                        if not sub_files:
                            print(f"\n  {RED}[!]{RST} No compatible files found inside `{target_dir_path.name}`.")
                            input("  Press [ENTER] to continue...")
                            continue

                        # Isolate the oldest artifact anchor
                        oldest_file_path = min(sub_files, key=os.path.getmtime)
                        oldest_ts = datetime.fromtimestamp(os.path.getmtime(oldest_file_path)).strftime('%Y-%m-%d %H:%M')
                        
                        print(f"\n  {BLU}[LAYER SELECTION LOCK]{RST}")
                        print(f"  Target Folder : {target_dir_path.name}/")
                        print(f"  Total Assets  : {len(sub_files)} tracking files available")
                        print(f"  Visual Anchor : Oldest found is {GRN}{oldest_file_path.name}{RST} ({oldest_ts})")
                        
                        confirm = input(f"\n  >> Track full folder containing {oldest_file_path.name}? [Y/n]: ").strip().lower()
                        if confirm != 'n':
                            descriptor_string = f"folder containing {oldest_file_path.name}"
                            
                            # Toggle logic match protection
                            existing_match = None
                            for item in selected_files:
                                if isinstance(item, dict) and item.get("dir_path") == target_dir_path:
                                    existing_match = item
                                    break
                            
                            if existing_match:
                                selected_files.remove(existing_match)
                                print(f"  Removed folder tracker descriptor layer.")
                            else:
                                selected_files.append({
                                    "name": descriptor_string,
                                    "dir_path": target_dir_path,
                                    "recursive": recursive_mode
                                })
                                print(f"  Folder descriptor layer added to bucket.")
                            input("  Press [ENTER] to return...")
                        
                elif len(dirs) < num <= len(dirs) + len(files):
                    file_obj = files[num - len(dirs) - 1]
                    file_path = Path(file_obj.path).resolve()
                    
                    if single_select:
                        return current, [file_path]
                    
                    # Direct check against pure Path references inside the container
                    if file_path in selected_files:
                        selected_files.remove(file_path)
                        print(f"   {RED}Removed{RST} {file_path.name} from batch.")
                    else:
                        selected_files.append(file_path)
                        print(f"   {GRN}Added{RST} {file_path.name} to batch.")
                else:
                    print(f"  {RED}[!]{RST} Invalid selection number.")
            except ValueError:
                print(f"  {RED}[!]{RST} Invalid input.")




# -- Option 3: Text File Slicer Logic --

def handle_text_splitting():
    print("\n--- Mode 3: Text File Slicer ---")
    print("Select a single text file to slice.")
    
    current_dir = Path.cwd()
    target_dir, file_list = interactive_file_selector(current_dir, single_select=True)
    file_path = file_list[0]

    print(f"\n Selected file for slicing: {BLD}{file_path.name}{RST}")
    
    # Check if JSON/JSONL variant
    json_data = None
    json_variant = None
    if file_path.suffix in ('.json', '.jsonl', '.ndjson', '.jsonc'):
        try:
            json_data, json_variant = load_json_variant(file_path)
            print(f"Detected JSON variant: {BLU}{json_variant.upper()}{RST}")
        except Exception as e:
            print(f"{RED}Warning:{RST} Failed to parse as structured JSON variant ({e}). Falling back to line slicing.")

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"{RED}Error{RST} reading file: {e}")
        return

    total_lines = len(lines)
    print(f" Total lines in file: {BLU}{total_lines:,}{RST}")

    try:
        num_chunks = int(input("How many files do you want to slice this into? (2 or more): ").strip())
        if num_chunks <= 0:
            raise ValueError
    except ValueError:
        print(f"{RED}[!]{RST} Invalid number specified. {RED}Aborting{RST}.")
        return

    if num_chunks > total_lines:
        print(f"{RED}[!]{RST} Cannot create more files than available lines.")
        return

    chunk_size = total_lines // num_chunks
    remainder = total_lines % num_chunks

    ts_now = datetime.now()
    ts = ts_now.strftime("%Y%m%d_%H%M%S")
    iso_ts = ts_now.isoformat()
    split_out_dir = OUTPUT_DIR / f"split_{file_path.stem}_{ts}"
    os.makedirs(split_out_dir, exist_ok=True)

    print(f"\n Slicing into {BLD}{num_chunks}{RST} files inside: {MAG}{split_out_dir}{RST}")

    tsv_lines = [
        PROTOCOL_HEADER_TSV.strip(),
        "chunk_file\toriginal_file\tchunk_index\tstart_line\t"
        "end_line\tline_count\tchecksum_md5\ttimestamp\tjson_ptr"
    ]

    meta_block = dict(PROTOCOL_META_JSON)
    meta_block["ts"] = datetime.now(timezone.utc).isoformat()
    
    json_index = {
        "_meta": meta_block,
        "original_file": file_path.name,
        "total_lines": total_lines,
        "num_chunks": num_chunks,
        "is_json_variant": json_variant is not None,
        "json_variant_type": json_variant,
        "chunks": []
    }

    start_idx = 0
    for i in range(num_chunks):
        current_chunk_size = chunk_size + (1 if i < remainder else 0)
        end_idx = start_idx + current_chunk_size
        
        chunk_lines = lines[start_idx:end_idx]
        chunk_content = "".join(chunk_lines)
        chunk_hash = hashlib.md5(chunk_content.encode('utf-8')).hexdigest()
        
        chunk_filename = f"{file_path.stem}_part{i+1}_of_{num_chunks}{file_path.suffix}"
        chunk_path = split_out_dir / chunk_filename

        with open(chunk_path, 'w', encoding='utf-8') as cf:
            cf.writelines(chunk_lines)

        tsv_lines.append(
            f"{chunk_filename}\t{file_path.name}\t{i+1}\t{start_idx+1}\t{end_idx}\t{len(chunk_lines)}\t{chunk_hash}\t{iso_ts}\t{json_ptr}"
        )

        json_index["chunks"].append({
            "chunk_file": chunk_filename,
            "chunk_index": i + 1,
            "start_line": start_idx + 1,
            "end_line": end_idx,
            "line_count": len(chunk_lines),
            "checksum_md5": chunk_hash,
            "json_ptr": json_ptr
        })

        print(f"  [Created] {chunk_filename} ({len(chunk_lines):,} lines | MD5: {chunk_hash[:8]})")
        start_idx = end_idx

    # Write tethered indices
    with open(split_out_dir / "dense.json", "w", encoding="utf-8") as f:
        json.dump(json_index, f, indent=2)

    dense_hash = hashlib.sha256(
        (split_out_dir / "dense.json").read_bytes()
    ).hexdigest()
    tsv_lines.insert(1, f"# DENSE_SHA256\t{dense_hash}")

    with open(split_out_dir / "index.tsv", "w", encoding="utf-8") as f:
        f.write('\n'.join(tsv_lines) + '\n')

    print(f"\n{GRN}Successfully{RST} sliced file into {BLD}{num_chunks}{RST} parts!")
    print(f"Output directory: {split_out_dir}")

# -- Option 4: Text File Reconstruction Logic with Directory Nav Fallback --

def perform_reconstruction_from_directory(target_dir: Path):
    tsv_path = target_dir / "index.tsv"
    if not tsv_path.exists():
        print(f"\n{RED}[!]{RST} Index file `index.tsv` not found in target package directory: {target_dir}")
        print("Looking for sliced files directly...")
        chunk_files = sorted(list(target_dir.glob("*_part*_of_*")))
        if not chunk_files:
            print(f"{RED}[!]{RST} No sliced files detected here either.")
            return

        print(f"Found {len(chunk_files)} sliced files. Reconstructing purely by filename sequence...")
        reconstructed_content = []
        original_file = "reconstructed_output.txt"
        
        for cf_path in chunk_files:
            with open(cf_path, "r", encoding="utf-8", errors="ignore") as cf:
                reconstructed_content.append(cf.read())
            print(f"  [Read] {cf_path.name}")

        out_file_path = target_dir / f"reconstructed_{original_file}"
        with open(out_file_path, "w", encoding="utf-8") as out_f:
            out_f.write("".join(reconstructed_content))

        print(f"\n{GRN}Successfully reconstructed fallback:{RST} {out_file_path}")
        return

    print(f"\nReconstructing from package map: {MAG}{target_dir.name}{RST}")
    
    chunks_info = []
    original_file = "reconstructed_output.txt"

    with open(tsv_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split("\t")
            if parts[0] == "chunk_file":
                continue
            if len(parts) >= 7:
                chunks_info.append({
                    "chunk_file": parts[0],
                    "original_file": parts[1],
                    "chunk_index": int(parts[2]),
                    "start_line": int(parts[3]),
                    "end_line": int(parts[4]),
                    "line_count": int(parts[5]),
                    "checksum_md5": parts[6]
                })
                original_file = parts[1]

    chunks_info.sort(key=lambda x: x["chunk_index"])

    reconstructed_content = []
    for info in chunks_info:
        chunk_file_path = target_dir / info["chunk_file"]
        if not chunk_file_path.exists():
            print(f"  {RED}[ERROR]{RST} Slice file missing: {info['chunk_file']}")
            return
        
        with open(chunk_file_path, "r", encoding="utf-8", errors="ignore") as cf:
            content = cf.read()

        current_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        if current_hash != info["checksum_md5"]:
            print(f"  {RED}[WARNING]{RST} MD5 Hash mismatch on {info['chunk_file']}! Content may have been altered.")
        else:
            print(f"  {GRN}[Verified]{RST} {info['chunk_file']} integrity OK")

        reconstructed_content.append(content)

    out_file_path = target_dir / f"reconstructed_{original_file}"
    with open(out_file_path, "w", encoding="utf-8") as out_f:
        out_f.write("".join(reconstructed_content))

    print(f"\n  {GRN}Successfully reconstructed:{RST} {out_file_path}")

def handle_reconstruction():
    print("\n  --- Mode 4: Text File Reconstruction ---")
    
    past_splits = []
    if OUTPUT_DIR.exists():
        # Most recent at the top
        past_splits = sorted([d for d in OUTPUT_DIR.iterdir() if d.is_dir() and d.name.startswith("split_")], key=lambda x: x.name, reverse=True)

    if past_splits:
        print(f"\n  {BLU}Found past slice jobs (Most recent first):{RST}")
        for idx, d in enumerate(past_splits, 1):
            print(f"    [{idx}] {d.name}")
        print(f"    [N] Navigate directories manually (Fallback / Custom folder)")
        print("-" * 60)
        
        choice = input("Select past job number or press [N] to navigate manually: ").strip().lower()
        if choice != 'n':
            try:
                sel = int(choice)
                if 1 <= sel <= len(past_splits):
                    target_dir = past_splits[sel - 1]
                    perform_reconstruction_from_directory(target_dir)
                    return
                else:
                    print(f"{RED}[!]{RST} Invalid selection index.")
            except ValueError:
                print(f"{RED}[!]{RST} Invalid input. Switching to directory navigation.")

    # Fallback / Manual navigation option
    print("\n[Manual Directory Navigation mode activated]")
    print("Browse to select the folder containing your slices and index file.")
    current_dir = Path.cwd()
    
    while True:
        print(f"\nCurrent Directory: {current_dir}")
        print("    [B] Go up parent directory")
        print(f"  [{GRN}ENTER{RST}] Select *this* current directory for reconstruction")
        print("    [{RED}Q{RST}] Cancel / Quit reconstruction")
        
        try:
            entries = sorted([e for e in os.scandir(current_dir) if e.is_dir() and not e.name.startswith('.')], key=lambda e: e.name.lower())
        except PermissionError:
            print(f"{RED}[!]{RST} Permission denied.")
            current_dir = current_dir.parent
            continue

        for idx, d in enumerate(entries, 1):
            print(f"  [{idx}] {d.name}/")

        nav_choice = input("Input number to open, [ENTER] a folder, [B]ack, or [Q]: ").strip().lower()
        if nav_choice == 'q':
            return
        elif nav_choice == 'b':
            current_dir = current_dir.parent
        elif nav_choice == '':
            perform_reconstruction_from_directory(current_dir)
            return
        else:
            try:
                num = int(nav_choice)
                if 1 <= num <= len(entries):
                    current_dir = Path(entries[num - 1].path)
                else:
                    print(f"{RED}[!]{RST} Invalid directory number.")
            except ValueError:
                print(f"{RED}[!]{RST} Invalid input.")

def main():
    parser = argparse.ArgumentParser(description="vdx dynamic AI optimized diff check & flattener")
    parser.add_argument("--mode", type=str, choices=["1", "2", "3", "4"], help="Run mode: 1 for Diff, 2 for Flatten, 3 for Slicer, 4 for Reconstruct")
    args, unknown = parser.parse_known_args()

    print(f"{CLS}")
    print(f"\n  {RED}======================================================================{RST}")
    print("  ======================================================================")
    print(f"                              {BLD}{RED}-- vdx --{RST}")
    print(f"                         {BLD}Diff, Flatten, Slice{RST}")
    print("  ======================================================================")
    print(f"  {RED}======================================================================{RST}")
    print()

    # Auto-scan OUTPUT_DIR for past reports (displayed cleanly without conflicting numbers)
    past_reports = []
    if OUTPUT_DIR.exists():
        past_reports = sorted([d.name for d in OUTPUT_DIR.iterdir() if d.is_dir()])
    
    if past_reports:
        print(f"                    {BLU}Recent Reports:{RST}")
        for rep in past_reports[:3]:  # Show top 3 recent ones
            print(f"                {MAG}    • {rep}")
        print(f"\n  {GRY}++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n{RST}")

    print(f"  {BLD}[1] Diff & Comparison Mode {GRY}(Compare target files against ground truth){RST}")
    print(f"  {BLD}[2] Flatten Mode           {GRY}(Reduce noise in 1 or more files){RST}")
    print(f"  {BLD}[3] Slice Mode             {GRY}(Slice a text file into smaller files){RST}")
    print(f"  {BLD}[4] Reconstruct Mode       {GRY}(Rebuild sliced files from past jobs){RST}")
    
    mode_choice = args.mode or (input(f"\n  >>  Select mode [{BLD}1 - 4{RST}]: ").strip() or "1")

    if mode_choice == "3":
        handle_text_splitting()
        return
    elif mode_choice == "4":
        handle_reconstruction()
        return

    current_dir = Path.cwd()

    while True:
        target_dir, file_path_list = interactive_file_selector(current_dir, single_select=False)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        if mode_choice == "2":
            print(f"\n  Processing {MAG}{len(file_path_list)}{RST} file(s) into a structured flattened package...")
            file_records = []
            for file_path in file_path_list:
                target_file = file_path.name
                origin_folder = file_path.parent.name or "Root"
                
                if file_path.suffix in ('.json', '.jsonl', '.ndjson', '.jsonc'):
                    try:
                        _, variant = load_json_variant(file_path)
                        print(f"  Parsed '{target_file}' as valid {variant.upper()}")
                    except Exception as e:
                        print(f"  {RED}Notice:{RST} '{target_file}' normalization falling back to plain text: {e}")

                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_src = f.read()
                file_clean = universal_normalize(file_src, target_file)
                
                file_records.append({
                    "name": target_file, 
                    "origin_layer": origin_folder,
                    "src": file_src, 
                    "clean": file_clean
                })

            out_dir_path = OUTPUT_DIR / f"flat_scan_{ts}"
            write_flat_batch_report(file_records, out_dir_path)

            print(f"\n   Unified flattened layer package successfully generated at:")
            print(f"  {MAG}{out_dir_path}{RST}")


        else:
            if len(file_path_list) < 2:
                print(f"  {RED}[!]{RST} Differential mode requires at least 2 files.")
                input(f"  Press [{GRN}ENTER{RST}] to continue...")
                continue

            # 1. Timeline configuration and format layout selector
            print(f"\n  {BLU}Timeline Configuration:{RST}")
            print(" [1] Forward Timeline (Oldest ➔ Newest) - Track evolution")
            print(" [2] Reverse Timeline (Newest ➔ Oldest) - Audit backward")
            time_choice = input(f"\n  >> Select timeline order [Default: 1]: ").strip()
            reverse_order = True if time_choice == "2" else False

            print(f"\n  {BLU}Output Format Profile:{RST}")
            print(" [1] Full Ingest Package (TSV JSON MD)")
            print(" [2] Lightweight Mapping Only (TSV Index Only - Extra Token-Saving)")
            fmt_choice = input(f"\n  >> Select output profile [Default: 1]: ").strip()
            tsv_only = True if fmt_choice == "2" else False

            # 2. Force strict chronological sorting based on absolute filesystem time
            sorted_file_paths = sorted(file_path_list, key=os.path.getmtime, reverse=reverse_order)

            direction_label = "Reverse" if reverse_order else "Forward"
            print(f"\n  Running {direction_label} sequential scan across {MAG}{len(sorted_file_paths)}{RST} files...")

            comparisons = []
            
            # 3. Pairwise sliding window calculation
            for i in range(len(sorted_file_paths) - 1):
                base_file_path = sorted_file_paths[i]
                target_file_path = sorted_file_paths[i + 1]

                base_file = base_file_path.name
                target_file = target_file_path.name

                # Calculate chronological time gaps between saves
                time_base = os.path.getmtime(base_file_path)
                time_target = os.path.getmtime(target_file_path)
                time_diff_seconds = abs(time_target - time_base)

                if time_diff_seconds < 60:
                    time_gap = f"{int(time_diff_seconds)}s apart"
                elif time_diff_seconds < 3600:
                    time_gap = f"{int(time_diff_seconds // 60)}m apart"
                else:
                    time_gap = f"{round(time_diff_seconds / 3600, 1)}h apart"

                print(f"    [{i+1}] Processing: {base_file} ➔ {target_file} ({time_gap})")

                # Read raw payloads
                with open(base_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    base_src = f.read()
                with open(target_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    t_src = f.read()

                # Normalize text
                base_clean = universal_normalize(base_src, base_file)
                t_clean = universal_normalize(t_src, target_file)

                # Calculate Syntactic Density (Clean Lines / Raw Lines)
                raw_base_len = len(base_src.splitlines()) or 1
                raw_target_len = len(t_src.splitlines()) or 1
                
                density_base = len(base_clean.splitlines()) / raw_base_len
                density_target = len(t_clean.splitlines()) / raw_target_len
                density_delta = density_target - density_base

                # Heavy structural processing for the Library
                diff = compute_diff(base_clean, t_clean)
                
                comparisons.append({
                    "base": base_file, 
                    "target": target_file, 
                    "diff": diff,
                    "time_gap": time_gap,
                    "density_delta": f"{density_delta:+.3f}"
                })

            out_dir_path = OUTPUT_DIR / f"diff_scan_{ts}"
            write_batch_report(comparisons, out_dir_path, tsv_only=tsv_only)

            print(f"\n   VDX delta package successfully generated at:")
            print(f"  {MAG}{out_dir_path}{RST}")



        again = input(f"\n >> {BLU}Run another job{RST}? [y/N]: ").strip().lower()
        if again != 'y':
            print("\n\n Exiting...")
            print(f"\n              ... {RED}Stay sharp{RST} .. {GRY}Not dull{RST} ...")
            break
        current_dir = target_dir

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[{RED}ERROR{RST}]: An unexpected error occurred: {e}")
        print(f"\n\n    ...{RED} Stay sharp{RST} .. {GRY}Not dull{RST} ...")
        input("\n                    Press [ENTER] to exit...")