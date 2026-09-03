extends Node2D


func _ready() -> void:
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	if GameManager.lose_reason == "patience":
		%Title.text = "อ้ายทองรอไม่ไหว"
		%Line.text = "กล่องข้าวไปไม่ทัน\nท้องของลูกว่างเปล่าก่อนแม่จะถึง"
	%Score.text = "กระติบ %d จาก %d" % [GameManager.kratib, GameManager.kratib_needed]
	AudioManager.stop_music()
	AudioManager.play("game_over")


func _on_retry_pressed() -> void:
	AudioManager.play("ui_click")
	GameManager.retry_checkpoint()


func _on_menu_pressed() -> void:
	AudioManager.play("ui_back")
	SceneTransition.load_scene_path("res://Scenes/Levels/menu.tscn")
