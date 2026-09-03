extends Control
## Overlay for the three rest-stop minigames: read first, then play.

signal finished(won: bool)

var _game := ""
var _hard := false
var _briefing := false
var _running := false
var _time_left := 0.0
var _player: Control
var _stones: Array[Control] = []
var _crows: Array[Control] = []
var _buffaloes: Array[Control] = []
var _villager: Control
var _chickens: Array[Dictionary] = []
var _shots_left := 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	hide()
	%StartButton.pressed.connect(_begin_play)


func open(game_id: String, hard: bool = false) -> void:
	_game = game_id
	_hard = hard
	_briefing = true
	_running = false
	_clear_field()
	var p := Locale.mini_prefix(game_id)
	%Deity.text = Locale.t(p + "_deity")
	%Title.text = Locale.t(p + "_title")
	%Story.text = Locale.t(p + "_story")
	var how: String = Locale.t(p + "_how")
	if game_id == "crow_scare" and hard:
		how += "\n" + Locale.t("mini_crow_hard")
	%How.text = how
	%StartButton.text = Locale.t("mini_start")
	%StartHint.text = Locale.t("mini_space")
	%PlayBar.hide()
	%Result.hide()
	%Field.hide()
	%Brief.show()
	show()
	modulate.a = 0.0
	var tween := create_tween()
	tween.set_pause_mode(Tween.TWEEN_PAUSE_PROCESS)
	tween.tween_property(self, "modulate:a", 1.0, 0.25)
	get_tree().paused = true
	AudioManager.play("page_turn")


func _begin_play() -> void:
	if not _briefing:
		return
	_briefing = false
	%Brief.hide()
	%Field.show()
	%PlayBar.show()
	%Hint.text = Locale.t(Locale.mini_prefix(_game) + "_play")
	_setup_game()
	_running = true
	AudioManager.play("ui_click")


func _setup_game() -> void:
	%Field.position = Vector2(24, 60)
	%Field.size = Vector2(752, 420)
	%Field.custom_minimum_size = Vector2(752, 420)
	match _game:
		"crow_scare":
			_time_left = 8.0 if _hard else 12.0
			_shots_left = 8 if _hard else 7
			_spawn_crows(7 if _hard else 5)
			_refresh_crow_hint()
		"buffalo_herd":
			_time_left = 20.0
			%Field.position = Vector2(160, 130)
			%Field.size = Vector2(480, 280)
			%Field.custom_minimum_size = Vector2(480, 280)
			_spawn_herd(3 if _hard else 2)
		"rice_guard":
			_time_left = 15.0
			_spawn_rice()
	%TimerLabel.text = "%.0f" % _time_left


func _process(delta: float) -> void:
	if not _running:
		return
	_move_player(delta)
	_time_left -= delta
	%TimerLabel.text = "%.0f" % maxf(0.0, _time_left)
	match _game:
		"crow_scare":
			_tick_crows(delta)
		"buffalo_herd":
			_tick_herd(delta)
		"rice_guard":
			_tick_rice(delta)
	if _time_left <= 0.0:
		_end(_game == "rice_guard" or _game == "buffalo_herd")


func _input(event: InputEvent) -> void:
	if not visible:
		return
	if _briefing:
		if event.is_action_pressed("Jump") or event.is_action_pressed("ui_accept"):
			_begin_play()
			get_viewport().set_input_as_handled()
		return
	if not _running:
		return
	if _game == "crow_scare" and event.is_action_pressed("Shoot"):
		_throw_stone()
		get_viewport().set_input_as_handled()


func _move_player(delta: float) -> void:
	if _player == null:
		return
	var dir := Vector2.ZERO
	if Input.is_action_pressed("Left"):
		dir.x -= 1.0
	if Input.is_action_pressed("Right"):
		dir.x += 1.0
	if _game == "buffalo_herd":
		if Input.is_action_pressed("Jump") or Input.is_action_pressed("ui_up") or Input.is_physical_key_pressed(KEY_W):
			dir.y -= 1.0
		if Input.is_action_pressed("Down"):
			dir.y += 1.0
	if dir == Vector2.ZERO:
		return
	var speed: float = 280.0 if _game != "buffalo_herd" else 260.0
	var next: Vector2 = _player.position + dir.normalized() * speed * delta
	_player.position.x = clampf(next.x, 8.0, %Field.size.x - 40.0)
	if _game == "buffalo_herd":
		_player.position.y = clampf(next.y, 8.0, %Field.size.y - 56.0)


func _clear_field() -> void:
	for child in %Field.get_children():
		child.free()
	_stones.clear()
	_crows.clear()
	_buffaloes.clear()
	_chickens.clear()
	_player = null
	_villager = null


func _tex(path: String) -> Texture2D:
	if ResourceLoader.exists(path):
		return load(path) as Texture2D
	return null


func _sprite(parent: Control, path: String, pos: Vector2, size: Vector2) -> TextureRect:
	var n := TextureRect.new()
	n.texture = _tex(path)
	n.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	n.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	n.position = pos
	n.size = size
	n.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(n)
	return n


func _mark_mother(who: Control) -> void:
	who.modulate = Color(0.98, 0.78, 0.42, 1)
	var tag := Label.new()
	tag.text = Locale.t("mini_mother")
	tag.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	tag.position = Vector2(-6, -22)
	tag.size = Vector2(44, 20)
	tag.add_theme_font_size_override("font_size", 16)
	tag.mouse_filter = Control.MOUSE_FILTER_IGNORE
	who.add_child(tag)


func _spawn_crows(count: int) -> void:
	var width: float = %Field.size.x
	_sprite(%Field, "res://Assets/Generated/Spritesheet/rice_mat.png", Vector2(width * 0.5 - 90, %Field.size.y - 56), Vector2(180, 48))
	for i in count:
		var x: float = 80.0 + float(i) * ((width - 180.0) / float(maxi(1, count - 1)))
		var y: float = 150.0 + float(i % 2) * 36.0
		var crow := _sprite(%Field, "res://Assets/Generated/Spritesheet/mini_crow.png", Vector2(x, y), Vector2(52, 40))
		crow.set_meta("home_y", y)
		crow.set_meta("phase", float(i) * 0.9)
		crow.set_meta("vx", 90.0 if i % 2 == 0 else -90.0)
		_crows.append(crow)
	_player = _sprite(%Field, "res://Assets/Generated/Spritesheet/mini_villager.png", Vector2(width * 0.5 - 16, %Field.size.y - 78), Vector2(32, 50))
	_mark_mother(_player)


func _refresh_crow_hint() -> void:
	%Hint.text = Locale.tf("mini_crow_ammo", [_shots_left])


func _throw_stone() -> void:
	if _player == null or _shots_left <= 0:
		return
	_shots_left -= 1
	_refresh_crow_hint()
	var origin := Vector2(_player.position.x + 5.0, _player.position.y - 8.0)
	var stone := _sprite(%Field, "res://Assets/Generated/Spritesheet/stone.png", origin, Vector2(22, 22))
	stone.set_meta("vy", -520.0)
	stone.set_meta("vx", 0.0)
	_stones.append(stone)
	AudioManager.play_varied("throw_stone")


func _box(node: Control, pad: float = 0.0) -> Rect2:
	return Rect2(node.position, node.size).grow(pad)


func _tick_crows(delta: float) -> void:
	var min_x := 8.0
	var max_x: float = %Field.size.x - 56.0
	for crow in _crows:
		if not is_instance_valid(crow):
			continue
		var vx: float = float(crow.get_meta("vx"))
		crow.position.x += vx * delta
		if crow.position.x < min_x or crow.position.x > max_x:
			vx *= -1.0
			crow.position.x = clampf(crow.position.x, min_x, max_x)
			crow.set_meta("vx", vx)
		var phase: float = float(crow.get_meta("phase")) + delta * 4.0
		crow.set_meta("phase", phase)
		crow.position.y = float(crow.get_meta("home_y")) + sin(phase) * 10.0
	for stone in _stones.duplicate():
		if not is_instance_valid(stone):
			_stones.erase(stone)
			continue
		stone.position.x += float(stone.get_meta("vx")) * delta
		stone.position.y += float(stone.get_meta("vy")) * delta
		stone.set_meta("vy", float(stone.get_meta("vy")) + 700.0 * delta)
		var stone_box := _box(stone, 12.0)
		for crow in _crows.duplicate():
			if not is_instance_valid(crow):
				continue
			if stone_box.intersects(_box(crow, 14.0)):
				AudioManager.play_varied("stone_hit")
				crow.queue_free()
				_crows.erase(crow)
				stone.queue_free()
				_stones.erase(stone)
				break
		if is_instance_valid(stone) and stone.position.y < -30.0:
			stone.queue_free()
			_stones.erase(stone)
	if _crows.is_empty():
		_end(true)
	elif _shots_left <= 0 and _stones.is_empty():
		_end(false)


func _spawn_herd(count: int) -> void:
	var cx: float = %Field.size.x * 0.5
	var cy: float = %Field.size.y * 0.5
	_villager = _sprite(%Field, "res://Assets/Generated/Spritesheet/mini_villager.png", Vector2(cx - 18, cy - 28), Vector2(36, 56))
	_player = _sprite(%Field, "res://Assets/Generated/Spritesheet/mini_villager.png", Vector2(cx - 70, cy + 16), Vector2(32, 50))
	_mark_mother(_player)
	var spots: Array[Vector2] = [
		Vector2(16, cy - 24),
		Vector2(%Field.size.x - 96, cy - 10),
		Vector2(cx - 40, 12),
	]
	for i in count:
		var buf := _sprite(%Field, "res://Assets/Generated/Spritesheet/mini_buffalo.png", spots[i % spots.size()], Vector2(80, 48))
		var toward: Vector2 = (Vector2(cx, cy) - buf.position).normalized()
		buf.set_meta("vx", toward.x * 120.0)
		buf.set_meta("vy", toward.y * 120.0)
		buf.set_meta("turn", randf_range(0.4, 0.8))
		_buffaloes.append(buf)


func _tick_herd(delta: float) -> void:
	if _player == null or _villager == null:
		return
	var villager_box := _box(_villager, -4.0)
	var player_box := _box(_player, 4.0)
	var home: Vector2 = _villager.position
	for buf in _buffaloes:
		if not is_instance_valid(buf):
			continue
		var turn: float = float(buf.get_meta("turn")) - delta
		if turn <= 0.0:
			var jitter := Vector2(randf_range(-0.35, 0.35), randf_range(-0.35, 0.35))
			var toward: Vector2 = (home - buf.position).normalized() + jitter
			if toward == Vector2.ZERO:
				toward = Vector2.RIGHT
			toward = toward.normalized()
			var speed: float = randf_range(100.0, 140.0)
			buf.set_meta("vx", toward.x * speed)
			buf.set_meta("vy", toward.y * speed)
			buf.set_meta("turn", randf_range(0.35, 0.7))
		else:
			buf.set_meta("turn", turn)
		var vx: float = float(buf.get_meta("vx"))
		var vy: float = float(buf.get_meta("vy"))
		buf.position.x += vx * delta
		buf.position.y += vy * delta
		if buf.position.x < 4.0 or buf.position.x > %Field.size.x - 80.0:
			vx *= -1.0
			buf.position.x = clampf(buf.position.x, 4.0, %Field.size.x - 80.0)
		if buf.position.y < 4.0 or buf.position.y > %Field.size.y - 52.0:
			vy *= -1.0
			buf.position.y = clampf(buf.position.y, 4.0, %Field.size.y - 52.0)
		buf.set_meta("vx", vx)
		buf.set_meta("vy", vy)
		var buffalo_box := _box(buf, 2.0)
		if buffalo_box.intersects(player_box):
			var away: Vector2 = (buf.position - _player.position).normalized()
			if away == Vector2.ZERO:
				away = Vector2.RIGHT
			buf.set_meta("vx", away.x * 160.0)
			buf.set_meta("vy", away.y * 160.0)
			buf.position += away * 16.0
			AudioManager.play_varied("ui_click")
		elif buffalo_box.intersects(villager_box):
			_end(false)
			return


func _spawn_rice() -> void:
	_sprite(%Field, "res://Assets/Generated/Spritesheet/rice_mat.png", Vector2(%Field.size.x * 0.5 - 90, 170), Vector2(180, 56))
	_player = _sprite(%Field, "res://Assets/Generated/Spritesheet/mini_villager.png", Vector2(%Field.size.x * 0.5 - 16, 150), Vector2(32, 50))
	_mark_mother(_player)
	for i in 3:
		var ch: TextureRect = _sprite(%Field, "res://Assets/Generated/Spritesheet/mini_chicken.png", Vector2(30.0 + float(i) * 220.0, 40.0 + float(i) * 12.0), Vector2(40, 36))
		_chickens.append({"node": ch, "home": ch.position})


func _tick_rice(delta: float) -> void:
	if _player == null:
		return
	var mat := Rect2(Vector2(%Field.size.x * 0.5 - 70, 176), Vector2(140, 40))
	var player_box := Rect2(_player.position, _player.size)
	for item in _chickens:
		var ch: Control = item["node"]
		if not is_instance_valid(ch):
			continue
		var toward: Vector2 = (mat.get_center() - ch.position).normalized()
		ch.position += toward * 70.0 * delta
		if player_box.intersects(Rect2(ch.position, ch.size)):
			ch.position = item["home"]
			AudioManager.play_varied("ui_click")
		elif mat.intersects(Rect2(ch.position, ch.size).grow(-4)):
			_end(false)
			return


func _end(won: bool) -> void:
	if not _running:
		return
	_running = false
	%Result.text = Locale.t(Locale.mini_prefix(_game) + ("_win" if won else "_lose"))
	%Result.show()
	if won:
		GameManager.patience = minf(GameManager.max_patience, GameManager.patience + 20.0)
		GameManager.add_ammo(3)
		AudioManager.play("checkpoint_bell")
	else:
		GameManager.fail_minigame()
		AudioManager.play("ui_back")
	await get_tree().create_timer(1.3, true, false, true).timeout
	var tween := create_tween()
	tween.set_pause_mode(Tween.TWEEN_PAUSE_PROCESS)
	tween.tween_property(self, "modulate:a", 0.0, 0.2)
	await tween.finished
	hide()
	get_tree().paused = false
	finished.emit(won)
