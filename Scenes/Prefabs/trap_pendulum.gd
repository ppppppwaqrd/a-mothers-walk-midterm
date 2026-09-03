extends Node2D
## Swinging rock. Hitbox is an Area2D on the arm, so it follows the stone.

@export var swing_angle_deg: float = 70.0
@export var swing_duration: float = 1.4

var _cooldown := 0.0


func _ready() -> void:
	var arm := $Arm
	var tween := create_tween()
	tween.set_loops()
	tween.tween_property(arm, "rotation_degrees", swing_angle_deg, swing_duration).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_property(arm, "rotation_degrees", -swing_angle_deg, swing_duration).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)


func _physics_process(delta: float) -> void:
	_cooldown = maxf(0.0, _cooldown - delta)
	if _cooldown > 0.0:
		return
	for body in $Arm/Hurt.get_overlapping_bodies():
		if not body.is_in_group("Player"):
			continue
		if body.get("can_damage") == false:
			continue
		if body.has_signal("hit_trap"):
			body.hit_trap.emit()
		_cooldown = 0.45
		break
