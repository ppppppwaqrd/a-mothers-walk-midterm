extends Node2D

@onready var ui: Control = $CanvasLayer/UI
@onready var btn_continue: Button = $CanvasLayer/UI/Buttons/btnContinue

func _ready() -> void:
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	_fit_ui_to_viewport()
	get_viewport().size_changed.connect(_fit_ui_to_viewport)
	btn_continue.disabled = !GameManager.has_gamesaved()
	GameManager.load_option()


func _fit_ui_to_viewport() -> void:
	var vp_size := get_viewport_rect().size
	ui.set_anchors_preset(Control.PRESET_TOP_LEFT)
	ui.position = Vector2.ZERO
	ui.size = vp_size


func _on_btn_start_pressed() -> void:
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN)
	GameManager.new_game()


func _on_btn_option_pressed() -> void:
	get_tree().change_scene_to_file("res://Scenes/Levels/options.tscn")


func _on_btn_credit_pressed() -> void:
	get_tree().change_scene_to_file("res://Scenes/Levels/credit.tscn")


func _on_btn_continue_pressed() -> void:
	GameManager.load_game()


func _on_btn_exit_pressed() -> void:
	get_tree().quit()
