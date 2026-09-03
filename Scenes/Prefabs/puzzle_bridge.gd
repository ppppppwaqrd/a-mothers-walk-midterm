extends AnimatableBody2D
## Floor that slides across a canal. Stays solid so the player can walk it.

@export var open_offset := Vector2(320, 0)
@export var open_duration := 0.8

var _opened := false


func open_gate() -> void:
	if _opened:
		return
	_opened = true
	AudioManager.play("gate_open")
	var tween := create_tween()
	tween.tween_property(self, "position", position + open_offset, open_duration).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
