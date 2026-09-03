extends Pickup

@export var speed_multiplier := 1.55
@export var duration := 6.0


func _collect(player: Node2D) -> bool:
	if not player.has_method("apply_speed_boost"):
		return false
	player.apply_speed_boost(speed_multiplier, duration)
	AudioManager.play("pickup_heart")
	return true
