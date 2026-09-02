extends Node2D

@onready var music_label: Label = $CanvasLayer/UI/MusicState
@onready var sfx_label: Label = $CanvasLayer/UI/SfxState


func _ready() -> void:
	GameManager.load_option()
	_refresh()


func _refresh() -> void:
	music_label.text = "เปิด" if GameManager.music_on else "ปิด"
	sfx_label.text = "เปิด" if GameManager.sfx_on else "ปิด"


func _on_music_pressed() -> void:
	GameManager.music_on = not GameManager.music_on
	GameManager.update_option()
	GameManager.save_option()
	_refresh()


func _on_sfx_pressed() -> void:
	GameManager.sfx_on = not GameManager.sfx_on
	GameManager.update_option()
	GameManager.save_option()
	_refresh()


func _on_back_pressed() -> void:
	get_tree().change_scene_to_file("res://Scenes/Levels/menu.tscn")
