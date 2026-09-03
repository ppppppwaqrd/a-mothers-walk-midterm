extends Node
## Central audio: pooled one-shot sound effects, crossfaded music, bus volumes.
##
## Every sound is one of the files under Assets/Generated/Sound, all synthesised
## by scripts/build_audio.py. Callers name a sound rather than reaching for a
## player node, so adding a sound means dropping in a file.

const SFX_DIR := "res://Assets/Generated/Sound/FX/"
const MUSIC_DIR := "res://Assets/Generated/Sound/Music/"

## Enough voices that a pickup, a jump and a hit can overlap without cutting
## each other off; past that the oldest voice is reused.
const VOICES := 8
const CROSSFADE := 1.2

## Which track plays in each level, and in the framing scenes.
const LEVEL_MUSIC := {
	"level_01": "day_walk",
	"level_02": "day_walk",
	"level_03": "noon_trail",
	"level_04": "noon_trail",
	"level_05": "night_canal",
	"level_06": "night_canal",
}
const MENU_MUSIC := "menu_theme"

var _voices: Array[AudioStreamPlayer] = []
var _next_voice := 0
var _music: Array[AudioStreamPlayer] = []
var _live := 0
var _playing := ""
var _cache: Dictionary = {}
var _fade: Tween


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for i in VOICES:
		var player := AudioStreamPlayer.new()
		player.bus = &"sfx"
		add_child(player)
		_voices.append(player)
	for i in 2:
		var player := AudioStreamPlayer.new()
		player.bus = &"music"
		player.volume_db = -80.0
		add_child(player)
		player.finished.connect(_on_music_finished.bind(player))
		_music.append(player)


## Fire a one-shot effect, e.g. play("jump"). Unknown names are ignored so a
## missing sound never takes gameplay down with it.
func play(sound: String, volume_db: float = 0.0, pitch: float = 1.0) -> void:
	var stream := _stream(SFX_DIR + sound + ".wav")
	if stream == null:
		return
	var player := _voices[_next_voice]
	_next_voice = (_next_voice + 1) % VOICES
	player.stream = stream
	player.volume_db = volume_db
	player.pitch_scale = pitch
	player.play()


## Slightly randomised pitch, for sounds that repeat constantly.
func play_varied(sound: String, volume_db: float = 0.0, spread: float = 0.08) -> void:
	play(sound, volume_db, randf_range(1.0 - spread, 1.0 + spread))


func play_music(track: String, volume_db: float = -8.0) -> void:
	if track == _playing:
		return
	var stream := _stream(MUSIC_DIR + track + ".ogg")
	if stream == null:
		return
	_playing = track
	var incoming: AudioStreamPlayer = _music[1 - _live]
	var outgoing: AudioStreamPlayer = _music[_live]
	_live = 1 - _live
	incoming.stream = stream
	incoming.volume_db = -80.0
	incoming.play()
	if _fade != null and _fade.is_valid():
		_fade.kill()
	_fade = create_tween().set_parallel(true)
	_fade.tween_property(incoming, "volume_db", volume_db, CROSSFADE)
	if outgoing.playing:
		_fade.tween_property(outgoing, "volume_db", -80.0, CROSSFADE)
		_fade.chain().tween_callback(outgoing.stop)


## Pick the track for a level id, or the menu theme when there is no level.
func play_music_for(level_id: String) -> void:
	play_music(LEVEL_MUSIC.get(level_id, MENU_MUSIC))


func stop_music() -> void:
	_playing = ""
	if _fade != null and _fade.is_valid():
		_fade.kill()
	for player in _music:
		player.stop()


## 0.0 silences the bus outright; anything above maps onto a normal fader curve.
func set_bus_volume(bus: StringName, linear: float) -> void:
	var index := AudioServer.get_bus_index(bus)
	if index < 0:
		return
	AudioServer.set_bus_mute(index, linear <= 0.001)
	AudioServer.set_bus_volume_db(index, linear_to_db(clampf(linear, 0.0001, 1.0)))


func _stream(path: String) -> AudioStream:
	if _cache.has(path):
		return _cache[path]
	var stream: AudioStream = null
	if ResourceLoader.exists(path):
		stream = load(path) as AudioStream
	else:
		push_warning("missing sound %s" % path)
	_cache[path] = stream
	return stream


## The OGG files are marked as looping on import, so this only fires if a track
## ever fails to loop; restarting keeps the level from going silent.
func _on_music_finished(player: AudioStreamPlayer) -> void:
	if player == _music[_live] and _playing != "":
		player.play()
