# OpenUSD Scene System — Standalone Knowledge

Snapshot: 2026-09.

Doel: genoeg conceptuele en API-kennis bewaren om een eigen scene layer / adapter rond OpenUSD te bouwen zonder opnieuw broncode te moeten bestuderen.

## Kernmodel

### Stage
Een `UsdStage` is de gecomposeerde scenegraph die ontstaat uit één root layer plus alle compositie-opinies daaronder. Werk in de regel tegen de Stage, niet rechtstreeks tegen losse bestanden.

Belangrijk:
- Stage presenteert de resolved/composed namespace.
- Stage heeft een root layer en optioneel session layer.
- EditTarget bepaalt naar welke layer nieuwe opinions worden geschreven.
- Save bewaart dirty contributing layers; export/flatten heeft andere semantiek.

### Prim
Een prim is een named scene-object op een absolute path zoals:

```text
/World
/World/Characters/Hero
/World/Cameras/Main
```

Een prim kan type/schema, metadata, attributes, relationships en children hebben.

Gebruik stabiele paths en een aparte interne UUID. Path kan veranderen; UUID niet.

### Property
Twee hoofdtypen:
- Attribute: getypeerde waarde, eventueel time-sampled.
- Relationship: verwijzing naar andere prims/properties.

### Schema
Schemas geven betekenis aan prims. Belangrijke families:

```text
UsdGeom    geometry, transforms, camera
UsdLux     lights
UsdShade   shader/material graph en bindings
UsdSkel    skeleton/animation
UsdPhysics / PhysX schema afhankelijk stack
```

## Layers en composition

USD's kracht zit in opinions combineren zonder de bronasset te vernietigen.

Belangrijkste mechanismen:

```text
sublayers     = lagen stapelen
references    = externe/interne asset-compositie
payloads      = references met laad/ontlaadgedrag voor working set
variants      = alternatieve configuraties
inherits      = gedeelde eigenschappen erven
specializes   = specialized afleiding
activations   = prim aan/uit
value clips   = schaalbare time-sampled animatie
```

### Sterkte
Bij composition wint de sterkere opinion volgens USD compositionregels. Bouw daarom lagen per verantwoordelijkheid, bijvoorbeeld:

```text
base_asset.usd
look.usd
animation.usd
shot.usd
ai_overrides.usd
session overrides
```

AI schrijft bij voorkeur naar een eigen override-layer. Daardoor blijven assets en artistieke bronlagen intact.

## Recommended world layout

```text
/World
  /Environment
  /Characters
  /Props
  /FX
  /Lights
  /Cameras
  /Materials
```

Gebruik `defaultPrim` voor het root-object dat een asset representeert wanneer assets los herbruikbaar moeten zijn.

## Transforms

Gebruik een Xform/Xformable-hiërarchie.

Intern normaliseren wij altijd naar:

```text
translation: vec3
rotation: quaternion
scale: vec3
space: local|world
```

USD kan meerdere xformOps en een expliciete op-order hebben. Adapter moet bestaande xformOpOrder respecteren in plaats van blind extra translate/rotate/scale properties toe te voegen.

## Geometry

Minimale geometry capability:

```text
Mesh
points
faceVertexCounts
faceVertexIndices
normals
UV primvars
color primvars
extent
subdivision metadata indien nodig
```

Voor grote assets:
- niet alles eager laden;
- payloads gebruiken;
- instancing behouden;
- geometry niet flattenen tenzij exportdoel dit vereist.

## Cameras

Canonical camera model:

```text
transform
projection: perspective|orthographic
focal_length
horizontal_aperture
vertical_aperture
focus_distance
f_stop
clipping_range
shutter timing / exposure elders indien renderer-specifiek
```

Zet filmische instellingen in een engine-onafhankelijk Camera object; adapter mappt naar UsdGeomCamera of Unreal CineCamera.

## Lighting

Canonical lights:

```text
directional/distant
point/sphere
spot/disk/cone
rect/area
dome/environment
```

Eigenschappen:

```text
intensity/exposure
color
color_temperature optional
size/radius/width/height
cone angle/softness
texture/IES optional
shadow flags renderer-specific
```

Houd fysieke lichtwaarden waar mogelijk consistent; renderer-adapter vertaalt units wanneer engines verschillen.

## Materials en UsdShade

`UsdShadeMaterial` is een container voor één of meer render contexts. Shader-netwerken leven onder de material namespace.

Canonical structuur:

```text
/World/Materials/Metal
  Material
    Shader nodes
    inputs
    outputs
```

Material binding gebeurt via `UsdShadeMaterialBindingAPI` op geometry/collections.

Belangrijk:
- materiaal kan direct of collection-based worden gebonden;
- material purpose/render context kan verschillen;
- geometry zelf kent shading niet; binding zit in UsdShade.

Voor cross-engine compatibility:
1. author eerst een portable representation (MaterialX of UsdPreviewSurface-achtig minimum);
2. voeg renderer-specific context alleen als override toe;
3. bewaar geen essentiële look uitsluitend in een proprietary shader node als portability belangrijk is.

## Variants

Gebruik variants voor discrete keuzestaten, bijvoorbeeld:

```text
costume = casual|formal
weather = dry|rain|snow
lod = high|medium|low
look = realistic|stylized
```

Gebruik variants niet als vervanging voor continue animatie of dynamische runtime state.

## References vs Payloads

Reference:
- composition aanwezig zodra stage geladen wordt.

Payload:
- composition kan expliciet unloaded blijven;
- goed voor grote environments en assets.

Regel: als een asset voor scene-navigation niet altijd nodig is, overweeg payload.

## Instancing

Gebruik instancing voor veel identieke objecten. AI-world generation moet object-identiteit en instance-prototype scheiden:

```text
prototype asset
instance transform
instance-specific lightweight metadata
```

Vermijd unieke volledige meshkopieën voor duizenden identieke props.

## Tijd en animatie

USD attributes kunnen values per timeCode hebben.

Intern gebruiken wij:

```text
fps/timeCodesPerSecond
start_time
end_time
samples: time -> value
```

Scheiding:
- structurele scene state in base/shot layers;
- animation samples in animation layer;
- tijdelijke AI preview in session/override layer.

## Flattening

Flattening produceert een eindlaag met gecomposeerde data en verwijdert vrijwel alle authoring/compositionstructuur.

Gebruik flatten alleen voor:
- export naar een consument die composition niet aankan;
- immutable delivery snapshot;
- debugging vergelijking.

Niet gebruiken als primaire editable master.

## Asset paths

Maak een AssetResolver-laag in onze architectuur. Geen absolute lokale Windows paths hard-coden.

Canonical asset URI concept:

```text
asset://characters/hero/v003/hero.usd
asset://materials/metal/brushed.mtlx
```

Resolver vertaalt naar local disk, object storage, Nucleus/cloud of andere locatie.

## Authoring-transactie

Voor AI-mutaties:

```text
1. validate command
2. select AI edit layer
3. verify expected world version
4. author opinions
5. compose/read back
6. validate resulting prim/state
7. save/checkpoint
8. increment world version
9. emit event
```

Bij fout: layer-mutatie terugdraaien of naar vorige checkpoint terugkeren.

## Minimal API operations voor onze USDAdapter

```text
open_stage(uri)
create_stage(uri)
save_stage()
set_edit_layer(layer_id)
get_prim(path)
create_prim(path, schema)
remove_prim(path)
set_attribute(path, name, value, time=None)
get_attribute(path, name, time=None)
set_relationship(path, name, targets)
set_transform(path, transform)
create_reference(path, asset_uri, target_prim=None)
set_payload(path, asset_uri)
set_variant(path, set_name, value)
bind_material(geom_path, material_path)
load_payload(path)
unload_payload(path)
list_children(path)
export_snapshot(uri, flatten=False)
```

## Performance rules

- Use payloads voor grote assetgroepen.
- Preserve instancing.
- Vermijd volledige stage traversal per frame.
- Cache paths/handles waar veilig.
- Batch writes.
- Schrijf niet elke physics frame naar disk; runtime state apart houden en alleen checkpoints authoren.
- Gebruik change notifications/events in plaats van constant polling waar beschikbaar.

## Fouten die we voorkomen

```text
geen absolute asset paths
geen blind flattenen
geen AI writes in bronasset-layer
geen path als enige permanente identiteit
geen volledige mesh duplicatie voor instances
geen renderer-proprietary materiaal als enige truth
geen save aannemen zonder compose/readback check
```
