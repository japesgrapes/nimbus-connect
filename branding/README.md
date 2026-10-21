# Nimbus Connect — Windows x64

Nimbus Connect is an independent source-built, Nimbus-branded RustDesk client
based on upstream **1.5.0**, commit `fada664df7a294d1d1a9ca3e7cd3637069122f17`.
This is not an official RustDesk binary.

## Identity and connection defaults

- Internal application/service/config name: `NimbusConnect`.
- Display branding, logos and Windows ProductName: `Nimbus Connect`.
- Installed executable: `nimbusconnect.exe`.
- ID server: `rustdesk.nimbusconnect.co.za`.
- Server public key: `OiHgteVB1Hk+sBd5WRgNwseYFthBc7LMZu+ESvzaTOk=`.
- Relay and API server fields: blank, matching the owner's existing client.
- No private keys, unattended passwords or API credentials are bundled.
- Defaults are not restrictions: saved settings can override them.

The internal name deliberately contains no spaces. The upstream Windows EXE
installer requires `[a-zA-Z0-9-]+` before elevation; its validation is preserved.
The earlier spaced internal identity was rejected by that check. The change
also changes the config/install/service namespace: it does not silently migrate
an existing RustDesk or old Nimbus Connect identity, history or credentials.

Identity/defaults are initialized by `src/common.rs::load_custom_client`.
Signed-custom-config validation, session authentication, encryption and permission
checks are not bypassed. The upstream custom-client update guard is retained;
updates require a new source build and acceptance test, not a Nimbus auto-updater.

## Branding and licence

- `flutter/assets/logo{,_light,_dark}.png`: horizontal Nimbus logo.
- `flutter/assets/icon.{png,ico}`: Nimbus emblem.
- `flutter/windows/runner/resources/app_icon.ico`, `res/icon.ico` and
  `res/tray-icon.ico`: Windows executable/wrapper/tray icons.
- `flutter/windows/runner/Runner.rc`: display metadata with preserved copyright.
- MSI preprocessing uses `--app-name NimbusConnect --manufacturer "Nimbus Connect"`.

Upstream licence and attribution remain intact; see `LICENCE`.
Corresponding modified source is in this repository's `nimbus-1.5.0` branch.

## Build and restricted binary distribution

`.github/workflows/nimbus-windows.yml` derives its Windows-x64-only jobs from
the pinned upstream release. The original workflows and master are not rewritten.
There are no release-publishing or signing-service calls; contents permission is
read-only. Windows project build-cache uploads are disabled to avoid retaining
unencrypted client outputs through that route. Bridge/helper artifacts contain
build inputs, not the branded client installers.

Only encrypted Nimbus installer artifacts are uploaded:

- `NimbusConnect-1.5.0-windows-x64-portable-encrypted`
- `NimbusConnect-1.5.0-windows-x64-encrypted`

Each contains one `.zip.aesgcm` file. AES-256-GCM uses a random nonce and
an owner-generated 256-bit key supplied through the Actions secret
`NIMBUS_ARTIFACT_KEY`. The key is never embedded in the client or checked into
source. CI refuses to proceed without it, encrypts before upload, and verifies
an authenticated decrypt/hash round trip. The portable encrypted package is
uploaded before MSI packaging, so an MSI failure cannot hide a successful EXE.

These encrypted blobs can be downloaded from the public repository, but cannot
be used without the key. The source remains public and can be built independently.
Do not upload the key, decrypted archives or raw EXE/MSI to GitHub. Artifacts
are retained for 14 days; usable client downloads are owner-controlled/self-hosted.

The decrypted complete ZIP contains:

- `NimbusConnect-1.5.0-windows-x64.exe`
- `NimbusConnect-1.5.0-windows-x64.msi`
- `SHA256SUMS.txt` and `LICENCE`

The portable ZIP omits the MSI. Binaries are **unsigned**. Never disable endpoint
security to run them or describe them as trusted/signed builds.

## Owner-side decryption

Install the pinned dependencies from `branding/requirements-build.txt` into a
separate Python environment, then use a protected key file (64 hexadecimal
characters; not a command-line key value):

```sh
python branding/artifact_crypto.py decrypt \
  --input NimbusConnect-1.5.0-windows-x64.zip.aesgcm \
  --output NimbusConnect-1.5.0-windows-x64.zip \
  --key-file /protected/path/build-artifacts.key
```

The output must not already exist. Check every binary against the decrypted
`SHA256SUMS.txt` before distributing it.

## Verification and acceptance

```sh
python -m unittest branding/test_branding.py branding/test_msi_preprocess.py branding/test_artifact_crypto.py -v
```

CI checks binary version/product metadata, effective defaults, real Windows
metadata probes and the actual EXE install-name safety validator. Packaging,
metadata and name-policy tests do not establish interactive installation success.

Before rollout, test the portable client on an agreed Windows PC: branding, ID
registration, outgoing/incoming sessions and relay fallback; then test the EXE's
Accept and install flow, service/shortcut creation and finally MSI installation.
Preserve the existing working RustDesk client. Do not silently install or migrate IDs.
