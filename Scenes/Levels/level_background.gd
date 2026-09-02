extends CanvasLayer
## Full-screen level background (no Parallax tiling seams).

@onready var rect: TextureRect = $TextureRect

const LEVEL_BG := {
	"level_01": "res://Assets/Generated/BG/bg_level_01.png",
	"level_02": "res://Assets/Generated/BG/bg_level_02.png",
	"level_03": "res://Assets/Generated/BG/bg_level_03.png",
	"level_04": "res://Assets/Generated/BG/bg_level_04.png",
	"level_05": "res://Assets/Generated/BG/bg_level_03.png",
	"level_06": "res://Assets/Generated/BG/bg_level_04.png",
}


func _ready() -> void:
	layer = -100
	follow_viewport_enabled = false
	# Parent BaseLevel sets GameManager.current_level in its _ready (after children).
	call_deferred("_apply_for_current_scene")
	get_viewport().size_changed.connect(_fit)
	_fit()


func _resolve_level_key() -> String:
	# Prefer GameManager (set by base_level after enter).
	if typeof(GameManager) != TYPE_NIL and str(GameManager.current_level).contains("level_0"):
		return str(GameManager.current_level).get_file().get_basename()
	var scene := get_tree().current_scene
	if scene != null:
		var path := str(scene.scene_file_path)
		if path.contains("level_0"):
			return path.get_file().get_basename()
	var n: Node = self
	while n != null:
		var p := str(n.scene_file_path)
		if p.contains("level_0"):
			return p.get_file().get_basename()
		n = n.get_parent()
	return "level_01"


func _apply_for_current_scene() -> void:
	var key := _resolve_level_key()
	var tex_path: String = LEVEL_BG.get(key, "res://Assets/Generated/BG/bg_level_01.png")
	if ResourceLoader.exists(tex_path):
		rect.texture = load(tex_path) as Texture2D
	_fit()


func _fit() -> void:
	if rect == null:
		return
	var vp := get_viewport().get_visible_rect().size
	rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	rect.position = Vector2.ZERO
	rect.size = vp
	rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
