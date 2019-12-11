// vertex shader for the GridProgram

#version 150
// position vector of location model or direction line VBO 0
attribute vec3 position;
// normal vector of location model face VBO 0
attribute vec3 normal;
// offsets of the model (location & lines) VBO 1
attribute vec3 offset;

//projection matrix
uniform mat4 projection;
// view matrix
uniform mat4 view;
// world matrix
uniform mat4 world;
// color of the grid lines
uniform vec4 line_color;
// color of the locaiton model
uniform vec4 model_color;
// scaling of the world
uniform vec3 world_scaling;
// scaling of the model size
uniform vec3 model_scaling;
// scaling of the line length
uniform vec3 line_scaling;
// min value of brightness
uniform float ambient_light;
// direction of the parallel lightsource
uniform vec3 light_direction;
// color of the parallel lightsource
uniform vec4 light_color;
// flag if drawing the lines or the location model
uniform bool drawing_lines;


// varying color for fragment shader
varying vec4 v_color;
void main(void)
{
   if(drawing_lines){
      v_color = line_color;
      gl_Position = projection * view * world * vec4((position * line_scaling + offset) * world_scaling, 1.0);
   }else{
      vec3 nn = normalize(normal);
      vec3 diffuseReflection = vec3(light_color) * vec3(model_color)
                             * max(max(ambient_light, dot(nn, light_direction)), dot(-nn, light_direction));
      v_color = vec4(diffuseReflection, model_color[3]);

      mat4 use_world = world;
      use_world[3] += vec4(offset * world_scaling, 0);
      gl_Position = projection  * view * use_world * vec4(position * model_scaling, 1.0);
   }
}
