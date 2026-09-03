extends Node2D
## Sound settings. The same values are reachable mid-level from the pause page.

var _loading := true


func _ready() -> void:
	GameManager.load_option()
	%Music.value = GameManager.music_volume
	%Sound.value = GameManager.sfx_volume
	%MusicOn.button_pressed = GameManager.music_on
	%SoundOn.button_pressed = GameManager.sfx_on
	_loading = false
	_show_percent()


func _show_percent() -> void:
	%MusicPct.text = "%d%%" % roundi(%Music.value * 100.0)
	%SoundPct.text = "%d%%" % roundi(%Sound.value * 100.0)


func _apply() -> void:
	# Setting the controls in _ready fires their signals; ignore that first pass
	# so it cannot write defaults back over the saved settings.
	if _loading:
		return
	GameManager.update_option()
	GameManager.save_option()


func _on_music_value_changed(value: float) -> void:
	GameManager.music_volume = value
	_show_percent()
	_apply()


func _on_sound_value_changed(value: float) -> void:
	GameManager.sfx_volume = value
	_show_percent()
	_apply()
	AudioManager.play("ui_click")


func _on_music_on_toggled(on: bool) -> void:
	GameManager.music_on = on
	_apply()


func _on_sound_on_toggled(on: bool) -> void:
	GameManager.sfx_on = on
	_apply()


func _on_btn_back_pressed() -> void:
	AudioManager.play("ui_back")
	SceneTransition.load_scene_path("res://Scenes/Levels/menu.tscn")
