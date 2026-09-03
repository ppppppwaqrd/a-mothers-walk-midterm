shader_type canvas_item;
render_mode blend_mix, unshaded;

/// Fine paper grain over the whole page. Strength is kept low so it reads as
/// stock, not as noise on the HUD.
uniform float strength : hint_range(0.0, 0.2) = 0.055;
uniform vec4 tint : source_color = vec4(0.22, 0.15, 0.08, 1.0);

void fragment() {
	vec2 uv = SCREEN_UV * vec2(1280.0, 720.0);
	float n1 = fract(sin(dot(uv, vec2(12.9898, 78.233))) * 43758.5453);
	float n2 = fract(sin(dot(uv + 17.3, vec2(39.346, 11.135))) * 23421.631);
	float grain = mix(n1, n2, 0.45);
	COLOR = vec4(tint.rgb, grain * strength);
}
