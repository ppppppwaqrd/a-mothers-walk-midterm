extends Area2D
## Mid-level shrine checkpoint — respawn here after death.

@export var amplitude := 3.0
@export var frequency := 2.5

var time_passed := 0.0
var initial_position := Vector2.ZERO
var used := false


func _ready() -> void:
	initial_position = position


func _process(delta: float) -> void:
	time_passed += delta
	position.y = initial_position.y + amplitude * sin(frequency * time_passed)


func _on_body_entered(body: Node2D) -> void:
	if not body.is_in_group("Player"):
		return
	GameManager.register_checkpoint(global_position)
	if body.has_method("set") or "spawn_point" in body:
		body.spawn_point = global_position
	if not used:
		used = true
		AudioManager.play("checkpoint_bell")
		_flash()
		var ui := get_tree().get_first_node_in_group("GameUI")
		if ui == null:
			ui = get_tree().current_scene.get_node_or_null("UserInterface")
		if ui and ui.has_method("alert"):
			ui.alert(Locale.t("toast_checkpoint"))


func _flash() -> void:
	var spr := get_node_or_null("Sprite2D")
	if spr == null:
		return
	var tween := create_tween()
	tween.tween_property(spr, "modulate", Color(1.4, 1.3, 0.7, 1), 0.15)
	tween.tween_property(spr, "modulate", Color(1, 1, 1, 1), 0.25)
