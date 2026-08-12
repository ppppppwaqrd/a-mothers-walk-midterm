extends Area2D

@export var amplitude := 4.0
@export var frequency := 4.0
@export var score_value := 1

var time_passed := 0.0
var initial_position := Vector2.ZERO


func _ready() -> void:
	initial_position = position


func _process(delta: float) -> void:
	time_passed += delta
	position.y = initial_position.y + amplitude * sin(frequency * time_passed)


func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("Player"):
		AudioManager.play_pickup_kratib()
		GameManager.add_score(score_value)
		var tween := create_tween()
		tween.tween_property(self, "position", Vector2(position.x, position.y - 80), 0.35)
		tween.parallel().tween_property(self, "scale", Vector2(1.6, 1.6), 0.35)
		await tween.finished
		queue_free()
