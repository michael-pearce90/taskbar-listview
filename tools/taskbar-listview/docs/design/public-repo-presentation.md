# Public Repository Presentation

This note records the legacy public presentation wording for the Taskbar
ListView module. The root repository presentation now belongs to TechTools for
Windows. This note does not change module scope, implementation state, or
support status.

## Repository Description

When Taskbar ListView is described as a module, keep the module description
close to:

> Proposed list view for grouped Windows 11 taskbar clicks.

## Social Preview Source

The repo-owned source artwork is
[`assets/social-preview.svg`](../../../../assets/social-preview.svg). It is a
1280 by 640 SVG containing original text and generic interface shapes for the
TechTools for Windows suite. It does not use copied screenshots, platform
branding, or application branding.

The source communicates the suite identity and module roadmap. It must not be
presented as a screenshot or as evidence of implemented behaviour.

## Manual Export

Use the SVG as the source artwork and export a PNG manually only when updating
the repository preview:

1. Open `assets/social-preview.svg` in a trusted local vector editor or
   browser-based export workflow.
2. Export at exactly 1280 by 640 pixels.
3. Use PNG format with the full artwork visible and no added branding.
4. Review the exported image for clipped text, font substitution, colour
   changes, and accidental metadata.
5. Keep the SVG as the repository source of truth. Do not commit an exported
   PNG unless the repository later adopts and documents a repeatable local
   export tool.

## GitHub Upload

Upload the exported image manually through the repository settings:

1. Open the repository on GitHub.
2. Select **Settings**.
3. In **General**, find **Social preview**.
4. Select **Edit**, then **Upload an image**.
5. Choose the reviewed 1280 by 640 PNG and save the change.
6. Reopen the public repository page and verify that the title and subtitle
   remain readable at preview size.

Uploading the image is a GitHub settings change and is intentionally not
performed by this documentation branch.

## Presentation Guardrails

- Keep the root display name **TechTools for Windows**.
- Keep Taskbar ListView described as experimental.
- State that there are no supported Windows builds and no runtime yet.
- Treat future private Explorer and taskbar internals as liable to break after
  Windows updates.
- Keep the one-purpose grouped-click title-list scope visible.
- Keep Browser Choice Tools clearly marked as proposed, with no code yet.
- Do not imply that the conceptual artwork is working software.
- Do not add copied product interfaces, platform marks, or application marks.
