go-backup
=========

go-backup is a backup tool.
go-backup places special emphasis on *data integrity* and stores cryptographic checksums with every backup.

Design principles
-----------------

go-backup must be simple and easy-to-audit. Clever code lets subtle bugs pass by. For example:
* Instead of "update this target directory to match source", just check out the most recent backup. This both tests restore functionality and is simpler
* Do not implement clever features that are hard-to-audit, like rolling checksums. If we can't be certain that go-backup does backups correctly, it is useless.

go-backup backups must be restorable without go-backup. We use "restorable" to mean "can whip up a Python script in 1-2 hours" not `cp -r magic-directory/ target/`.

Backup format
-------------

**(The format below is stable and we intend no changes in foreseeable future.)**

The backend for go-backup backups is a [content-addressable storage](https://en.wikipedia.org/wiki/Content-addressable_store) (CAS). Each blob stored in the CAS stores either:
* contents of a file; or
* directory metadata in format described below.

An entire backup is referenced by the hash of the blob describing its root directory. We now describe, in full detail, the format of directory metadata. If a detail is unspecified or ambiguous, it is a bug; please report it as such.

Each directory metadata blob is a byte string consisting of two parts concatenated together:
* magic string "go-backup metadata (version X)\n" used as header (we mandate X=1 for the current version and that all incompatible versions have different version numbers); and
* JSON encoding of a list of directory entries. The directory entry format is described below and the list is sorted by name.
In particular, the plan is that everything up to the first newline is a header field containing version information. The binary format after the newline might change in the future (but there are currently no plans to do so).

go-backup uses `json.dump(indent=2, encoding="utf-8", separators=(',', ': '), sort_keys=True)` for the JSON encoding. Note that `json` module does not make explicit guarantees that same object will always result in the same encoding, but it appears to be the case in practice. The correctness of go-backup does not rely on unique encodings.

Each directory entry is a dictionary with the following keys and their corresponding values:
- `name` (relative to the directory)
- `type`, as string. Only the following values are permitted: "file", "symlink", "directory".
- `mtime`, as the string result of `time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(mtime))`. This is the combined date/time format of ISO 8601, using UTC as the timezone. Note that mtime entry here stores the value with resolution of one second.
- `size` (iff `type`="file"), an integer specifying the length of the file in bytes
- `user`, `group` - the symbolic (not numeric) user/group names, as returned by Python 2 `pwd.getpwall` and `grp.getgrall` calls
- `link_target` (iff `type`="symlink") containing the target of the symbolic link entry
- `permissions`, a string of four octal digits encoding the file mode (i.e. `"%04o" % os.stat(filename).st_mode`)
- `hash` (iff `type`="file" or `type`="directory") -- hash of the file contents (if `type`="file"), or the metadata blob describing the particular subdirectory (if `type`="directory")

Notes on `mtime`:
- go-backup does not store ctime (the ctime semantics limits its usefulness and even with root privileges there is no standard way of restoring it) and atime (storing it would preclude metadata deduplication, as atimes change after each backup).
- In Python 2, the result of os.stat call returns mtime as floating point number with not enough accuracy to store nanosecond time, and thus performs rounding. Even if nanosecond time was obtained, it could not be properly restored as Python uses utimes(2) syscall, which only supports microsecond resolution (see https://bugs.python.org/issue10148). Thus files restored from go-backup backup might slightly differ from the originals in the mtime field.

Notes on `size`:
- JavaScript Numeric type only guarantees accurate storage of integers not exceeding 2^53, however JSON, as an abstract format, does not have this limitation. In either case, 2^53 bytes ~ 9 petabytes, far exceeding the size supported by common file systems.

Planned primitive operations
----------------------------
- `get-filesystem-metadata <directory>`
  - Input: a directory to be backed up
  - Output: a merged JSON metadata description of the entire directory structure, including hashes
- `get-cas-metadata <root>`
  - Input: hash of the root metadata object in the CAS
  - Output: merged JSON metadata
- `metadata-diff [MERGED-METADATA1] [MERGED-METADATA2]`
- `metadata-parse`
  - Given a metadata file, parse it to verify that it is correct, and then print a current-version of it if it is correct (used for upgrades)
- `backup --dry-run`
  - `get-filesystem-metadata`
  - `get-cas-metadata`
  - `metadata-diff`
- `import-diff`
  - Input: Merged JSON metadata
  - Output: chunks the metadata and copies all referenced files into the CAS
- `backup`
  - `backup --dry-run`
  - `import-diff`
- `cat-blob [HASH]`
  - Input: hash of a CAS object
  - Output: writes that object to STDOUT after verifying integrity (non-recursively)
- `restore <HASH> <destination>`
- `get-cas-metadata <HASH>`
  - a loop that creates target structure (is this useful on its own?)
  - a loop of cat-blob
  - a loop that fixes up permissions, etc
  - Q: do we want restores in non-empty targets? Proposal: FLAG CONTROLLED; default off, but can specify --force
- `list-snapshots`
- `verify-reachable`
  - Input: snapshot list
  - Operation: check that all objects are reachable and verify integrity recursively
- `list-unreachable`
  - Input: snapshot list
  - Operation: find all objects, remove all reachable objects. Return result
- `consistency-check`
  - `verify-reachable`
  - `list-unreachable `
- `garbage-collect`
  - `consistency-check`
  - `prune-unreachable`
- `cas-diff [root-set-1] [root-set-2]`
- `cas-export-subset [root set]`
  - Produces a new CAS that contains only the recursively reachable set described by the input.
- `export-next-incremental`
  - metadata-diff on two last
  - cas-export-subset the result
  - Optional: tar up result
- `import-next-incremental`

Patterns
--------

go-backup expects a file with include/exclude patterns in `src/.go_backup_patterns`. All lines in file must be either comments (starting with `#`), include patterns (matching `+ /dir/ect/ory` or `+ /file/name`) and exclude patterns (matching `- /dir/ect/ory` or `- /file/name`). Above "to match" means that pattern either coincides with the file/directory name or specifies a directory that contains the file/directory name it is matched against. The last matching pattern wins. The default is to "include" (so empty pattern file would be the same as asking to backup entire `src`). All patterns *look like absolute paths* (e.g. `+ /`), but are interpreted *relative* to `src` and `dest`. The paths are what you would see after a `chroot src`.

Logging
-------

The output of go-backup will include:
* all errors encountered;
* all excluded files or directories in `src`, but not files/directories within an excluded directory;
* all paths ignored in `src` (e.g. named pipes, block devices, etc.);
* all mount points encountered (note that `go-backup` won't recurse in a mount point);
* new, changed or deleted files between the current and the previous go-backup runs;
* statistics.

Handling of special cases
-------------------------

With respect to special file types go-backup will do the following:
* do not follow symlinks, but report them in the metadata file and recreate them under `dest`;
* treat hardlinks as normal files/directories;
* for directories that are mount points create their equivalents under `dest`, but do no *not* recurse into them;
* ignore block devices, FIFOs and other special file types.

Requirements
------------

go-backup depends on `pytest` for tests. It has only been tested on Unix-like systems (in particular, Linux and OS X). File name handling will likely require changes to work on Windows, due to the different path separators.

Bibliographic notes
-------------------

go-backup is designed by Alexander Chernyakhovsky, Ludwig Schmidt and Madars Virza. go-backup is written in Python, not Go; apart from being a nice name, the "go" in go-backup also stands for [Glorious Office](http://www.gloriousoffice.com/).
