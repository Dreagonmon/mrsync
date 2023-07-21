# mrsync

My rsync config manager.

I want to backup some of my dirs to remote server and local mobile hard disk, at the same time.

It is stupid to maintain 4 copies of bash scripts (backup, restore, for remote, for local) for each dir.

This is why I write this tools.

## Goal

- generate different rsync command, for a single dir, with many different locations (source, destination).
- define different `mode` to control rsync flags (args).
- Can be packed to a single .pyz python executable zip file.

## Configure

See `example.mrsync.hjson`
