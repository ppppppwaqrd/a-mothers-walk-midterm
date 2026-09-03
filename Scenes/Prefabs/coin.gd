extends Pickup


func _collect(_player: Node2D) -> bool:
	AudioManager.play_varied("pickup_kratib")
	GameManager.add_score()
	return true
