class_name Pickup
extends Area2D
## Shared behaviour for everything the player walks into and takes.
##
## Subclasses override `_collect(player)` to grant whatever they give, then the
## flourish is the same everywhere: the item lifts off the ground, swells, and
## fades. Taking something should always look like it was taken.

@export var amplitude := 5.0
@export var frequency := 3.5
## Degrees per second. Coins and stones turn; a water gourd hanging still does not.
@export var spin := 0.0

var _rest := Vector2.ZERO
var _time := 0.0
var _taken := false


func _ready() -> void:
	_rest = position
	# A row of items placed on the same line would otherwise bob in lockstep.
	_time = randf() * TAU


func _process(delta: float) -> void:
	if _taken:
		return
	_time += delta
	position.y = _rest.y + amplitude * sin(frequency * _time)
	if spin != 0.0:
		rotation_degrees += spin * delta


func _on_body_entered(body: Node2D) -> void:
	if _taken or not body.is_in_group("Player"):
		return
	if not _collect(body):
		return
	_taken = true
	set_deferred("monitoring", false)
	var tween := create_tween().set_parallel(true)
	tween.tween_property(self, "position", position + Vector2(0.0, -78.0), 0.4).set_ease(Tween.EASE_OUT)
	tween.tween_property(self, "scale", scale * 1.7, 0.4)
	tween.tween_property(self, "modulate:a", 0.0, 0.4).set_delay(0.1)
	await tween.finished
	queue_free()


## Grant the pickup. Return false to leave the item in the world, e.g. when the
## player is already at full health.
func _collect(_player: Node2D) -> bool:
	return true
