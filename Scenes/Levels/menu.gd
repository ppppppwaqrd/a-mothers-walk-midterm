extends Node2D
## The cover of the book: where a run is started, resumed, or set up.


func _ready() -> void:
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	%btnContinue.disabled = not GameManager.has_gamesaved()
	GameManager.load_option()
	AudioManager.play_music("menu_theme")


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
