extends Area2D
## Help a villager once — refill patience / ammo and score.

@export var patience_reward := 20.0
@export var ammo_reward := 3
@export var score_reward := 2
@export var help_message := "ช่วยชาวบ้านแล้ว — ไอ้ทองรอได้นานขึ้น"

var helped := false


func _on_body_entered(body: Node2D) -> void:
	if helped or not body.is_in_group("Player"):
		return
	helped = true
	GameManager.patience = minf(GameManager.max_patience, GameManager.patience + patience_reward)
	GameManager.add_ammo(ammo_reward)
	GameManager.add_score(score_reward)
	AudioManager.coin_pickup_sfx.play()
	var ui := get_tree().current_scene.get_node_or_null("UserInterface")
	if ui and ui.has_method("alert"):
		ui.alert(help_message)
	var spr := get_node_or_null("Sprite2D")
	if spr:
		spr.modulate = Color(0.6, 0.9, 0.6, 1)
	# Disable further triggers but keep visible as helped.
	set_deferred("monitoring", false)
