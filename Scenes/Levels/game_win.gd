extends Node2D


func _ready() -> void:
	_apply_locale()
	if not Locale.language_changed.is_connected(_apply_locale):
		Locale.language_changed.connect(_apply_locale)
	AudioManager.stop_music()
	AudioManager.play("win")


func _apply_locale() -> void:
	if GameManager.has_happy_ending():
		%Title.text = Locale.t("win_good_title")
		%Line.text = Locale.t("win_good_line")
	else:
		%Title.text = Locale.t("win_ok_title")
		%Line.text = Locale.t("win_ok_line")
	%Score.text = Locale.tf("kratib_count", [GameManager.kratib, GameManager.kratib_needed])
	$CanvasLayer/UI/Page/Body/Buttons/btnRetry.text = Locale.t("win_retry")
	$CanvasLayer/UI/Page/Body/Buttons/btnMenu.text = Locale.t("win_menu")


func _on_retry_pressed() -> void:
	AudioManager.play("ui_click")
	GameManager.new_game()


func _on_menu_pressed() -> void:
	AudioManager.play("ui_back")
	SceneTransition.load_scene_path("res://Scenes/Levels/menu.tscn")
