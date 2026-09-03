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
	%Fullscreen.set_pressed_no_signal(GameManager.fullscreen)
	_apply_locale()
	if not Locale.language_changed.is_connected(_apply_locale):
		Locale.language_changed.connect(_apply_locale)


func _apply_locale() -> void:
	$Page/Body/Heading.text = Locale.t("pause_title")
	%Resume.text = Locale.t("pause_resume")
	$Page/Body/Retry.text = Locale.t("pause_retry")
	$Page/Body/Menu.text = Locale.t("pause_menu")
	$Page/Body/MusicRow/MusicLabel.text = Locale.t("opt_music")
	$Page/Body/SoundRow/SoundLabel.text = Locale.t("opt_sfx")
	%Fullscreen.text = Locale.t("opt_fullscreen")
	%LangTitle.text = Locale.t("opt_lang")
	%LangTh.disabled = Locale.lang == "th"
	%LangEn.disabled = Locale.lang == "en"


func open() -> void:
	if visible:
		return
	AudioManager.play("ui_click")
	%Music.value = GameManager.music_volume
	%Sound.value = GameManager.sfx_volume
	%Fullscreen.set_pressed_no_signal(GameManager.fullscreen)
	_apply_locale()
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


func _on_fullscreen_toggled(on: bool) -> void:
	GameManager.set_fullscreen(on)
	AudioManager.play("ui_click")


func _on_lang_th_pressed() -> void:
	AudioManager.play("ui_click")
	Locale.set_lang("th")


func _on_lang_en_pressed() -> void:
	AudioManager.play("ui_click")
	Locale.set_lang("en")
