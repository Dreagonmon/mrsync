import argparse
import mconfig
import shutil
import shlex
import subprocess

EXE_RSYNC = shutil.which("rsync")

def cmd_info(args):
    # subcommand info
    print(f"Executable rsync path: {EXE_RSYNC}")
    print(f"Config path: {args.config}")
    cfg = mconfig.load_config(args.config)
    print("================================")
    print("Available entries:")
    entries = cfg.get("entries", {})
    for k in entries.keys():
        print()
        print(f"{k}:")
        entry = entries[k]
        # locations
        print(f"    Available locations for entry '{k}':")
        locs = entry.get("locations", {})
        for lk in locs.keys():
            print(f"        {lk}")
        # modes
        print(f"    Available mods for entry '{k}':")
        mods = set()
        for ek in entry.keys():
            if ek.startswith("flags_"):
                mods.add(ek[len("flags_"):])
        for mod in mods:
            print(f"        {mod}")

def _confirm(message):
    while True:
        inp = input(f"{message} (y/n): ").lower()
        if inp in [ "y", "yes" ]:
            return True
        elif inp in [ "n", "no" ]:
            return False
        print()

def _show_or_sync(args, show=True):
    cp = mconfig.ConfigParser(args.config)
    flags = cp.get_flags(args.entry, args.mode)
    if show:
        flags.append("v")
        flags.append("dry-run")
    _from = cp.get_location(args.entry, args._from)
    to = cp.get_location(args.entry, args.to)
    exc = cp.get_exclude(args.entry)
    inc = cp.get_include(args.entry)
    # print options
    print(f"Source path: {_from.get('path', '')}")
    print(f"Destination path: {to.get('path', '')}")
    print("================================")
    print("Exclude patterns:")
    for e in exc:
        print(e)
    print("================================")
    print("Include patterns:")
    for i in inc:
        print(i)
    # get cmd args
    cmd_args = [ EXE_RSYNC ]
    cmd_args.extend(cp.generate_cmd_args(flags, _from, to, exc, inc))
    print("================================")
    print("The following command will be executed:")
    print("")
    print(shlex.join(cmd_args))
    print("")
    if (not show) and (not args.yes) and (not _confirm("Do you want to continue execute?")):
        return
    print("================================")
    subprocess.run(cmd_args)


def cmd_show(args):
    _show_or_sync(args, True)

def cmd_sync(args):
    _show_or_sync(args, False)

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        title="subcommands",
        required=True,
    )

    # global options
    parser.add_argument(
        "-c", "--config", 
        dest="config",
        default="mrsync.hjson",
        metavar="CONFIG_PATH",
        help="Config file path (default is mrsync.hjson)",
    )

    # subcommand info
    p_info = subparsers.add_parser(
        "info",
        help="Show informations",
    )
    p_info.set_defaults(func=cmd_info)

    def common_args_show_sync(p):
        # type: (argparse.ArgumentParser) -> None
        p.add_argument(
            "-e", "--entry",
            dest="entry",
            required=True,
            metavar="ENTRY",
            help="Select entry",
        )
        p.add_argument(
            "-f", "--from",
            dest="_from",
            required=True,
            metavar="LOCATION",
            help="From location",
        )
        p.add_argument(
            "-t", "--to",
            dest="to",
            required=True,
            metavar="LOCATION",
            help="To location",
        )
        p.add_argument(
            "-m", "--mode",
            dest="mode",
            required=False,
            default="",
            metavar="MODE",
            help="Select user defined mode",
        )

    # subcommand show
    p_show = subparsers.add_parser(
        "show",
        help="Show rsync dry-run result",
    )
    common_args_show_sync(p_show)
    p_show.set_defaults(func=cmd_show)

    # subcommand sync
    p_sync = subparsers.add_parser(
        "sync",
        help="Execute rsync sync",
    )
    common_args_show_sync(p_sync)
    p_sync.add_argument(
        "-y", "--yes",
        dest="yes",
        action="store_true",
        help="Confirm yes",
    )
    p_sync.set_defaults(func=cmd_sync)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
