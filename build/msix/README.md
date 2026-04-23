# MSIX Packaging

Use `build/build_windows.ps1` after `neu build --release`.

## Signing placeholder

Integrate with signtool in release pipeline:

```powershell
signtool sign /fd SHA256 /a /f certificate.pfx /p <password> dist/*.msix
```

## Auto-update

Publish signed MSIX and app installer feed in enterprise deployment channel.
