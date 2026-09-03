extends StaticBody2D
## Tall blocking gate opened by puzzle_switch. Slides up; stays visible.

@export var open_offset := Vector2(0, -192)
@export var open_duration := 0.6
@export var hide_when_open := false

var _opened := false


func open_gate() -> void:
	if _opened:
		return
	_opened = true
	AudioManager.play("gate_open")
	var tween := create_tween()
	tween.tween_property(self, "position", position + open_offset, open_duration)
	await tween.finished
	collision_layer = 0
	collision_mask = 0
	if hide_when_open:
		hide()
