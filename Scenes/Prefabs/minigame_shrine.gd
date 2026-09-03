extends Area2D
## Rest-point that opens an Isan minigame once.

@export_enum("crow_scare", "buffalo_herd", "rice_guard") var game_id: String = "crow_scare"
@export var hard := false
@export var hint := "เดินเข้ามาคุย"

var used := false


func _on_body_entered(body: Node2D) -> void:
	if used or not body.is_in_group("Player"):
		return
	used = true
	var ui := get_tree().current_scene.get_node_or_null("UserInterface")
	if ui and ui.has_method("open_minigame"):
		ui.open_minigame(game_id, hard)
	elif ui and ui.has_method("alert"):
		ui.alert(hint)
	$Sprite2D.modulate = Color(0.7, 0.9, 0.7, 1)
