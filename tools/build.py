#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import sys
import shlex
import subprocess
from lib.ninja_syntax import Writer as NinjaWriter
from lib.xex_editor import XEXEditor
import shutil
from io import StringIO

try:
    import tomllib
except ModuleNotFoundError:
    raise Exception("tomllib module not found. Please use Python 3.11 or newer.")

# Ninja writer
ninja_build_file = StringIO()
ninja = NinjaWriter(ninja_build_file)

# Paths in _ark/dx/custom_textures that should generate list dtbs
custom_texture_paths = []

# Base Title ID for Dance Central 3

XEX_INFO = {
    "default_id": 0x373307D9,
    "vanilla": {
        "retail": "vanilla.xex",
        "debug": "vanilla_debug.xex",
    },
    "deluxe": {"retail": "deluxe.xex", "debug": "deluxe_debug.xex"},
}

# Version map
VERSION_MAP = {
    "vanilla": ("vanilla", "retail"),
    "vanilla_debug": ("vanilla", "debug"),
    "deluxe": ("deluxe", "retail"),
    "deluxe_debug": ("deluxe", "debug"),
    0: ("deluxe", "retail"),
    1: ("vanilla", "retail"),
    2: ("deluxe", "debug"),
    3: ("vanilla", "debug"),
}

# Xenia run map

XENIA_RUN_MAP = {
    0: None,
    1: ("deluxe.xex"),
    2: ("vanilla.xex"),
    3: ("deluxe_debug.xex"),
    4: ("vanilla_debug.xex"),
}


def get_dtacheck_executable():
    match sys.platform:
        case "win32":
            return Path("tools", "windows", "dtacheck.exe")
        case "darwin":
            return Path("tools", "macos", "dtacheck")
        case _:
            return Path("tools", "linux", "dtacheck")


def ark_file_filter(file: Path):
    if file.is_dir():
        return False
    if file.suffix.endswith("_ps3"):
        return False
    if file.suffix.endswith("_wii"):
        return False
    if any(file.suffix.endswith(suffix) for suffix in ["_ps2", "vgs"]):
        return False

    return True


def prepare_src(config):
    obj_src_dir = Path("obj", "src")
    obj_src_dir.mkdir(parents=True, exist_ok=True)
    src_dir = Path(config["source"])

    if not src_dir.exists():
        raise FileNotFoundError(f"Source directory '{src_dir}' does not exist.")

    for src_file in filter(ark_file_filter, src_dir.rglob("*")):
        if src_file.is_file():
            rel_path = src_file.relative_to(src_dir)

            # Check if it's a milo file
            if ".milo_" in src_file.name:
                dest = Path(obj_src_dir / rel_path.parent / "gen" / rel_path.name)
            else:
                dest = Path(obj_src_dir / rel_path)

            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dest)


def get_git_info(repo_path: Path = Path('.')):
    try:
        tag = (
            subprocess.check_output([
                "git",
                "describe",
                "--tags",
                "--abbrev=0",
            ], cwd=repo_path)
            .strip()
            .decode()
        )
    except Exception:
        # Fallback to commit short hash if no tag is available
        try:
            tag = (
                subprocess.check_output([
                    "git",
                    "rev-parse",
                    "--short",
                    "HEAD",
                ], cwd=repo_path)
                .strip()
                .decode()
            )
        except Exception:
            tag = "unknown"

    try:
        commit = (
            subprocess.check_output([
                "git",
                "rev-parse",
                "--short",
                "HEAD",
            ], cwd=repo_path)
            .strip()
            .decode()
        )
    except Exception:
        commit = ""

    return tag, commit


def inject_versions_into_obj_src(obj_src_root: Path, tag: str, commit: str):
    try:
        branch = (
            subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=Path(".")
            )
            .strip()
            .decode()
        )
    except Exception:
        branch = ""

    ham_path = obj_src_root.joinpath("config", "ham_version.dta")
    if ham_path.exists():
        try:
            ham_path.write_text(f'"Definitive: {tag} ({branch} / {commit}) / DC3: 1221004"\n')
        except Exception:
            pass

    dx_ver_path = obj_src_root.joinpath("dx", "dx_version.dta")
    if dx_ver_path.exists():
        try:
            build_time = (
                subprocess.check_output(
                    [
                        sys.executable,
                        "-c",
                        "from datetime import datetime; print(datetime.utcnow().replace(microsecond=0).isoformat() + 'Z')",
                    ]
                )
                .strip()
                .decode()
            )
        except Exception:
            build_time = ""

        try:
            dx_ver_path.write_text(
                "\n".join(
                    [
                        f'(dx_version "{tag}")',
                        f'(dx_tag "{tag}")',
                        f'(dx_commit "{commit}")',
                        f'(dx_branch "{branch}")',
                        f'(dx_build_time "{build_time}")',
                    ]
                )
                + "\n"
            )
        except Exception:
            pass


def prepare_ninja(config):
    ninja.variable("ark_version", "-v 6")
    ninja.variable("dtb_encrypt", "-e")
    ninja.variable("ark_encrypt", "-e")
    ninja.variable("miloVersion", "--miloVersion 26")

    match sys.platform:
        case "win32":
            ninja.variable("silence", ">nul")
            ninja.rule("copy", "cmd /c copy $in $out $silence", description="COPY $in")
            ninja.rule(
                "bswap",
                "tools\\windows\\swap_art_bytes.exe $in $out",
                description="BSWAP $in",
            )
            ninja.variable("superfreq", "tools\\windows\\superfreq.exe")
            ninja.variable("arkhelper", "tools\\windows\\arkhelper.exe")
            ninja.variable("dtab", "tools\\windows\\dtab.exe")
            ninja.variable("dtacheck", "tools\\windows\\dtacheck.exe")
        case "darwin":
            ninja.variable("silence", "> /dev/null")
            ninja.rule("copy", "cp $in $out", description="COPY $in")
            ninja.rule(
                "bswap",
                "python3 tools/python/swap_rb_art_bytes.py $in $out",
                description="BSWAP $in",
            )
            ninja.rule(
                "version",
                "python3 tools/python/gen_version.py $out",
                description="Writing version info",
            )
            ninja.variable("superfreq", "tools/macos/superfreq")
            ninja.variable("arkhelper", "tools/macos/arkhelper")
            ninja.variable("dtab", "tools/macos/dtab")
            # dtacheck needs to be compiled for mac
            ninja.variable("dtacheck", "true")
        case "linux":
            ninja.variable("silence", "> /dev/null")
            ninja.rule("copy", "cp --reflink=auto $in $out", description="COPY $in")
            ninja.rule("bswap", "tools/linux/swap_art_bytes $in $out", "BSWAP $in")
            ninja.rule(
                "version",
                "python3 tools/python/gen_version.py $out",
                description="Writing version info",
            )
            ninja.variable("superfreq", "tools/linux/superfreq")
            ninja.variable("arkhelper", "tools/linux/arkhelper")
            ninja.variable("dtab", "tools/linux/dtab")
            ninja.variable("dtacheck", "tools/linux/dtacheck")

    ark_dir = Path("obj", "ark")
    out_dir = Path(config["output"], "gen")

    ninja.rule(
        "ark",
        f"$arkhelper dir2ark -n patch_xbox $ark_version $ark_encrypt -s 4073741823 --logLevel error {ark_dir} {out_dir}",
        description="Building ark",
    )

    ninja.rule(
        "sfreq",
        f"$superfreq png2tex -l error $miloVersion --platform $platform $in $out",
        description="SFREQ $in",
    )
    ninja.rule("dtab_serialize", "$dtab -b $in $out", description="DTAB SER $in")
    ninja.rule(
        "dtab_encrypt", f"$dtab $dtb_encrypt $in $out", description="DTAB ENC $in"
    )
    ninja.build("_always", "phony")


def prepare_build(config):
    ark_files = []
    obj_src_dir = Path("obj", "src")
    ark_dir = Path("obj", "ark")
    raw_dir = Path("obj", "raw")

    for f in filter(ark_file_filter, obj_src_dir.rglob("*")):
        match f.suffixes:
            case [".png"]:
                index = f.parts.index("src")
                output_directory = ark_dir.joinpath(*f.parent.parts[index + 1:])
                target_filename = Path("gen", f.stem + ".png_xbox")
                xbox_directory = ark_dir.joinpath(*f.parent.parts[index + 1:])
                xbox_output = xbox_directory.joinpath(target_filename)
                ninja.build(
                    str(xbox_output), "sfreq", str(f), variables={"platform": "x360"}
                )
                ark_files.append(str(xbox_output))
            case [".dta"]:
                target_filename = Path("gen", f.stem + ".dtb")
                stamp_filename = Path("gen", f.stem + ".dtb.checked")

                index = f.parts.index("src")
                output_directory = ark_dir.joinpath(*f.parent.parts[index + 1:])
                serialize_directory = raw_dir.joinpath(*f.parent.parts[index + 1:])

                serialize_output = serialize_directory.joinpath(target_filename)
                encryption_output = output_directory.joinpath(target_filename)
                stamp = serialize_directory.joinpath(stamp_filename)
                stamp.parent.mkdir(parents=True, exist_ok=True)
                stamp.touch()
                ninja.build(
                    str(serialize_output),
                    "dtab_serialize",
                    str(f),
                    implicit=[str(stamp), "_always"],
                )
                ninja.build(
                    str(encryption_output), "dtab_encrypt", str(serialize_output)
                )
                ark_files.append(str(encryption_output))
            case _:
                index = f.parts.index("src")
                out_path = ark_dir.joinpath(*f.parts[index + 1 :])
                ninja.build(str(out_path), "copy", str(f))
                ark_files.append(str(out_path))

    hdr = str(Path("out", "patch_xbox" + ".hdr"))
    ark = str(Path("out", "patch_xbox" + "_" + "0" + ".ark"))

    ninja.build(
        ark,
        "ark",
        implicit=ark_files,
        implicit_outputs=[hdr],
    )

    return hdr


def run_dtacheck(config):
    dtacheck_exe = get_dtacheck_executable()

    for dta_file in Path("obj", "src").rglob("*.dta"):
        result = subprocess.run(
            [str(dtacheck_exe), str(dta_file), ".dtacheckfns"],
            capture_output=True,
            text=True,
        )
        combined_output = (result.stdout or "") + (result.stderr or "")
        has_checker_error = "error:" in combined_output.lower()

        if result.returncode != 0 or has_checker_error:
            if config["allow_dtacheck_errors"]:
                print(f"DTACHECK reported issues in {dta_file}")
                if combined_output.strip():
                    print(combined_output.rstrip())
                continue

            message = [
                f"DTACHECK failed for {dta_file}.",
                f"Exit code: {result.returncode}",
            ]
            if combined_output.strip():
                message.append(combined_output.rstrip())
            raise RuntimeError("\n".join(message))


def prepare_includes(config):
    build_files = []
    include_dir = Path(config["includes"])
    for f in filter(lambda x: x.is_file(), include_dir.rglob("*")):
        index = f.parts.index(include_dir.name)
        out_path = Path(config["output"]).joinpath(*f.parts[index + 1 :])
        ninja.build(str(out_path), "copy", str(f))
        build_files.append(str(out_path))

    return build_files


def prepare_binaries(config):
    obj_bin_dir = Path("obj", "bin")
    obj_bin_dir.mkdir(parents=True, exist_ok=True)
    bin_dir = Path(config["binaries"])

    build_files = []

    # Copy all binaries first
    for f in filter(lambda x: x.is_file(), bin_dir.rglob("*")):
        index = f.parts.index(bin_dir.name)
        rel_path = Path(*f.parts[index + 1 :])
        out_path = Path(config["output"]) / rel_path

        # Check if this is a XEX file we need to modify
        to_build = False

        for version in config["versions"]:
            variant, build_type = VERSION_MAP[version]
            xex_name = XEX_INFO[variant][build_type]

            if rel_path.name == xex_name:
                to_build = True
                break

        if to_build:
            # Copy to obj/bin first for modification
            temp_xex = obj_bin_dir / rel_path.name
            shutil.copy2(f, temp_xex)

            build_files.append(str(temp_xex))

    return build_files


def clean(config):
    if config["clean"]:
        if Path("build.ninja").exists():
            os.remove("build.ninja")
        if Path("obj").exists():
            shutil.rmtree("obj")


def copy_patch_file(config):
    source_patch = Path("assets", "373307D9 - Dance Central 3.patch.toml")
    
    if config["patch_output"]:
        dest = Path(config["patch_output"]) / source_patch.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_patch, dest)
    
    if config["xenia_root"]:
        xenia_patches_dir = Path(config["xenia_root"]) / "patches"
        xenia_patches_dir.mkdir(parents=True, exist_ok=True)
        dest = xenia_patches_dir / source_patch.name
        shutil.copy2(source_patch, dest)


def launch_xenia(config, xex_files):
    if config["xenia_run"] == 0 or not config["xenia_path"]:
        return

    run_xex_name = XENIA_RUN_MAP[config["xenia_run"]]
    if run_xex_name is None:
        return

    run_xex_path = Path(config["output"]) / run_xex_name
    if not run_xex_path.exists():
        print(f"Error: XEX to run with Xenia '{run_xex_path}' does not exist.")
        return

    xenia_exe = Path(config["xenia_path"])
    extra_args = shlex.split(
        config["xenia_args"],
        posix=(sys.platform != "win32"),
    )
    cmd = [str(xenia_exe), str(run_xex_path), *extra_args]
    print(f"Running Xenia: {' '.join(shlex.quote(part) for part in cmd)}")

    if sys.platform == "win32":
        subprocess.Popen(cmd, creationflags=subprocess.DETACHED_PROCESS)
    else:
        subprocess.Popen(cmd)


def run_build(config):
    obj_dir = Path("obj")
    if obj_dir.exists():
        shutil.rmtree(obj_dir)
    obj_dir.mkdir(parents=True, exist_ok=True)

    out_dir = Path(config["output"])
    if (config["clean"]):
        if out_dir.exists():
            shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    build_files = []

    prepare_src(config)
    # Inject current git tag/commit into copied src files so build contains correct versions
    try:
        tag, commit = get_git_info(Path('.'))
        inject_versions_into_obj_src(Path('obj', 'src'), tag, commit)
    except Exception:
        # Non-fatal: continue even if injection fails
        pass
    run_dtacheck(config)
    prepare_ninja(config)

    hdr = prepare_build(config)
    build_files.append(hdr)

    if config["includes"]:
        include_files = prepare_includes(config)
        build_files.extend(include_files)

    xex_files = prepare_binaries(config)

    for xex in xex_files:
        shutil.copy2(xex, out_dir / Path(xex).name)

    ninja.build("all", "phony", build_files)

    with open("build.ninja", "w+") as f:
        ninja_build_file.seek(0)
        shutil.copyfileobj(ninja_build_file, f)

    # Execute build and stop immediately on failure.
    match sys.platform:
        case "win32":
            result = subprocess.run(["tools\\windows\\ninja.exe", "-f", "build.ninja"])
        case "darwin":
            result = subprocess.run(["tools/macos/ninja", "-f", "build.ninja"])
        case "linux":
            result = subprocess.run(["tools/linux/ninja", "-f", "build.ninja"])

    if result.returncode != 0:
        raise RuntimeError(f"Build failed: ninja exited with code {result.returncode}")

    # Post build
    clean(config)

    # Copy patch file to output locations
    copy_patch_file(config)

    # Launch Xenia if requested
    launch_xenia(config, xex_files)


def main():
    parser = argparse.ArgumentParser(description="Dance Central 3 Deluxe Build Tool")

    parser.add_argument(
        "source",
        type=Path,
        help="Path to deluxe source directory (default: src)",
        default=Path("src"),
    )
    parser.add_argument(
        "binaries",
        type=Path,
        help="Path to game binaries directory (default: bin)",
        default=Path("bin"),
    )
    parser.add_argument("--debug", action="store_true", help="Include debug versions")
    parser.add_argument(
        "--vanilla",
        action="store_true",
        help="Include vanilla versions",
    )
    parser.add_argument(
        "--includes",
        type=Path,
        default=None,
        help="Optional directory with additional files to include in build (like original vanilla arks etc.)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("out"),
        help="Output directory (default: out)",
    )
    parser.add_argument(
        "--clean",
        default=False,
        action="store_true",
        help="Cleans cache after build",
    )
    parser.add_argument(
        "--allow-dtacheck-errors",
        action="store_true",
        help="Do not fail the build when dtacheck reports errors",
    )
    parser.add_argument(
        "--patch-output",
        type=Path,
        default=None,
        help="Directory to copy Xenia patch to",
    )
    parser.add_argument(
        "--xenia-root",
        type=Path,
        default=None,
        help="Path to Xenia root directory (will copy patch to patches/ subdirectory)",
    )
    parser.add_argument(
        "--cwd",
        type=Path,
        default=Path("."),
        help="Current working directory",
    )
    xenia_group = parser.add_argument_group("xenia testing", "Run built XEX in Xenia")
    xenia_group.add_argument("--xenia-path", type=Path, help="Path to Xenia executable")
    parser.add_argument(
        "--xenia-run",
        type=int,
        choices=range(5),
        default=0,
        help="Game to run with Xenia: 0=None (Default), 1=Deluxe, 2=Vanilla, 3=Deluxe Debug, 4=Vanilla Debug",
    )
    xenia_group.add_argument(
        "--xenia-args",
        type=str,
        help="Additional arguments to pass to Xenia",
        default="",
    )

    args = parser.parse_args()

    # Determine which versions to build
    versions_to_build = []

    if args.vanilla:
        versions_to_build.append("vanilla")
        if args.debug:
            versions_to_build.append("vanilla_debug")

    # Always include deluxe (at least one version needed)
    versions_to_build.append("deluxe")
    if args.debug:
        versions_to_build.append("deluxe_debug")

    # Check if Xenia location exist
    if args.xenia_path:
        if not args.xenia_path.exists():
            print(f"Error: Xenia executable '{args.xenia_path}' does not exist.")
            sys.exit(1)

    # Print build configuration
    print("Build Configuration:")
    print(f"  Source: {args.source}")
    print(f"  Output: {args.output}")
    print(f"\nVersions to build:")
    for version in versions_to_build:
        print(f"  {version}")

    # Return config for use in ninja generation
    return {
        "source": args.source,
        "binaries": args.binaries,
        "output": args.output,
        "includes": args.includes,
        "versions": versions_to_build,
        "clean": args.clean,
        "allow_dtacheck_errors": args.allow_dtacheck_errors,
        "patch_output": args.patch_output,
        "xenia_root": args.xenia_root,
        "xenia_path": args.xenia_path,
        "xenia_run": args.xenia_run,
        "xenia_args": args.xenia_args,
    }


if __name__ == "__main__":
    config = main()

    run_build(config)
