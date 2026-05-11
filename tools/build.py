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
    ninja.rule("dtacheck", "$dtacheck $in .dtacheckfns", description="DTACHECK $in")
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
                ninja.build(str(stamp), "dtacheck", str(f))
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


def render_template(template_path, output_path, **context):
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Process each context variable
    for key, value in context.items():
        placeholder = f"{{{key}}}"

        if placeholder in content:
            if isinstance(value, list):
                # Format list items for TOML array
                formatted_items = ",\n".join(f'    "{item}"' for item in value)
                content = content.replace(placeholder, formatted_items)
            else:
                # Simple string/number substitution
                content = content.replace(placeholder, str(value))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


def handle_xenia(config, xex_files):
    if not config["xenia_path"]:
        return

    if config["xenia_patch"]:
        # Prepare Xenia patch
        xenia_template_path = Path("assets", "xenia_patch_template.toml")
        xenia_patch_content_path = Path("assets", "xenia_patch_content.toml")
        patch_content_body = (
            xenia_patch_content_path.read_text(encoding="utf-8").strip() + "\n"
        )
        xenia_hashes = {
            "vanilla.xex": "A9FAAA8E4E739E19",
            "deluxe.xex": "98552AC419B4C690",
            "deluxe_debug.xex": "6B15C22CA94CC2E1",
            "vanilla_debug.xex": "8D7A4A25A9EB6634",
        }

        xenia_root = Path(config["xenia_path"]).parent
        patches_dir = xenia_root / "patches"
        patches_dir.mkdir(exist_ok=True, parents=True)

        def append_hash_entry(existing_text: str, new_hash: str) -> str:
            """Insert a missing module hash into the existing hash array while preserving formatting."""
            if not new_hash:
                return existing_text

            lines = existing_text.splitlines()
            hash_start = next(
                (i for i, line in enumerate(lines) if line.strip().startswith("hash")),
                None,
            )

            if hash_start is None:
                block = ["hash = [", f'    "{new_hash}"', "]"]
                prefix = (
                    "\n" if not existing_text.endswith("\n") and existing_text else ""
                )
                return existing_text + prefix + "\n".join(block) + "\n"

            closing_idx = None
            for i in range(hash_start, len(lines)):
                if lines[i].strip().startswith("]"):
                    closing_idx = i
                    break

            if closing_idx is None:
                # Malformed block, fall back to appending a new block at the end
                block = ["hash = [", f'    "{new_hash}"', "]"]
                prefix = (
                    "\n" if not existing_text.endswith("\n") and existing_text else ""
                )
                return existing_text + prefix + "\n".join(block) + "\n"

            # Ensure previous entry ends with a comma when needed
            prev_idx = closing_idx - 1
            while prev_idx > hash_start and lines[prev_idx].strip() == "":
                prev_idx -= 1

            if prev_idx >= hash_start:
                stripped = lines[prev_idx].rstrip()
                if stripped and not stripped.endswith(",") and stripped.strip() != "[":
                    lines[prev_idx] = stripped + ","

            # Match indentation of previous non-empty line or default to 4 spaces
            indent_source = lines[prev_idx] if prev_idx >= 0 else "    "
            indent = (
                indent_source[: len(indent_source) - len(indent_source.lstrip())]
                or "    "
            )

            lines.insert(closing_idx, f'{indent}"{new_hash}"')
            return "\n".join(lines) + ("\n" if existing_text.endswith("\n") else "")

        for xex_path in xex_files:
            title_id = XEX_INFO["default_id"]
            module_hash = xenia_hashes.get(Path(xex_path).name, "")

            patch_file = patches_dir / f"{title_id} - Dance Central 3.patch.toml"

            if patch_file.exists():
                existing = patch_file.read_text(encoding="utf-8")

                try:
                    parsed = tomllib.loads(existing) if tomllib else None
                    existing_hashes = set(parsed.get("hash", [])) if parsed else set()
                except Exception:
                    existing_hashes = set()

                needs_hash = bool(module_hash and module_hash not in existing_hashes)
                needs_patch_body = "### - DC3DX_v1 - ###" not in existing

                updated = existing
                if needs_hash:
                    updated = append_hash_entry(updated, module_hash)

                if needs_patch_body:
                    if not updated.endswith("\n"):
                        updated += "\n"
                    updated += "\n" + patch_content_body

                if updated != existing:
                    patch_file.write_text(updated, encoding="utf-8")
            else:
                render_template(
                    xenia_template_path,
                    patch_file,
                    title_id=title_id,
                    hashes=[module_hash],
                    patch_content=patch_content_body,
                )

    if config["xenia_run"] != 0:
        run_xex_name = XENIA_RUN_MAP[config["xenia_run"]]
        if run_xex_name is None:
            return

        if not config["xenia_path"]:
            print("Error: --xenia-run requires --xenia-path.")
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

    # Handle Xenia patching & running
    handle_xenia(config, xex_files)


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
        "--xenia-patch",
        action="store_true",
        help="Adds a Xenia patch to the given Xenia installation (can override existing DC3 / DC3DX patch!)",
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
        "xenia_path": args.xenia_path,
        "xenia_run": args.xenia_run,
        "xenia_args": args.xenia_args,
        "xenia_patch": args.xenia_patch,
    }


if __name__ == "__main__":
    config = main()

    run_build(config)
