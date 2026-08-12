extends Node

@onready var jump_sfx = $JumpSfx
@onready var coin_pickup_sfx = $CoinPickup
@onready var death_sfx = $DeathSfx
@onready var respawn_sfx = $RespawnSfx
@onready var level_complete_sfx = $LevelCompleteSfx
@onready var throw_sfx = $ThrowSfx
@onready var pickup_kratib_sfx = $PickupKratibSfx


func play_throw() -> void:
	if throw_sfx and throw_sfx.stream:
		throw_sfx.play()


func play_pickup_kratib() -> void:
	if pickup_kratib_sfx and pickup_kratib_sfx.stream:
		pickup_kratib_sfx.play()
	else:
		coin_pickup_sfx.play()
