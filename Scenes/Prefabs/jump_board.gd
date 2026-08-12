extends Area2D

@export var bounce_force: float = 950.0


func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("Player") and body.has_method("jump"):
		body.velocity.y = -bounce_force
		if AudioManager.jump_sfx:
			AudioManager.jump_sfx.play()
