extends Node2D
## Opening pages of the book: the story, then every rule, before chapter 1.

const PAGES: Array[Dictionary] = [
	{
		"chapter": "กล่องข้าวน้อย",
		"title": "กาลครั้งหนึ่ง",
		"art": "res://Assets/Generated/Story/cover_menu.png",
		"body": "ในหมู่บ้านอีสาน แม่หุงข้าวเหนียวใส่กล่องใบน้อย\nเพื่อนำไปให้ลูกชายชื่อไอ้ทองที่รออยู่ปลายทาง\n\nท้องของลูกว่างเปล่า และเวลาไม่คอยใคร",
	},
	{
		"chapter": "เนื้อเรื่อง",
		"title": "ทางที่แม่ต้องเดิน",
		"art": "res://Assets/Generated/Story/page_01.png",
		"body": "แม่เดินจากหมู่บ้าน ผ่านป่าไผ่ ทางขรุขระ ทุ่งนา\nและคูน้ำกลางคืน ก่อนกล่องข้าวจะถึงมืออ้ายทอง\n\nระหว่างทางมีหนาม หอกไผ่ สัตว์ป่า\nและปริศนาที่ต้องไข จึงจะข้ามไปได้",
	},
	{
		"chapter": "เป้าหมาย",
		"title": "สิ่งที่แม่ต้องทำให้จบ",
		"art": "res://Assets/Generated/Story/page_06.png",
		"body": "ส่งกล่องข้าวให้ถึงก่อนหลอดไอ้ทองหมด\nหลอดนี้ลดลงตลอดเวลา หมดแล้วเรื่องจบ\n\nเก็บกระติบข้าวให้ครบ 8 ใบ ทั้งเรื่อง\nจึงจะจบแบบสุข ถ้าเก็บไม่ครบ แม่ถึงแต่ลูกยังหิว",
	},
	{
		"chapter": "กติกา",
		"title": "วิธีพลิกเท้า",
		"art": "res://Assets/Generated/Story/page_02.png",
		"body": "A หรือ ลูกศรซ้าย — เดินซ้าย\nD หรือ ลูกศรขวา — เดินขวา\nSpace หรือ W — กระโดด\nJ — ปาหิน  (ก้อนหินมีจำกัด ต้องเก็บเติม)\nEsc หรือ P — เปิดหน้าพัก\n\nบนจอสัมผัสใช้ปุ่มมุมล่างแทนได้",
	},
	{
		"chapter": "กติกา",
		"title": "สิ่งที่ต้องมองบนหน้ากระดาษ",
		"art": "res://Assets/Generated/Story/page_03.png",
		"body": "หัวใจ คือชีวิต เสียแล้วเกิดใหม่ที่ศาลเซฟ\nหัวใจหมดทุกดวง เรื่องจบ\n\nแถบเขียว คือเลือดของแม่\nแถบน้ำตาล คือความอดทนของไอ้ทอง\nตัวเลขกระติบ คือข้าวที่เก็บได้  หิน คือกระสุน",
	},
	{
		"chapter": "กติกา",
		"title": "ของบนทาง",
		"art": "res://Assets/Generated/Story/page_05.png",
		"body": "งู หมูป่า ควาย นกกา — ปาหินได้ ควายกับหมูทนกว่า\nหนาม หอกไผ่ ลูกตุ้ม ใบมีด — อย่าเหยียบ\nตกคูน้ำแล้วตาย\n\nหินลูกรังดันทับสวิตช์ เพื่อเปิดกำแพงไผ่หรือสะพาน\nศาลเขียวคือจุดเซฟ  ศาลเทวดาคือมินิเกม\nเล่นผ่านได้ความอดทนกับก้อนหิน\nเล่นไม่ผ่าน หลอดไอ้ทองจะลดเร็วขึ้น",
	},
]

var _index: int = 0
var _turning: bool = false


func _ready() -> void:
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	AudioManager.play_music("menu_theme")
	_show_page(0, false)


func _unhandled_input(event: InputEvent) -> void:
	if _turning or not event.is_pressed() or event.is_echo():
		return
	if event.is_action_pressed("ui_right") or event.is_action_pressed("ui_accept") or event.is_action_pressed("Jump"):
		_on_next_pressed()
	elif event.is_action_pressed("ui_left"):
		_on_prev_pressed()
	elif event.is_action_pressed("ui_cancel"):
		_finish()


func _on_next_pressed() -> void:
	if _index >= PAGES.size() - 1:
		_finish()
		return
	_show_page(_index + 1, true)


func _on_prev_pressed() -> void:
	if _index <= 0:
		return
	_show_page(_index - 1, true)


func _on_skip_pressed() -> void:
	_finish()


func _show_page(index: int, animate: bool) -> void:
	if _turning:
		return
	_index = clampi(index, 0, PAGES.size() - 1)
	var page: Dictionary = PAGES[_index]
	%Chapter.text = str(page.get("chapter", ""))
	%Title.text = str(page.get("title", ""))
	%Body.text = str(page.get("body", ""))
	%Folio.text = "แผ่น %d จาก %d" % [_index + 1, PAGES.size()]
	var art_path := str(page.get("art", ""))
	if art_path != "" and ResourceLoader.exists(art_path):
		%Illustration.texture = load(art_path) as Texture2D
		%Illustration.visible = true
	else:
		%Illustration.visible = false
	%btnPrev.disabled = _index <= 0
	%btnNext.text = "เริ่มเดินทาง" if _index >= PAGES.size() - 1 else "พลิกหน้าถัดไป"
	if animate:
		_flip()
	else:
		%Page.scale = Vector2.ONE
		%Page.modulate.a = 1.0


func _flip() -> void:
	_turning = true
	AudioManager.play("page_turn")
	%Page.pivot_offset = %Page.size * 0.5
	var tween := create_tween()
	tween.tween_property(%Page, "scale", Vector2(0.96, 0.96), 0.12)
	tween.parallel().tween_property(%Page, "modulate:a", 0.72, 0.12)
	tween.tween_property(%Page, "scale", Vector2.ONE, 0.2).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.parallel().tween_property(%Page, "modulate:a", 1.0, 0.2)
	await tween.finished
	_turning = false


func _finish() -> void:
	if _turning:
		return
	_turning = true
	AudioManager.play("ui_click")
	SceneTransition.load_scene_path("res://Scenes/Levels/level_01.tscn")
