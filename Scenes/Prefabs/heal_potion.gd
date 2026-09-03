extends Pickup

@export var heal_amount := 20


func _collect(_player: Node2D) -> bool:
	GameManager.add_hp(heal_amount)
	AudioManager.play("pickup_heart")
	return true
