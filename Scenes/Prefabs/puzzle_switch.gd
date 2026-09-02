extends Area2D
## Pressure switch — opens linked gate(s) when player steps on it.

@export var gate_paths: Array[NodePath] = []
@export var one_shot := true

var activated := false


func _on_body_entered(body: Node2D) -> void:
	if activated and one_shot:
		return
	if not body.is_in_group("Player"):
		return
	activated = true
	$Sprite2D.modulate = Color(0.4, 1.0, 0.5, 1)
	for path in gate_paths:
		var gate := get_node_or_null(path)
		if gate and gate.has_method("open_gate"):
			gate.open_gate()
	var ui := get_tree().current_scene.get_node_or_null("UserInterface")
	if ui and ui.has_method("alert"):
		ui.alert("สะพานเปิดแล้ว!")
