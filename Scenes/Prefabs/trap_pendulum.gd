extends StaticBody2D

@export var swing_angle_deg: float = 70.0
@export var swing_duration: float = 1.4


func _ready() -> void:
	var arm := $Arm
	var tween := create_tween()
	tween.set_loops()
	tween.tween_property(arm, "rotation_degrees", swing_angle_deg, swing_duration).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_property(arm, "rotation_degrees", -swing_angle_deg, swing_duration).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
