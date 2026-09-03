extends Node2D
## Four-layer storybook parallax background.
##
## The sky is pinned to the screen. The far/mid/near layers are anchored in world
## space and scroll horizontally at their own rate. Each layer texture is
## horizontally tileable, so it is drawn through a repeating region wide enough to
## cover the viewport and shifted with a modulo: the level can be any length
## without running out of image.
##
## Vertically each layer is aligned by its *ground line* — the height at which its
## painted terrain sits. Every layer image ends with a SKIRT-deep pad below that
## line (see scripts/build_storybook_bgs.py), so the ground line is always
## `texture_height - SKIRT`, and the pad keeps the layer's hard bottom edge out of
## sight where the terrain drops away. The line itself is matched to the top of
## the level's own ground tiles, which sit at a different height in each level.

const SKIRT := 420.0

## Scroll rate and where each layer's ground line sits relative to the top of the
## level's ground tiles, back to front. Far sits just above so its base tucks
## behind the terrain; near sits below so its plants overlap the player's ground.
const LAYERS := {
	"Far": {"factor": 0.10, "offset": -16.0},
	"Mid": {"factor": 0.28, "offset": 6.0},
	"Near": {"factor": 0.60, "offset": 4.0},
}

const SKY_DRIFT := 0.015
const SKY_BASE_HEIGHT := 720.0

## Used until the level's ground tiles can be measured.
const FALLBACK_GROUND_Y := 384.0

var _sky: Sprite2D
var _layers: Dictionary = {}
var _ground_y := FALLBACK_GROUND_Y
var _level_key := ""


func _ready() -> void:
	z_index = -100
	z_as_relative = false
	_sky = $Sky
	for name in LAYERS:
		_layers[name] = get_node(NodePath(name)) as Sprite2D
	if _level_key == "":
		apply_level(_level_id_from_parent())


## Point every layer at one level's artwork. Called by base_level.gd.
func apply_level(key: String) -> void:
	_level_key = key
	_ground_y = _measure_ground_y()
	_assign(_sky, "sky", key)
	for name in LAYERS:
		_assign(_layers[name], name.to_lower(), key)
	_update_positions()


## Height of the ground the player actually walks on, in world space.
##
## Not the top of the tilemap: a single high ledge would drag that up and lift
## every background layer with it. Take the top of each column of tiles and use
## the median, so ledges and pits are outvoted by the main floor.
func _measure_ground_y() -> float:
	var parent := get_parent()
	if parent == null:
		return FALLBACK_GROUND_Y
	var tops: Array[float] = []
	for child in parent.find_children("*", "TileMapLayer", true, false):
		var layer := child as TileMapLayer
		var column_top: Dictionary = {}
		for cell in layer.get_used_cells():
			var seen = column_top.get(cell.x)
			if seen == null or cell.y < seen:
				column_top[cell.x] = cell.y
		var half := layer.tile_set.tile_size.y * 0.5
		for x in column_top:
			var local := layer.map_to_local(Vector2i(x, column_top[x])) - Vector2(0.0, half)
			tops.append(layer.to_global(local).y)
	if tops.is_empty():
		return FALLBACK_GROUND_Y
	tops.sort()
	return tops[tops.size() / 2]


func _assign(sprite: Sprite2D, prefix: String, key: String) -> void:
	if sprite == null:
		return
	# Layer files are numbered, e.g. "level_03" -> sky_03.png.
	var path := "res://Assets/Generated/BG/%s_%s.png" % [prefix, key.trim_prefix("level_")]
	if not ResourceLoader.exists(path):
		push_warning("missing background layer %s" % path)
		path = "res://Assets/Generated/BG/%s_01.png" % prefix
	if ResourceLoader.exists(path):
		sprite.texture = load(path) as Texture2D
	sprite.centered = false
	sprite.region_enabled = true
	sprite.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED


func _level_id_from_parent() -> String:
	var parent := get_parent()
	if parent != null:
		var id = parent.get("level_id")
		if id != null and str(id) != "":
			return str(id)
	return "level_01"


func _process(_delta: float) -> void:
	_update_positions()


func _update_positions() -> void:
	var camera := get_viewport().get_camera_2d()
	if camera == null:
		return
	var view: Vector2 = get_viewport_rect().size
	var centre: Vector2 = camera.get_screen_center_position()
	var top_left: Vector2 = centre - view * 0.5

	if _sky != null and _sky.texture != null:
		var zoom: float = view.y / SKY_BASE_HEIGHT
		_sky.scale = Vector2(zoom, zoom)
		var sky_width: float = _sky.texture.get_width()
		_sky.region_rect = Rect2(0.0, 0.0, view.x / zoom, SKY_BASE_HEIGHT)
		_sky.position = Vector2(top_left.x - fposmod(centre.x * SKY_DRIFT, sky_width), top_left.y)

	for name in LAYERS:
		var sprite: Sprite2D = _layers.get(name)
		if sprite == null or sprite.texture == null:
			continue
		var data: Dictionary = LAYERS[name]
		var size: Vector2 = sprite.texture.get_size()
		var shift: float = fposmod(centre.x * float(data["factor"]), size.x)
		sprite.region_rect = Rect2(0.0, 0.0, view.x + size.x, size.y)
		var ground_line: float = size.y - SKIRT
		sprite.position = Vector2(
			top_left.x - shift,
			_ground_y + float(data["offset"]) - ground_line
		)
