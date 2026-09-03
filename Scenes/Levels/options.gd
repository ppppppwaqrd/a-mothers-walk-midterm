extends Node2D
## Settings. Same values are reachable mid-level from the pause page.

var _loading := true


func _ready() -> void:
	GameManager.load_option()
	%Music.value = GameManager.music_volume
	%Sound.value = GameManager.sfx_volume
	%MusicOn.button_pressed = GameManager.music_on
	%SoundOn.button_pressed = GameManager.sfx_on
	%Fullscreen.button_pressed = GameManager.fullscreen
	_loading = false
	_show_percent()
	_apply_locale()
	if not Locale.language_changed.is_connected(_apply_locale):
		Locale.language_changed.connect(_apply_locale)


func _apply_locale() -> void:
	%Title.text = Locale.t("opt_title")
	%MusicLabel.text = Locale.t("opt_music")
	%MusicOn.text = Locale.t("opt_music_on")
	%SoundLabel.text = Locale.t("opt_sfx")
	%SoundOn.text = Locale.t("opt_sfx_on")
	%DisplayTitle.text = Locale.t("opt_screen")
	%Fullscreen.text = Locale.t("opt_fullscreen")
	%LangTitle.text = Locale.t("opt_lang")
	$CanvasLayer/UI/btnBack.text = Locale.t("opt_back")
	%LangTh.disabled = Locale.lang == "th"
	%LangEn.disabled = Locale.lang == "en"


func _show_percent() -> void:
	%MusicPct.text = "%d%%" % roundi(%Music.value * 100.0)
	%SoundPct.text = "%d%%" % roundi(%Sound.value * 100.0)


func _apply() -> void:
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


func _on_fullscreen_toggled(on: bool) -> void:
	if _loading:
		return
	GameManager.set_fullscreen(on)
	AudioManager.play("ui_click")


func _on_lang_th_pressed() -> void:
	AudioManager.play("ui_click")
	Locale.set_lang("th")


func _on_lang_en_pressed() -> void:
	AudioManager.play("ui_click")
	Locale.set_lang("en")


func _on_btn_back_pressed() -> void:
	AudioManager.play("ui_back")
	SceneTransition.load_scene_path("res://Scenes/Levels/menu.tscn")
