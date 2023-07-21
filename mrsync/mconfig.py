import merror
import hjson
import os

def load_config(cfg_path):
    if os.path.exists(cfg_path) and os.path.isfile(cfg_path):
        with open(cfg_path, "rt", encoding="utf-8") as f:
            cfg = hjson.loads(f.read())
        return cfg
    raise merror.ConfigNotFoundError(cfg_path)

def process_flags(flags, flist):
    # type: (set, list[str]) -> None
    for item in flist:
        if item.startswith("-"):
            flags.discard(item[1:])
        else:
            flags.add(item)

class ConfigParser:
    def __init__(self, cfg_path):
        self.cfg = load_config(cfg_path)
        self.gflags = set()
        self.ginclude = list()
        self.gexclude = list()
        # global options
        glob = self.cfg.get("global", {})
        process_flags(self.gflags, glob.get("flags", []))
        self.ginclude.extend(glob.get("include", []))
        self.gexclude.extend(glob.get("exclude", []))
    
    def get_entry(self, entry):
        entries = self.cfg.get("entries", {})
        if entry not in entries:
            raise merror.EntryNotFoundError(entry)
        return entries.get(entry, {})
    
    def get_location(self, entry, location):
        locations = self.get_entry(entry).get("locations", {})
        if location not in locations:
            raise merror.LocationNotFoundError(location)
        loc = locations.get(location, {})
        if "path" not in loc:
            raise merror.LocationNotFoundError(location)
        if not loc.get("path", "").endswith(os.path.sep):
            raise merror.LocationNotEndWithSlashError(location)
        return loc
    
    def get_flags(self, entry, mode=""):
        flags = self.gflags.copy()
        entry_item = self.get_entry(entry)
        process_flags(flags, entry_item.get("flags", []))
        if len(mode) > 0:
            fkey = f"flags_{mode}"
            if fkey not in entry_item:
                raise merror.ModeNotFoundError(mode)
            process_flags(flags, entry_item.get(fkey, []))
        flags_list = list(flags)
        flags_list.sort()
        flags_list.sort(key=lambda flag: len(flag))
        return flags_list
    
    def get_include(self, entry):
        flist = list(self.ginclude)
        flist.extend(self.get_entry(entry).get("include", []))
        return flist

    def get_exclude(self, entry):
        flist = list(self.gexclude)
        flist.extend(self.get_entry(entry).get("exclude", []))
        return flist
    
    def generate_cmd_args(self, flags, location_from, location_to, exclude_pattern=[], include_pattern=[]):
        if isinstance(location_from, str):
            location_from = self.get_location(location_from)
        if isinstance(location_to, str):
            location_to = self.get_location(location_to)
        cmd_args = []
        # flags
        flags_set = set(flags)
        flags_list = list(flags_set)
        flags_list.sort()
        flags_list.sort(key=lambda flag: len(flag))
        for flag in flags_list:
            if len(flag) == 1:
                cmd_args.append(f"-{flag}")
            else:
                cmd_args.append(f"--{flag}")
        # pattern
        for exclude in exclude_pattern:
            cmd_args.append("--exclude")
            cmd_args.append(exclude)
        for include in include_pattern:
            cmd_args.append("--include")
            cmd_args.append(include)
        # source
        if "options" in location_from:
            cmd_args.append("-e")
            cmd_args.append(location_from["options"])
        cmd_args.append(location_from["path"])
        # dest
        if "options" in location_to:
            cmd_args.append("-e")
            cmd_args.append(location_to["options"])
        cmd_args.append(location_to["path"])
        return cmd_args
