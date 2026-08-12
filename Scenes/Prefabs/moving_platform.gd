extends AnimatableBody2D

@export var move_offset: Vector2 = Vector2(180, 0)
@export var move_duration: float = 2.0

var _start: Vector2


func _ready() -> void:
	_start = position
	var tween := create_tween()
	tween.set_loops()
	tween.tween_property(self, "position", _start + move_offset, move_duration).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_property(self, "position", _start, move_duration).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
