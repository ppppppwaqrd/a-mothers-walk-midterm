extends Pickup

@export var ammo_amount := 3


func _collect(_player: Node2D) -> bool:
	GameManager.add_ammo(ammo_amount)
	AudioManager.play("pickup_stone")
	return true
