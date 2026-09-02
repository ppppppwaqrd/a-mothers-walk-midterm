extends StaticBody2D
## Blocking gate opened by puzzle_switch.

@export var open_offset := Vector2(0, -96)
@export var open_duration := 0.6

var _opened := false


func open_gate() -> void:
	if _opened:
		return
	_opened = true
	var tween := create_tween()
	tween.tween_property(self, "position", position + open_offset, open_duration)
	# Disable collision after open so player can pass even if sprite still visible mid-tween.
	await tween.finished
	collision_layer = 0
	collision_mask = 0
	hide()
