extends Node2D


func _ready() -> void:
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	if GameManager.has_happy_ending():
		%Title.text = "ถึงมืออ้ายทองแล้ว"
		%Line.text = "กล่องข้าวยังอุ่น ข้าวเหนียวยังนุ่ม\nแม่นั่งลงข้างลูก แล้วเรื่องนี้ก็จบลงตรงนี้"
	else:
		%Title.text = "ถึงแล้ว แต่ข้าวไม่พอ"
		%Line.text = "แม่เดินมาถึงข้างลูกแล้ว แต่กระติบไม่ครบทั้งทาง\nไอ้ทองยังหิว กล่องข้าวไม่พอให้ยิ้มได้"
	%Score.text = "กระติบ %d จาก %d" % [GameManager.kratib, GameManager.kratib_needed]
	AudioManager.stop_music()
	AudioManager.play("win")


func _on_retry_pressed() -> void:
	AudioManager.play("ui_click")
	GameManager.new_game()


func _on_menu_pressed() -> void:
	AudioManager.play("ui_back")
	SceneTransition.load_scene_path("res://Scenes/Levels/menu.tscn")
