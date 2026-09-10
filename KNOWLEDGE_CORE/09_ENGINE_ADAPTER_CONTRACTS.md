# Canonical Engine Adapter Contracts

Doel: één vaste taal tussen onze AI/orchestrator en iedere toekomstige 3D/game engine.

Engine-specifieke SDK namen mogen veranderen; deze interne contracten blijven stabiel.

## Capability manifest

```json
{
  "engine": "unreal",
  "engine_version": "5.x",
  "adapter_version": "1.0.0",
  "mode": "editor|runtime|headless",
  "capabilities": {
    "scene_read": true,
    "scene_write": true,
    "asset_import": true,
    "materials": true,
    "animation": true,
    "physics": true,
    "sequencer": true,
    "realtime_events": true,
    "preview_render": true,
    "final_render": true,
    "path_tracing": false,
    "remote_streaming": false
  }
}
```

Capabilities zijn runtime facts, geen hard-coded aannames.

## Transform

```json
{
  "translation": [0.0, 0.0, 0.0],
  "rotation_quat": [0.0, 0.0, 0.0, 1.0],
  "scale": [1.0, 1.0, 1.0],
  "space": "local"
}
```

Adapter doet unit/axis/handedness conversie.

## Entity

```json
{
  "entity_id": "uuid",
  "name": "Hero",
  "asset_id": "asset-hero-v3",
  "parent_id": null,
  "transform": {},
  "tags": ["hero_character"],
  "visible": true,
  "material_bindings": [],
  "animation": null,
  "physics": null,
  "metadata": {}
}
```

`metadata` krijgt alleen kleine veilige extensies; geen secrets of willekeurige blobs.

## Asset

```json
{
  "asset_id": "uuid",
  "version": 3,
  "kind": "mesh",
  "uri": "asset://props/chair/v003/chair.usd",
  "hash": "sha256:...",
  "units": "meter",
  "up_axis": "Y",
  "forward_axis": "-Z",
  "provenance": {
    "source": "generated|owned|licensed",
    "license": "..."
  }
}
```

## Material

```json
{
  "material_id": "uuid",
  "model": "pbr_metallic_roughness",
  "base_color": [1.0,1.0,1.0,1.0],
  "metallic": 0.0,
  "roughness": 0.5,
  "emissive": [0.0,0.0,0.0],
  "opacity": 1.0,
  "ior": 1.5,
  "clearcoat": 0.0,
  "sheen": 0.0,
  "textures": [],
  "graph_uri": null,
  "style_tags": []
}
```

## Texture

```json
{
  "uri": "asset://textures/wood_basecolor.ktx2",
  "semantic": "baseColor",
  "color_space": "srgb",
  "uv_set": 0,
  "channels": "rgba",
  "normal_y": null
}
```

Voor normal map:

```text
semantic=normal
color_space=data/linear
normal_y=positive|negative
```

## Light

```json
{
  "light_id": "uuid",
  "type": "directional|point|spot|rect|dome",
  "transform": {},
  "intensity": 1.0,
  "unit": "engine_normalized|lux|lumens|candela|nits",
  "color": [1.0,1.0,1.0],
  "temperature_k": null,
  "size": {},
  "cone": {},
  "casts_shadows": true,
  "volumetric": 1.0
}
```

Adapter rapporteert welke units exact worden ondersteund.

## Camera

```json
{
  "camera_id": "uuid",
  "transform": {},
  "projection": "perspective",
  "focal_length_mm": 50.0,
  "sensor_width_mm": 36.0,
  "sensor_height_mm": 20.25,
  "aperture_f": 2.8,
  "focus_distance_m": 4.0,
  "near_clip_m": 0.05,
  "far_clip_m": 10000.0
}
```

## Animation clip

```json
{
  "clip_id": "uuid",
  "asset_id": "anim-walk-v2",
  "duration_s": 2.4,
  "loop": true,
  "play_rate": 1.0,
  "start_offset_s": 0.0,
  "root_motion": "preserve|ignore|extract"
}
```

## PhysicsBody

```json
{
  "type": "static|dynamic|kinematic",
  "mass_kg": 10.0,
  "linear_velocity": [0,0,0],
  "angular_velocity": [0,0,0],
  "linear_damping": 0.0,
  "angular_damping": 0.05,
  "gravity": true,
  "ccd": false,
  "shapes": []
}
```

## Shot

```json
{
  "shot_id": "uuid",
  "camera_id": "camera-main",
  "start_s": 0.0,
  "duration_s": 6.0,
  "fps": 24,
  "timeline": [],
  "style_profile": "cinematic_realism",
  "render_profile": "preview"
}
```

## Timeline key

```json
{
  "time_s": 1.5,
  "target_id": "camera-main",
  "property": "transform.translation",
  "value": [0,1,2],
  "interpolation": "linear|cubic|step"
}
```

## EngineCommand envelope

```json
{
  "command_id": "uuid",
  "correlation_id": "uuid",
  "world_id": "uuid",
  "expected_world_version": 42,
  "operation": "set_camera",
  "target_id": "camera-main",
  "payload": {},
  "deadline_ms": 5000,
  "idempotency_key": "optional"
}
```

## EngineResult envelope

```json
{
  "command_id": "uuid",
  "ok": true,
  "world_version": 43,
  "result": {},
  "warnings": [],
  "error": null,
  "latency_ms": 18
}
```

## Error

```json
{
  "error_code": "CAPABILITY_UNSUPPORTED",
  "safe_message": "The selected engine cannot perform this operation in the current mode.",
  "source": "unreal-adapter",
  "retryable": false,
  "correlation_id": "uuid",
  "details_internal": null
}
```

`details_internal` nooit ongefilterd aan publieke client doorgeven.

## RenderJob

```json
{
  "render_id": "uuid",
  "world_id": "uuid",
  "shot_id": "uuid",
  "profile": "preview|final",
  "renderer": "auto|raster|raytrace|pathtrace",
  "resolution": [1920,1080],
  "fps": 24,
  "frame_range": [0,143],
  "format": "png|exr|video",
  "passes": ["beauty"],
  "output_uri": "asset://renders/job-123/",
  "settings": {}
}
```

## WorldEvent

```json
{
  "event_id": "uuid",
  "world_id": "uuid",
  "world_version": 43,
  "source": "engine|physics|user|ai",
  "type": "entity_changed",
  "entity_ids": ["uuid"],
  "payload": {},
  "timestamp": "UTC",
  "correlation_id": "uuid"
}
```

## Required adapter methods

```text
connect
shutdown
healthcheck
get_capabilities
create/open/save/checkpoint world
create/update/delete entity
set material
set light
set camera
set animation
set physics
execute action
read world/entity state
subscribe events
render preview/final
query render job
```

## Rules voor mappings

1. Engine-native handles blijven intern in adapter.
2. Externe API krijgt canonical IDs.
3. Unit conversion alleen op adapter boundary.
4. Axis/handedness conversion alleen op adapter boundary.
5. Unsupported property → warning/fallback/capability error; nooit stil negeren als betekenis verandert.
6. Na structural mutation readback of engine acknowledgement.
7. Iedere command traceable via correlation_id.
8. Engine crash/reconnect mag canonical world model niet vernietigen.
