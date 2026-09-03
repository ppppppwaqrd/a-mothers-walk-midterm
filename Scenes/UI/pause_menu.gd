extends Control
## The paused page: resume, retry, volume, and the way back to the menu.
##
## Pausing is what this scene owns — it sets and clears `SceneTree.paused`, so
## nothing else has to remember to unpause when the player leaves through one of
## these buttons.


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	hide()
	%Music.value = GameManager.music_volume
	%Sound.value = GameManager.sfx_volume


func open() -> void:
	if visible:
		return
	AudioManager.play("ui_click")
	show()
	get_tree().paused = true
	%Resume.grab_focus()
	%Page.pivot_offset = %Page.size * 0.5
	%Page.scale = Vector2(0.9, 0.9)
	modulate.a = 0.0
	var tween := create_tween().set_parallel(true)
	tween.tween_property(self, "modulate:a", 1.0, 0.2)
	tween.tween_property(%Page, "scale", Vector2.ONE, 0.25).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_BACK)


func close() -> void:
	if not visible:
		return
	AudioManager.play("ui_back")
	hide()
	get_tree().paused = false


func toggle() -> void:
	if visible:
		close()
	else:
		open()


func _on_resume_pressed() -> void:
	close()


func _on_retry_pressed() -> void:
	get_tree().paused = false
	AudioManager.play("ui_click")
	GameManager.retry_level()


func _on_menu_pressed() -> void:
	get_tree().paused = false
	AudioManager.play("ui_back")
	GameManager.save_game()
	SceneTransition.load_scene_path("res://Scenes/Levels/menu.tscn")


func _on_music_value_changed(value: float) -> void:
	GameManager.music_volume = value
	GameManager.update_option()
	GameManager.save_option()


func _on_sound_value_changed(value: float) -> void:
	GameManager.sfx_volume = value
	GameManager.update_option()
	GameManager.save_option()
	AudioManager.play("ui_click")
