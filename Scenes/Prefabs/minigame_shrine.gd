extends Area2D
## Rest-point that opens an Isan minigame once.

@export_enum("crow_scare", "buffalo_herd", "rice_guard") var game_id: String = "crow_scare"
@export var hard := false
@export var hint := ""

var used := false


func _ready() -> void:
	_apply_locale()
	if not Locale.language_changed.is_connected(_apply_locale):
		Locale.language_changed.connect(_apply_locale)


func _apply_locale() -> void:
	if $Hint == null:
		return
	if hint != "":
		$Hint.text = hint
	else:
		$Hint.text = Locale.t("shrine_" + game_id)


func _on_body_entered(body: Node2D) -> void:
	if used or not body.is_in_group("Player"):
		return
	used = true
	var ui := get_tree().current_scene.get_node_or_null("UserInterface")
	if ui and ui.has_method("open_minigame"):
		ui.open_minigame(game_id, hard)
	elif ui and ui.has_method("alert"):
		ui.alert($Hint.text if $Hint else Locale.t("shrine_crow_scare"))
	$Sprite2D.modulate = Color(0.7, 0.9, 0.7, 1)
