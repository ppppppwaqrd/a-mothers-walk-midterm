extends Pickup

@export var heal_amount := 25
@export var give_extra_life := false


func _collect(_player: Node2D) -> bool:
	GameManager.add_hp(heal_amount)
	if give_extra_life:
		GameManager.add_life()
	AudioManager.play("pickup_heart")
	return true
