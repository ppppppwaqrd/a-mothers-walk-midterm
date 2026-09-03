extends Area2D

@export var next_scene: PackedScene
@export var teleport_marker: Marker2D


func _on_body_entered(body: Node2D) -> void:
	if not body.is_in_group("Player"):
		return
	if next_scene != null:
		AudioManager.play("level_complete")
		SceneTransition.load_scene(next_scene)
	elif teleport_marker != null:
		body.global_position = teleport_marker.global_position
