extends Control
## The page that turns over at the start of a level, naming the chapter.
##
## Runs on its own while the game is paused, then hands control back. Any input
## skips it, so a replay is never held up by it.

signal dismissed

const HOLD := 2.6
const FADE := 0.45

var _dismissing := false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	hide()


## `chapter` is the small line above the title, e.g. "บทที่ 3".
## `level_id` loads the matching watercolor plate when one exists.
func open(chapter: String, title: String, hint: String, level_id: String = "") -> void:
	%Chapter.text = chapter
	%Title.text = title
	%Hint.text = hint
	_show_art(level_id)
	_dismissing = false
	show()
	modulate.a = 0.0
	%Page.pivot_offset = %Page.size * 0.5
	%Page.scale = Vector2(0.94, 0.94)
	%Page.rotation_degrees = -1.6
	AudioManager.play("page_turn")
	var tween := create_tween().set_parallel(true)
	tween.tween_property(self, "modulate:a", 1.0, FADE)
	tween.tween_property(%Page, "scale", Vector2.ONE, FADE).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_BACK)
	tween.tween_property(%Page, "rotation_degrees", 0.0, FADE)
	await get_tree().create_timer(HOLD, true, false, true).timeout
	close()


func _show_art(level_id: String) -> void:
	var art: TextureRect = %Illustration
	var key := level_id.trim_prefix("level_")
	var path := "res://Assets/Generated/Story/page_%s.png" % key
	if key != "" and ResourceLoader.exists(path):
		art.texture = load(path) as Texture2D
		art.visible = true
	else:
		art.texture = null
		art.visible = false


func close() -> void:
	if _dismissing or not visible:
		return
	_dismissing = true
	var tween := create_tween().set_parallel(true)
	tween.tween_property(self, "modulate:a", 0.0, FADE * 0.7)
	tween.tween_property(%Page, "scale", Vector2(1.04, 1.04), FADE * 0.7)
	await tween.finished
	hide()
	dismissed.emit()


func _input(event: InputEvent) -> void:
	if not visible or _dismissing:
		return
	if event.is_pressed() and not event.is_echo():
		close()
