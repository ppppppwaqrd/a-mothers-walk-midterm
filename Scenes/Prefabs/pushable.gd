extends CharacterBody2D
## A laterite rock or bamboo bundle the player can shove into a gap.

@export_enum("laterite", "bamboo") var kind: String = "laterite"
@export var push_speed := 90.0
@export var gravity := 1400.0

const TEX := {
	"laterite": "res://Assets/Generated/Spritesheet/push_laterite.png",
	"bamboo": "res://Assets/Generated/Spritesheet/push_bamboo.png",
}


func _ready() -> void:
	var path: String = str(TEX.get(kind, TEX["laterite"]))
	if ResourceLoader.exists(path):
		$Sprite2D.texture = load(path) as Texture2D


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += gravity * delta
	else:
		velocity.y = 0.0
	velocity.x = 0.0
	for body in $PushArea.get_overlapping_bodies():
		if not body.is_in_group("Player"):
			continue
		var away := signf(global_position.x - body.global_position.x)
		var walking := absf(body.velocity.x) > 20.0 and signf(body.velocity.x) == away
		var holding := (Input.is_action_pressed("Right") and away > 0.0) or (Input.is_action_pressed("Left") and away < 0.0)
		if walking or holding:
			velocity.x = away * push_speed
	move_and_slide()
