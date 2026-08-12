extends Node2D

@onready var ui: Control = $CanvasLayer/UI

func _ready() -> void:
	_fit_ui_to_viewport()
	get_viewport().size_changed.connect(_fit_ui_to_viewport)


func _fit_ui_to_viewport() -> void:
	var vp_size := get_viewport_rect().size
	ui.set_anchors_preset(Control.PRESET_TOP_LEFT)
	ui.position = Vector2.ZERO
	ui.size = vp_size
