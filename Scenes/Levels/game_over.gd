extends Node2D


func _ready() -> void:
	_apply_locale()
	if not Locale.language_changed.is_connected(_apply_locale):
		Locale.language_changed.connect(_apply_locale)
	AudioManager.stop_music()
	AudioManager.play("game_over")


func _apply_locale() -> void:
	if GameManager.lose_reason == "patience":
		%Title.text = Locale.t("over_hunger_title")
		%Line.text = Locale.t("over_hunger_line")
	else:
		%Title.text = Locale.t("over_fall_title")
		%Line.text = Locale.t("over_fall_line")
	%Score.text = Locale.tf("kratib_count", [GameManager.kratib, GameManager.kratib_needed])
	$CanvasLayer/UI/Page/Body/Buttons/btnRetry.text = Locale.t("over_retry")
	$CanvasLayer/UI/Page/Body/Buttons/btnMenu.text = Locale.t("over_menu")


func _on_retry_pressed() -> void:
	AudioManager.play("ui_click")
	GameManager.retry_checkpoint()


func _on_menu_pressed() -> void:
	AudioManager.play("ui_back")
	SceneTransition.load_scene_path("res://Scenes/Levels/menu.tscn")
