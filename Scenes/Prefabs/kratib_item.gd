extends Pickup
## A sticky-rice basket: the collectible the whole errand is about.

@export var score_value := 1


func _collect(_player: Node2D) -> bool:
	AudioManager.play_varied("pickup_kratib")
	GameManager.add_kratib(score_value)
	return true
