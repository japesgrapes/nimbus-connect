# Nimbus Connect — Windows x64

Nimbus Connect is a source-built, Nimbus-branded RustDesk client based on the
upstream **1.5.0** release (commit `fada664df7a294d1d1a9ca3e7cd3637069122f17`).
This is an independent build, not an official RustDesk binary.

## Built-in defaults

- Application name: `Nimbus Connect`
- ID server: `rustdesk.nimbusconnect.co.za`
- Server public key: `OiHgteVB1Hk+sBd5WRgNwseYFthBc7LMZu+ESvzaTOk=`
- Relay server and API server fields: blank, matching the owner's existing client.
- No passwords, unattended-access secrets, private server keys or API tokens are bundled.
- These are defaults, not restrictions: saved client settings can override them.
- The existing upstream custom-client update guard is retained. Updates are rebuilt
  and tested from source; there is no Nimbus automatic-update service yet.

The name and connection defaults are initialized at the start of
`src/common.rs::load_custom_client`. RustDesk's signed-custom-config validation,
remote-session authentication, encryption and permissions are not bypassed.

## Branding surface

- `flutter/assets/logo{,_light,_dark}.png`: horizontal Nimbus logo.
- `flutter/assets/icon.{png,ico}`: Nimbus cloud/circuit emblem.
- `flutter/windows/runner/resources/app_icon.ico`, `res/icon.ico` and
  `res/tray-icon.ico`: Windows executable, wrapper and tray icons.
- `flutter/windows/runner/Runner.rc`: Nimbus Windows product metadata; upstream
  copyright text is preserved.
- The CI packaging step renames the built executable to `nimbus connect.exe` to
  match the application name used by the existing Windows install/service logic.
- Installer preprocessing receives `--app-name "Nimbus Connect"` and
  `--manufacturer "Nimbus Connect"`.

Upstream license files and attribution remain intact. See `LICENCE` in the root.
Corresponding modified source is available in this repository's `nimbus-1.5.0` branch.

## Build

`.github/workflows/nimbus-windows.yml` contains a Windows-x64-only derivative of
upstream's official 1.5.0 jobs, using the original pinned toolchain/actions.
It runs on pushes to `nimbus-1.5.0`, and has a manual-dispatch trigger.
The original upstream workflows and `master` branch are not rewritten.
No automatic releases or signing-service calls are performed. The jobs use
read-only repository permissions and upload build artifacts for 14 days.

Expected artifact: `NimbusConnect-1.5.0-windows-x64`, containing:

- `NimbusConnect-1.5.0-windows-x64.exe`: self-extracting client.
- `NimbusConnect-1.5.0-windows-x64.msi`: installer.
- `SHA256SUMS.txt` and the upstream `LICENCE`.

These binaries are **unsigned**. Do not distribute them as trusted/signed builds.
Windows reputation warnings may occur. Do not disable endpoint security to run them.

## Verification and acceptance

Local source/asset contracts:

```sh
python3 -m unittest branding/test_branding.py -v
```

CI also checks Windows product metadata, executes the binary with `--version`,
and runs a Rust test of the effective app name/server/public-key/blank fields.
A successful build is not a real remote-session test.

Before rollout: test the portable client on an agreed Windows PC, verify name,
logos, ID registration, outgoing connection, incoming permission/authentication,
relay fallback, and finally the installer/service. Preserve the existing working
RustDesk client until these checks pass. Do not silently install or migrate IDs.
