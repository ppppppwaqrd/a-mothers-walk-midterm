extends Pickup

@export var jump_multiplier := 1.4
@export var duration := 6.0


func _collect(player: Node2D) -> bool:
	if not player.has_method("apply_jump_boost"):
		return false
	player.apply_jump_boost(jump_multiplier, duration)
	AudioManager.play("pickup_heart")
	return true
