go-backup
=========

go-backup is a backup tool.

Workflow
--------

The go-backup workflow when invoked as `go-backup src dest` is to:
1. Verify the current backup (residing in `dest`) with the previously recorded hash digest file from `dest/.go_backup/hashdigests/<most-recent-timestamp>`.
2. Create hash file for the source directory `src`.
3. Compare this hash file against the hash file of the backups.
4. Move files for which the hashes changed or files which got deleted into `dest/.go_backup/oldfiles/<current-timestamp>`.
5. Copy over all changed/new files from `src` to `dest`.
6. Verify the backup at `dest` against the hash file of `src`.

Patterns
--------

go-backup expects a file with include/exclude patterns in `src/.go_backup_patterns`. All lines in file must be either comments (starting with `#`), include patterns (matching `+ /dir/ect/ory` or `+ /file/name`) and exclude patterns (matching `- /dir/ect/ory` or `- /file/name`). The last matching pattern wins. The default is to "include" (so empty pattern file would be the same as asking to backup entire `src`).

Bibliographic notes
-------------------

go-backup is written by Ludwig Schmidt and Madars Virza. go-backup is written in Python, not Go; apart from being a nice name, the go- in go-backup also stands for [Glorious Office](http://www.gloriousoffice.com/).
