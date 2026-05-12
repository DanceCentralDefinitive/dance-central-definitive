# Changelog

All notable changes to this project are documented here.

## [v0.0.4] - 2026-05-12

### Fixed

- Minor fixes

## [v0.0.3] - 2026-05-12

### Added

- Disabled motion blur in all menus.
- Added instructions for non-technical users / players
- Added ability to enable/disable depth buffers

### Changed

- Xenia patch is now static and works for all versions
- Improved and simplified the build process
- Improved CI/CD and automatic code verification


### Fixed

- Autoplay now also fakes player being active.
- Minor DTA fixes

## [v0.0.2] - 2026-05-11

### Added

- Release packaging now includes `out/deluxe.xex` alongside the generated patch archive.
- Tag release builds stamp `src/config/ham_version.dta` with the tag name and short commit hash.
- Automatic docs publishing runs from the `docs/` subdirectory.
- DTA/build validation workflow runs on pushes that touch source or build-related files.

### Changed

- Release archives now pull `patch_xbox.hdr` and `patch_xbox_0.ark` from `out/gen/`.
- Docs publishing workflow now runs from the MkDocs project root in `docs/`.

## [v0.0.1] - 2026-05-11

### Added

- Initial public release packaging workflow.
- Basic project documentation, build instructions, and helper script guidance.
- MIT licensing notice for original project-authored content.

### Notes

- Stock/original game assets and binaries remain owned by their respective rights holders.
- This project is intended as a non-commercial fan preservation effort.
