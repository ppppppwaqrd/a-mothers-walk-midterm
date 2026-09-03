extends Node2D
## The cover of the book: where a run is started, resumed, or set up.


func _ready() -> void:
	%btnContinue.disabled = not GameManager.has_gamesaved()
	GameManager.load_option()
	GameManager.apply_display()
	AudioManager.play_music("menu_theme")
	_apply_locale()
	if not Locale.language_changed.is_connected(_apply_locale):
		Locale.language_changed.connect(_apply_locale)


func _apply_locale() -> void:
	$CanvasLayer/UI/Cover/Body/Title.text = Locale.t("menu_title")
	$CanvasLayer/UI/Cover/Body/Subtitle.text = Locale.t("menu_sub")
	$CanvasLayer/UI/Cover/Body/Buttons/btnStart.text = Locale.t("menu_new")
	%btnContinue.text = Locale.t("menu_continue")
	$CanvasLayer/UI/Cover/Body/Buttons/btnOption.text = Locale.t("menu_options")
	$CanvasLayer/UI/Cover/Body/Buttons/btnCredit.text = Locale.t("menu_credits")
	$CanvasLayer/UI/Cover/Body/Buttons/btnExit.text = Locale.t("menu_quit")


func _on_btn_start_pressed() -> void:
	AudioManager.play("ui_click")
	GameManager.new_game()


func _on_btn_continue_pressed() -> void:
	AudioManager.play("ui_click")
	GameManager.load_game()


func _on_btn_option_pressed() -> void:
	AudioManager.play("ui_click")
	SceneTransition.load_scene_path("res://Scenes/Levels/options.tscn")


func _on_btn_credit_pressed() -> void:
	AudioManager.play("ui_click")
	SceneTransition.load_scene_path("res://Scenes/Levels/credit.tscn")


func _on_btn_exit_pressed() -> void:
	AudioManager.play("ui_back")
	get_tree().quit()
