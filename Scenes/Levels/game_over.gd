extends Node2D

@onready var ui: Control = $CanvasLayer/UI


func _ready() -> void:
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	_fit()
	get_viewport().size_changed.connect(_fit)


func _fit() -> void:
	ui.set_anchors_preset(Control.PRESET_TOP_LEFT)
	ui.position = Vector2.ZERO
	ui.size = get_viewport_rect().size


func _on_menu_pressed() -> void:
	get_tree().change_scene_to_file("res://Scenes/Levels/menu.tscn")


func _on_retry_pressed() -> void:
	GameManager.retry_checkpoint()
