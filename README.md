go-backup
=========

go-backup is a backup tool.

Workflow
--------

The go-backup workflow when invoked as `go-backup src dest` is to:
1. Verify the current backup (residing in `dest`) with the previously recorded hash digest file from `dest/.go_backup/hashdigests/<most-recent-timestamp>`;
2. Create hash file for the source directory `src`;
3. Compare this hash file against the hash file of the backups;
4. Move files for which the hashes changed or files which got deleted into `dest/.go_backup/oldfiles/<current-timestamp>`;
5. Copy over all changed/new files from `src` to `dest`;
6. Verify the backup at `dest` against the hash file of `src`.

Hashing is done using `hashdeep` and copying/moving is done using `rsync`.

Patterns
--------

go-backup expects a file with include/exclude patterns in `src/.go_backup_patterns`. All lines in file must be either comments (starting with `#`), include patterns (matching `+ /dir/ect/ory` or `+ /file/name`) and exclude patterns (matching `- /dir/ect/ory` or `- /file/name`). The last matching pattern wins. The default is to "include" (so empty pattern file would be the same as asking to backup entire `src`). All patterns *look like absolute paths* (e.g. `+ /`), but are interpreted *relative* to `src` and `dest`.

Directory structure
-------------------

go-backup expects the following structure under `src`:
* a `.go_backup_patterns` file

go-backup will maintain the following structure under `dest/.go_backup`:
* a `version.txt` containing the version of the maintained structures; this will get bumped up with every incompatible change to go-backup;
* an `oldfiles` directory containing a subdirectories with moved/changed files from previous backup iterations. For example, assume that today's version of `src` does not contain `src/foo`, while it was backed up in `dest/foo` during the previous go-backup run. Then go-backup would move `dest/foo` to `dest/oldfiles/<current-timestamp>/foo`;
* a `hashdigests` directory containing `hashdeep` DFXML outputs of previous go-backup runs on `src`. Each such file itself is checksummed and a result stored in (TODO);
* a `metadata` folder with text files (one per each go-backup run) containing meta data of all matching files/directories/symbolic links from `src`. Each meta data file is checksummed and a result stored in (TODO).

Metadata files
--------------

For each macthing file/directory/symbolic link of `src` go-backup will store the following information in the metadata file:

* name;
* type (file/directory/symbolic link);
* creation, access and modification times;
* size (for files);
* target (for symbolic links).

(TODO: specify format)

Handling of special cases
-------------------------

With respect to specal file types go-backup will do the following:
* do not follow symlinks, but pass them over for copying to `rsync`;
* treat hardlinks as normal files/directories;
* copy over directories that are mount points, but *not* recurse into them;
* ignore block devices, FIFOs and other special file types.

(TODO: have we missed anything?)

Restoring data
--------------

Should be as easy as just copying the `dest` back over to `src` (ignoring `dest/.go_backup` folder, if older versions of files are not needed).

(TODO: provide tools?)

Bibliographic notes
-------------------

go-backup is written by Ludwig Schmidt and Madars Virza. go-backup is written in Python, not Go; apart from being a nice name, the go- in go-backup also stands for [Glorious Office](http://www.gloriousoffice.com/).
