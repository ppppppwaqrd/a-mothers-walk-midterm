extends Area2D

@export var bounce_force: float = 950.0


func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("Player") and body.has_method("jump"):
		body.velocity.y = -bounce_force
		# Lower than the player's own jump, so a board reads as a bigger launch.
		AudioManager.play("jump", 0.0, 0.78)
