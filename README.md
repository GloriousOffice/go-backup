go-backup
=========

go-backup is a backup tool.

Workflow
--------

As a default, go-backup is invoked with `go-backup src dest`. Then, the workflow is as follows:

1. Verify the current backup (residing in `dest`) with the previously recorded hash digest data from `dest/.go_backup/backup_<timestamp-of-most-recent-backup>/metadata.json` (after checking this file with the corresponding `hashsums.json`). If this check fails the back up is aborted unless `--ignore-initial-verification` option is specified.
2. Compute the hashes for the source directory `src` and write the metadata to  `dest/.go_backup/backup_<current-timestamp>/metadata.json`
3. Compare the hashes of the backup and the source directory by comparing the content of the two `.json` files described above.
4. Move files for which the hashes changed or files which were deleted into `dest/.go_backup/backup_<current-timestamp>/old_files`. The `old_files` directory has a flat structure, where each filename is the hash of its contents.
5. Copy all changed/new files from `src` to `dest`.
6. Verify the backup at `dest` against the metadata file `dest/.go_backup/backup_<current-timestamp>/metadata.json`.

Hashing is done using `hashdeep` and copying/moving is done using `rsync`.

Patterns
--------

go-backup expects a file with include/exclude patterns in `src/.go_backup_patterns`. All lines in file must be either comments (starting with `#`), include patterns (matching `+ /dir/ect/ory` or `+ /file/name`) and exclude patterns (matching `- /dir/ect/ory` or `- /file/name`). Above "to match" means that pattern either coincides with the file/directory name or specifies a directory that contains the file/directory name it is matched against. The last matching pattern wins. The default is to "include" (so empty pattern file would be the same as asking to backup entire `src`). All patterns *look like absolute paths* (e.g. `+ /`), but are interpreted *relative* to `src` and `dest`. The paths are what you would see after a `chroot src`.

Directory structure
-------------------

go-backup expects the following structure under `src`:
* a `.go_backup_patterns` file

go-backup will maintain the following structure under `dest/.go_backup`:
* a `version.txt` containing the version of the maintained structures; this will get bumped up with every incompatible change to go-backup;
* a directory `backup_YYYY_MM_DD_HH_MM_SS` for each go-backup invocation containing:
  * a `metadata.json` containing an entry for each file/directory/symbolic link (listing its meta data and checksums (if applicable));
  * a `log.txt`
  * a `old_files` directory containing files that existed in previous backup iteration but got changed/deleted in the current one. For example, assume that today's version of `src` does not contain `src/foo`, while it was backed up in `dest/foo` during the previous go-backup run. Then go-backup would move `dest/foo` to `dest/.go_backup/backup_YYYY_MM_DD_HH_MM_SS/oldfiles/HASH`, where `HASH` is a hash of `dest/foo`;
  * a `prev_metadata.json` file describing the structure of `src` before the `go-backup` invocation;
  * and `hashsums.json` containing checksums of `metadata.json`, `prev_metadata.json` and `log.txt`

Storing `prev_metadata.json` which, if not corrupted, will coincide with `metadata.json` of previous backup is intentional: we want to be able to simply delete old `backup_...` directories, without compromising our ability to restore-to-previous of all following backups.

Format of `metadata.json`
-------------------------

A `metadata.json` contains a dictionary with the following structure:
* `timestamp`
* `command_line`
* `files` a list of dictionaries each having the following structure:
  * `name`
  * `atime`, `ctime`, `mtime`
  * `sha1`, `sha256`
  * `size`
  * `user`
  * `group`
  * `permissions`
* `directories`, a list of dictionaries each having the following structure:
  * `name`
  * `atime`, `ctime`, `mtime`
  * `user`
  * `group`
  * `permissions`
* `symlinks`, a list of dictionaries each having the following structure:
  * `name`
  * `native_target`
  * `atime`, `ctime`, `mtime`
  * `user`
  * `group`
  * `permissions`

Logging
-------

The output of go-backup will include:
* all errors encountered;
* all paths ignored (e.g. named pipes);
* difference between previous go-backup output and the current state of `src`;
* statistics.
* output of `rsync`.

Handling of special cases
-------------------------

With respect to specal file types go-backup will do the following:
* do not follow symlinks, but pass them over for copying to `rsync`;
* treat hardlinks as normal files/directories;
* copy over directories that are mount points, but do *not* recurse into them;
* ignore block devices, FIFOs and other special file types.

(TODO: have we missed anything?)

Restoring data
--------------

Should be as easy as just copying the `dest` back over to `src` (ignoring `dest/.go_backup` folder, if older versions of files are not needed).

(TODO: provide tools?)

Bibliographic notes
-------------------

go-backup is written by Ludwig Schmidt and Madars Virza. go-backup is written in Python, not Go; apart from being a nice name, the "go" in go-backup also stands for [Glorious Office](http://www.gloriousoffice.com/).
