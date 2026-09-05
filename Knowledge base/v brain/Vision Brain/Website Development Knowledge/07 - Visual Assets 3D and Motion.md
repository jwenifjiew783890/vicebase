---
type: note
domain: Website Development Knowledge
section: Assets
created: 2026-09-04
---

# Visual Assets, 3D and Motion

Imagery, icons, motion and 3D make a site feel alive — or make it slow and gaudy. The skill
is choosing the lightest asset that does the job, and knowing when *not* to add one.

## Choosing the right asset type

| Content | Use | Not |
| --- | --- | --- |
| Icons, logos, simple illustration | **SVG** — sharp at any size, tiny, styleable with CSS | Raster PNGs for line art |
| Photos, complex imagery | **AVIF → WebP → JPEG** fallback | PNG for photos (huge) |
| Screenshots, transparency needs | WebP/PNG | JPEG (no alpha) |
| Short looping motion | Video (`<video>` muted/autoplay/loop) or Lottie/CSS | Heavy GIF (large, low quality) |
| Data | HTML/SVG chart | Screenshot of a chart |

## Responsive, optimised media

- Serve the right size per viewport with `srcset`/`sizes`; never ship a 3000px image to a phone.
- **Always** set `width`/`height` or `aspect-ratio` — prevents layout shift (CLS).
- `loading="lazy"` below the fold; eager + `fetchpriority="high"` on the LCP image.
- Compress everything; SVGs go through an optimiser (SVGO). Icons: an inline sprite or an icon
  set ([[Website Development Knowledge/03 - Figma Workflow and Plugins|Iconify in Figma]]).
- Provide `alt` text ([[Website Development Knowledge/05 - Responsiveness Accessibility and Performance|05]]).

## Motion & animation

- Prefer **CSS transitions/animations**; they run off the main thread and keep INP low.
  Reserve JS animation (or the Web Animations API) for sequencing that CSS can't express.
- Animate cheap properties — `transform` and `opacity`. Avoid animating layout
  (`width/height/top/left`), which forces reflow and jank.
- **Always** honour `prefers-reduced-motion` — provide a reduced or no-motion path.
- Motion should have a purpose: guide attention, show state change, ease transitions. Motion
  for its own sake distracts and costs performance.

## 3D on the web — when it earns its weight

3D is powerful and expensive. Add it only when it does something 2D cannot: a product a user
should rotate and inspect, a configurable object, an immersive hero for a brand where that is
the point.

- **Do not** use 3D for decoration on a content/landing site — it costs load time, battery,
  and accessibility, and usually a good image or subtle CSS is better.
- Ask: does interactivity/rotation add real value here? If not, render the 3D to an image or a
  short video instead.

Tech when 3D is warranted:
- **WebGL / Three.js** (or React Three Fiber) is the standard runtime for interactive 3D.
- **`<model-viewer>`** is the simplest way to drop an interactive **glTF/GLB** model on a page.
- **glTF / GLB** is the web-native 3D format — compact, runtime-friendly. Export from Blender
  to GLB.
- Optimise hard: **Draco/meshopt** geometry compression, **KTX2/basis** textures, low poly
  counts, baked lighting, lazy-load the model, show a poster/fallback first.

Vision creates 3D assets with its Blender executor and exports GLB; see
[[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]] (especially
optimisation, materials, and export). This domain covers *putting them on the web*, not making
them.

## Failure modes

- A huge unoptimised hero image or an autoplaying heavy video wrecking LCP.
- 3D added for wow-factor on a site that needed a fast landing page.
- GIFs where a small muted video (or CSS) would be a fraction of the size.
- Animating `width`/`top` and causing jank.
- Motion with no reduced-motion path.
- Un-optimised GLB (raw meshes, 4K textures) shipped to the browser.

## See also

- [[3D & Blender Knowledge/00 - 3D & Blender Knowledge|3D & Blender Knowledge]]
- [[Image Knowledge/00 - Image Knowledge|Image Knowledge]]
- [[Website Development Knowledge/05 - Responsiveness Accessibility and Performance|Responsive, A11y & Performance]]

## Sources

MDN (<https://developer.mozilla.org/>, CC BY-SA 2.5) and web.dev (<https://web.dev/>) for media,
image formats and animation; glTF is a Khronos standard (<https://www.khronos.org/gltf/>);
`<model-viewer>` (<https://modelviewer.dev/>). Practitioner synthesis otherwise. See
[[Website Development Knowledge/99 - Sources and Provenance|99 · Sources]].
