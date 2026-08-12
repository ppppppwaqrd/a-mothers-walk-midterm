extends Node2D

func _ready() -> void:
	GameManager.player = %Player
	GameManager.on_level_entered(scene_file_path)
	var bg := get_node_or_null("LevelBackground")
	if bg and bg.has_method("_apply_for_current_scene"):
		bg._apply_for_current_scene()
	if %Player:
		%Player.spawn_point = %Player.global_position
	$MusicPlayer.play(0)
	_show_start_hints()


func _show_start_hints() -> void:
	var label := $UserInterface/Label
	if label == null:
		return
	var level_title := str(label.text).strip_edges()
	label.text = "%s\nA/D เดิน | Space กระโดด | J ปาหิน" % level_title
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var tween = create_tween()
	label.scale = Vector2.ZERO
	tween.tween_property(label, "scale", Vector2.ONE, 0.8)
	await get_tree().create_timer(4.0).timeout
	if is_instance_valid(label):
		label.queue_free()


func _on_player_hit_enemy(enemy: Node2D = null) -> void:
	if enemy != null and enemy.has_method("get_touch_damage"):
		GameManager.damage(enemy.get_touch_damage())
	else:
		GameManager.damage(8)


func _on_player_hit_trap() -> void:
	GameManager.damage(20)
	if GameManager.player and GameManager.player.has_method("damage_tween"):
		GameManager.player.damage_tween()


func _on_music_player_finished() -> void:
	$MusicPlayer.play(0)
