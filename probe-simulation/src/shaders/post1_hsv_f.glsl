#version 330

uniform float aberrationAmount;
uniform vec2 iResolution;// Add resolution uniform
uniform float iTime;// Add time uniform
out vec4 fragColor;

void main()
{
    fragColor=vec4(0);
}
